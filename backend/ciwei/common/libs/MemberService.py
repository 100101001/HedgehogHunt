#!/usr/bin/python3.6.8

# -*- coding:utf-8 -*-

import hashlib
import json
import random
import string

import itertools
import jieba
import requests
from flask import g
from sqlalchemy import or_

from application import app, db
from common.libs.Helper import getCurrentDate
from common.models.ciwei.Appeal import Appeal
from common.models.ciwei.Goods import Good
from common.models.ciwei.Mark import Mark
from common.models.ciwei.Member import Member
from common.models.ciwei.MemberBalanceChangeLog import MemberBalanceChangeLog
from common.models.ciwei.Recommend import Recommend


class MemberService:

    @staticmethod
    def geneAuthCode(member_info=None):
        m = hashlib.md5()
        str = "%s-%s" % (member_info.id, member_info.salt)
        m.update(str.encode('utf-8'))
        return m.hexdigest

    # 生成秘钥
    @staticmethod
    def geneSalt(length=16):
        keylist = [random.choice((string.ascii_letters + string.digits)) for _ in range(length)]
        return "".join(keylist)

    @staticmethod
    def getWeChatOpenId(code, get_session_key=False):
        appid = app.config['OPENCS_APP']['appid']
        appkey = app.config['OPENCS_APP']['appkey']
        url = 'https://api.weixin.qq.com/sns/jscode2session?appid={0}&secret={1}&' \
              'js_code={2}&grant_type=authorization_code'.format(appid, appkey, code)

        r = requests.get(url, headers={'Connection': 'close'})
        res = json.loads(r.text)

        openid = None
        session_key = None
        if 'openid' in res:
            openid = res['openid']
        if 'session_key' in res:
            session_key = res['session_key']

        if get_session_key:
            return openid, session_key
        else:
            return openid

    @staticmethod
    def updateCredits(member_info):
        # 发布成功，用户积分涨5
        member_info.credits += 5
        member_info.updated_time = getCurrentDate()
        db.session.add(member_info)
        db.session.commit()
        return True

    @staticmethod
    def blockMember(select_member_id):
        # 发布成功，用户积分涨5
        # 违规用户状态设置为0.则无法再正常使用
        select_member_info = Member.query.filter_by(id=select_member_id).first()
        select_member_info.status = 0

        # 该用户下正常的账户
        goods_list = Good.query.filter(Good.member_id == select_member_id, Good.status == 1).all()
        for item in goods_list:
            item.status = 8
            item.updated_time = getCurrentDate()
            db.session.add(item)
            db.session.commit()

        select_member_info.updated_time = getCurrentDate()
        db.session.add(select_member_info)
        db.session.commit()
        return True

    @staticmethod
    def restoreMember(select_member_id):
        # 违规用户状态设置为0.则无法再正常使用
        select_member_info = Member.query.filter_by(id=select_member_id).first()
        select_member_info.status = 1

        # 该用户下正常的账户
        goods_list = Good.query.filter(Good.member_id == select_member_id, Good.status == 8).all()
        for item in goods_list:
            item.status = 1
            item.updated_time = getCurrentDate()
            db.session.add(item)
            db.session.commit()

        select_member_info.updated_time = getCurrentDate()
        db.session.add(select_member_info)
        db.session.commit()

        return True

    @staticmethod
    def autoRecommendGoods(goods_info=None, edit=False):
        """
        自动匹配推荐
        :param edit:
        :param goods_info:
        """
        from common.libs import SubscribeService

        # 不能是同一个人发布的拾/失,物品有效
        query = Good.query.filter(Good.status != 7, Good.status != 5)
        query = query.filter(Good.member_id != goods_info.member_id)
        # 筛选物品类别
        query = query.filter(Good.category == goods_info.category)

        # 拓展搜索词
        search_words = MemberService.getSearchWords(goods_info.name)
        common_rule = or_(*[Good.name.like(name) for name in search_words])
        if goods_info.owner_name != "无":
            rule = or_(Good.owner_name == goods_info.owner_name, common_rule)
            query = query.filter(rule)
        else:
            query = query.filter(common_rule)

        # 互相匹配
        release_type = goods_info.business_type
        goods_list = query.filter_by(business_type=1 - release_type).all()
        for good in goods_list:
            member_id = good.member_id if release_type == 1 else g.member_info.id  # 获得寻物启示贴主id
            new_recommend = MemberService.addRecommendGoods(member_id=member_id,
                                                            goods_id=good.id, edit=edit)
            if new_recommend and release_type == 1:
                # 通知：有人可能捡到了你遗失的东西
                SubscribeService.send_recommend_subscribe(goods_info=good)

    @staticmethod
    def addRecommendGoods(member_id=0, goods_id=0, edit=False):
        """
        增加新的记录，进行防重
        归还和通知会加进推荐
        :param edit:
        :param member_id:
        :param goods_id:
        :return:
        """
        if not member_id or not goods_id:
            return False
        repeat_recommend = Recommend.query.filter_by(goods_id=goods_id, member_id=member_id).first()
        if repeat_recommend:
            if edit:
                # 已阅推荐记录，但因为物品被编辑了就更新为未读
                # 进来前未阅记录被置为物品已删，所以需要重新置为未读
                repeat_recommend.status = 0
                db.session.add(repeat_recommend)
                db.session.commit()
            return False
        model_recommend = Recommend()
        model_recommend.goods_id = goods_id
        model_recommend.member_id = member_id
        db.session.add(model_recommend)
        db.session.commit()
        return True

    @staticmethod
    def filterRecommends(recommend_list=None, only_new=True):
        """
        对于只看新增的就过滤已经删除的物品
        如果推荐的物品，已经被删除，将推荐的状态置为 -1
        :param only_new: 只要新的有效的推荐记录
        :param recommend_list: 推荐记录列表
        :return:
        """
        if recommend_list is None:
            # 默认赋值[]是可变的，不允许
            recommend_list = []
        recommend_dict = {}
        for recommend in recommend_list:
            good_id = recommend.goods_id
            good = Good.query.filter_by(id=good_id).first()
            if good is None or good.status in [7, 8]:
                # 推荐的物品已被删除
                recommend.status = -1
                db.session.add(recommend)
                db.session.commit()
                if only_new:
                    # 只要最新的，不要看被删除的
                    continue
            recommend_dict[good_id] = recommend.status
        return recommend_dict

    @staticmethod
    def setRecommendStatus(member_id=0, goods_id=0, status=1):
        recommend = Recommend.query.filter_by(goods_id=goods_id, member_id=member_id).first()
        if recommend and recommend.status != status:
            recommend.status = status
            db.session.add(recommend)

    @staticmethod
    def setMemberBalanceChange(member_info=None, unit=0, note="答谢"):
        """
        记录会员账户余额变化
        :param member_info:
        :param unit:
        :param note:
        :return:
        """
        balance_change_model = MemberBalanceChangeLog()
        balance_change_model.member_id = member_info.id
        balance_change_model.openid = member_info.openid
        balance_change_model.unit = unit
        balance_change_model.total_balance = member_info.balance
        balance_change_model.note = note
        balance_change_model.created_time = getCurrentDate()
        db.session.add(balance_change_model)

    @staticmethod
    def getSearchWords(name):
        search_words = list(jieba.cut_for_search(name))
        tag = search_words[-1]
        more = [tag.replace(item, '') for item in search_words[:-1]]
        more.extend([tag, name] if tag != name else [tag])
        search_words = []
        for k, _ in itertools.groupby(more):
            if k:
                search_words.append('%' + k + '%')
        # keyword = synonyms.seg(goods_info.name)[0][-1]
        # # 获取近义词
        # synonyms_good_names = synonyms.nearby(keyword)[0][:2]
        # synonyms_good_names.extend([keyword])
        # synonyms_good_names = ['%'+name+'%' for name in synonyms_good_names]
        # 一定非空
        # 寻物启示可精准，失物招领宜宽泛。
        # 寻物启示三思后发
        return search_words

    @staticmethod
    def preMarkGoods(member_id=0, goods_id=0):
        """
        预认领
        :param member_id:
        :param goods_id:
        :return:
        """
        if not member_id or not goods_id:
            return
        repeat_mark = Mark.query.filter_by(member_id=member_id, goods_id=goods_id).first()
        if repeat_mark:
            if repeat_mark.status == 7:
                # 将被删除的记录状态初始化
                repeat_mark.status = 0
                db.session.add(repeat_mark)
            return
        pre_mark = Mark()
        pre_mark.goods_id = goods_id
        pre_mark.member_id = member_id
        db.session.add(pre_mark)

    @staticmethod
    def markGoods(member_id=0, goods_id=0):
        """
        认领
        :param member_id:
        :param goods_id:
        :return: 认领失败/成功
        """
        if not member_id or not goods_id:
            return False
        pre_mark = Mark.query.filter_by(member_id=member_id, goods_id=goods_id).first()
        if not pre_mark or pre_mark.status != 0:
            # 不符合认领的条件
            return False
        pre_mark.status = 1
        db.session.add(pre_mark)
        return True

    @staticmethod
    def hasMarkGoods(member_id=0, goods_id=0):
        """
        是否预认领/认领了该物品(详情可否见放置地址)
        :param member_id:
        :param goods_id:
        :return:
        """
        if not member_id or not goods_id:
            return False
        mark = Mark.query.filter(Mark.member_id == member_id,
                                 Mark.goods_id == goods_id,
                                 Mark.status != 7).first()
        return mark is not None

    @staticmethod
    def appealGoods(member_id=0, goods_id=0):
        """
        创建申诉(认为已被他人取走的物品是自己的)
        :param member_id:
        :param goods_id:
        :return:
        """
        if not member_id or not goods_id:
            return
        repeat_appeal = Appeal.query.filter_by(member_id=member_id, goods_id=goods_id).first()
        if repeat_appeal:
            if repeat_appeal.status == 7:
                # 将被删除的记录状态初始化
                repeat_appeal.status = 0
                db.session.add(repeat_appeal)
            return
        appeal = Appeal()
        appeal.member_id = member_id
        appeal.goods_id = goods_id
        db.session.add(appeal)
