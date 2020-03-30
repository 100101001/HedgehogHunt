#!/usr/bin/python3.6.8

# -*- coding:utf-8 -*-


import hashlib
import random
import string

import json
import requests
from flask import g

from application import app, db
from common.libs.Helper import getCurrentDate
from common.libs.Helper import selectFilterObj, getDictFilterField
from common.models.ciwei.Goods import Good
from common.models.ciwei.Member import Member
from common.models.ciwei.MemberBalanceChangeLog import MemberBalanceChangeLog


class MemberService():

    @staticmethod
    def geneAuthCode(member_info=None):
        m = hashlib.md5()
        str = "%s-%s" % (member_info.id, member_info.salt)
        m.update(str.encode('utf-8'))
        return m.hexdigest

    # 生成秘钥
    @staticmethod
    def geneSalt(length=16):
        keylist = [random.choice((string.ascii_letters + string.digits)) for i in range(length)]
        return ("".join(keylist))

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
    def recommendGoods(goods_info):
        """
        当有新的发布时，在系统中进行查询对立面，即发布失物招领时查询寻物启示，
        发布寻物启事时查询失物招领，如果姓名相同，则给用户推荐信息
        当用户被直接扫码时也推荐
        在end-creat完成之后进行推荐
        寻物启事发布时是给发布者推荐，失物招领时是给寻物启事的发布者推荐
       :param goods_info:
       :return: True
       """
        from common.libs import SubscribeService
        # 按物主owner_name, 物品名name 匹配失/拾物品
        # 在失去物品的作者的recommmend_id中加入匹配到的拾物品id
        # 不能是同一个人发布的拾/失
        query = Good.query.filter(Good.status != 7, Good.status != 5, Good.status != 8)
        query = query.filter_by(owner_name=goods_info.owner_name)
        query = query.filter_by(name=goods_info.name)
        query = query.filter(Good.member_id != goods_info.member_id)
        if goods_info.business_type == 1:
            # 发布的是失物招领，找到了对应的寻物启事
            goods_list = query.filter_by(business_type=0).all()
            if goods_list:
                # 获取用户的信息
                member_ids = selectFilterObj(goods_list, "member_id")
                member_map = getDictFilterField(Member, Member.id, "id", member_ids)
                for item in goods_list:
                    if item.member_id not in member_map:
                        item.status = 7
                        db.session.add(item)
                        db.session.commit()
                        continue
                    tmp_member_info = member_map[item.member_id]
                    if tmp_member_info:
                        MemberService.addRecommendGoods(tmp_member_info, item.id)
                        # 通知：有人可能捡到了你遗失的东西
                        SubscribeService.send_recommend_subscribe(item)
        else:
            # 发布的是寻物启事，找到了对应的失物招领,给用户返回失物招领的列表
            goods_list = query.filter_by(business_type=1).all()
            if goods_list:
                member_info = g.member_info
                for item in goods_list:
                    MemberService.addRecommendGoods(member_info, item.id)
                    # # 通知：有人可能丢了你捡到的东西
                    # SubscribeService.send_recommend_subscribe(item)
        return True

    @staticmethod
    def addRecommendGoods(member_info, goods_id):
        """
        在会员的
        :param member_info:
        :param goods_id:
        :return:
        """
        if member_info.recommend_id:
            recommend_id_dict = MemberService.getRecommendDict(member_info.recommend_id, False)
            recommend_id_list = recommend_id_dict.keys()
            # 考虑到信息编辑更新时如果之前已经推荐过就不再推荐了
            if str(goods_id) not in recommend_id_list:
                member_info.recommend_id = member_info.recommend_id + '#' + str(goods_id) + ':0'
        else:
            member_info.recommend_id = str(goods_id) + ':0'
        db.session.add(member_info)
        db.session.commit()

    @staticmethod
    def getRecommendDict(recommend_id, only_new):
        re_list = recommend_id.split('#')
        re_dict = {}
        for i in re_list:
            goods_id = int(i.split(':')[0])
            status = int(i.split(':')[1])
            good = Good.query.filter_by(id=goods_id).first()
            if good is None or good.status == 7 or good.status == 8:  # 已被删除或封锁
                continue
            if only_new:
                if status == 0:
                    re_dict[goods_id] = status
            else:
                re_dict[goods_id] = status

        return re_dict

    @staticmethod
    def joinRecommendDict(re_dict):
        keys = list(re_dict.keys())
        if len(re_dict) == 0:
            return ''
        recommend_id = str(keys[0]) + ':' + str(re_dict[keys[0]])
        for key in keys[1:]:
            recommend_id = recommend_id + '#' + str(key) + ':' + str(re_dict[key])
        return recommend_id

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
