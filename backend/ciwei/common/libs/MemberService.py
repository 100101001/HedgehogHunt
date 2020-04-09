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
        app.logger.warn("推荐中")
        # 不能是同一个人发布的拾/失
        query = Good.query.filter(Good.member_id != goods_info.member_id)
        # 筛选物品类别
        query = query.filter(Good.category == goods_info.category)

        # 拓展搜索词
        search_words = MemberService.getSearchWords(goods_info.name)
        app.logger.warn("推荐中")
        common_rule = or_(*[Good.name.like(name) for name in search_words])
        if goods_info.owner_name != "无":
            rule = or_(Good.owner_name == goods_info.owner_name, common_rule)
            query = query.filter(rule)
        else:
            query = query.filter(common_rule)

        # 互相匹配（假设予认领的人没有恶意）
        release_type = goods_info.business_type
        goods_list = query.filter_by(business_type=1 - release_type, status=1).all()
        for good in goods_list:
            target_member_id = good.member_id if release_type == 1 else g.member_info.id  # 获得寻物启示贴主id
            lost_goods_id = good.id if release_type == 1 else goods_info.id
            found_goods_id = good.id if release_type == 0 else goods_info.id  # 获取失物招领id
            new_recommend = MemberService.addRecommendGoods(target_member_id=target_member_id,
                                                            found_goods_id=found_goods_id,
                                                            lost_goods_id=lost_goods_id,
                                                            edit=edit)
            if new_recommend and release_type == 1:
                # 是之前没推荐过的新物品给了寻物启示失主，才发通知
                # 通知：有人可能捡到了你遗失的东西
                SubscribeService.send_recommend_subscribe(goods_info=good)
        app.logger.warn("推荐结束")

    @staticmethod
    def addRecommendGoods(target_member_id=0, found_goods_id=0, lost_goods_id=0, edit=False):
        """
        增加新的记录，进行防重
        归还和通知会加进推荐
        :param edit:
        :param target_member_id:
        :param found_goods_id:
        :param lost_goods_id: 只是用于记录一下（在查看推荐记录时好看一下，匹配的动因）
        :return:
        """
        if not target_member_id or not found_goods_id:
            return False
        repeat_recommend = Recommend.query.filter_by(found_goods_id=found_goods_id,
                                                     target_member_id=target_member_id,
                                                     lost_goods_id=lost_goods_id).first()
        # 有但修改了
        if repeat_recommend and edit:
            repeat_recommend.status = 0
            db.session.add(repeat_recommend)
        # 没有
        model_recommend = Recommend()
        model_recommend.found_goods_id = found_goods_id
        model_recommend.target_member_id = target_member_id
        model_recommend.lost_goods_id = lost_goods_id
        db.session.add(model_recommend)
        db.session.commit()
        # 是新的推荐
        return repeat_recommend is None

    @staticmethod
    def setRecommendStatus(member_id=0, goods_id=0, new_status=1, old_status=0):
        # 假设第一点，一个用户不会发出大于一条的类似帖子，如果发了
        # 假设第二点，用户知道自己正在找的东西，还删除了推荐记录，所以会将所有相关的都置无效（无论因为哪一条推给了用户）
        Recommend.query.filter_by(found_goods_id=goods_id, target_member_id=member_id, status=old_status). \
            update({'status': new_status}, synchronize_session=False)

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
            return repeat_mark.status == 0
        pre_mark = Mark()
        pre_mark.goods_id = goods_id
        pre_mark.member_id = member_id
        db.session.add(pre_mark)
        return True

    @staticmethod
    def cancelPreMarkGoods(member_id=0, goods_id=0):
        """
        对预认领的帖子，取消预先认领
        :param member_id:
        :param goods_id:
        :return:
        """
        if not member_id or not goods_id:
            return
        all_mark_query = Mark.query.filter(Mark.goods_id == goods_id, Mark.status != 7)
        all_marks = all_mark_query.all()
        pre_mark = all_mark_query.filter_by(member_id=member_id).first()
        if pre_mark and pre_mark.status == 0:
            # 前端会控制只对予认领的显示取消认领，这里判断status==0只是以防万一
            pre_mark.status = 7
            db.session.add(pre_mark)
            # 表示最后一个预认领的人取消了，帖子状态需要变成待认领
            return len(all_marks) == 1
        # 这种情况基本不会发生（一个予认领贴一定会有有效的认领记录），只是以防万一
        return len(all_marks) == 0


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
        新的待处理Appeal
        :param member_id:
        :param goods_id:
        :return:
        """
        if not member_id or not goods_id:
            return False
        appeal = Appeal.query.filter_by(member_id=member_id, goods_id=goods_id).first()
        if appeal is None:
            appeal = Appeal()
            appeal.member_id = member_id
            appeal.goods_id = goods_id
        else:
            appeal.status = 0
        db.session.add(appeal)
