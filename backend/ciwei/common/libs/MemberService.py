# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/3/10 下午11:03
@file: MemberService.py
@desc:
"""
import json

import requests

from application import app, db
from common.cahce.core import CacheQueryService, CacheOpService
from common.models.ciwei.Mark import Mark
from common.models.ciwei.Member import Member
from common.models.ciwei.MemberSmsPkg import MemberSmsPkg
from common.models.ciwei.Recommend import Recommend
from common.models.ciwei.admin.User import User


class MemberHandler:
    pass


class MemberService:

    @staticmethod
    def getWeChatOpenId(code, get_session_key=False):
        """
        通过code在微信登录获取openid, session_key
        :param code:
        :param get_session_key:
        :return:
        """
        openid = None
        session_key = None
        if code:
            app_id = app.config['OPENCS_APP']['appid']
            app_key = app.config['OPENCS_APP']['appkey']
            url = 'https://api.weixin.qq.com/sns/jscode2session?appid={0}&secret={1}&' \
                  'js_code={2}&grant_type=authorization_code'.format(app_id, app_key, code)

            r = requests.get(url, headers={'Connection': 'close'})
            res = json.loads(r.text)
            if 'openid' in res:
                openid = res['openid']
            if 'session_key' in res:
                session_key = res['session_key']

        if get_session_key:
            return openid, session_key
        else:
            return openid

    @staticmethod
    def isReg(openid=''):
        """
        微信用户是否已经注册
        :param openid:
        :return:
        """
        member_info = None
        if openid:
            member_info = Member.query.filter_by(openid=openid).first()
        return member_info is not None

    @staticmethod
    def doLogin(openid=''):
        """
        登录
        :param openid:
        :return: 会员和管理员信息
        """
        member_info = None
        user_info = None
        if openid:
            member_info = Member.getByOpenId(openid=openid)
            if member_info:
                CacheOpService.setMemberCache(member_info=member_info)
                user_info = User.query.filter_by(member_id=member_info.id).first()
                CacheOpService.setUsersCache(users=[user_info])
        return member_info, user_info

    @staticmethod
    def doRegister(nickname='', sex=1, avatar='', openid='', mobile=''):
        new_member = Member(nickname=nickname, sex=sex, avatar=avatar, openid=openid, mobile=mobile)
        db.session.add(new_member)
        return new_member

    @staticmethod
    def updateCredits(member_id=0, quantity=5):
        """
        更新会员积分
        :param member_id:
        :param quantity: 变更积分数，默认 5
        :return:
        """
        if not member_id or not quantity:
            return
        # 发布成功，用户积分涨5
        member_info = Member.getById(member_id)
        if member_info:
            member_info.credits += quantity
            db.session.add(member_info)

    @staticmethod
    def updateName(member_id=0, name=""):
        """
        更新会员的姓名
        :param member_id:
        :param name:
        :return:
        """
        if not member_id or not name:
            return

        member_info = Member.getById(member_id)
        if member_info:
            member_info.name = name
            db.session.add(member_info)

    @staticmethod
    def updateSmsNotify(member_id=0, sms_times=0):
        """
        更新剩余通知次数，缓存写入
        :param member_id:
        :param sms_times:
        :return:
        """
        if not sms_times or not member_id:
            return
        member_info = Member.getById(member_id)
        if member_info:
            member_info.left_notify_times += sms_times
            db.session.add(member_info)

    @staticmethod
    def updateBalance(member_id=0, unit=0):
        """
        余额在购物，(被)答谢，通知，充值等情况下更新
        :param member_id:
        :param unit:
        :return:
        """
        if not member_id or not unit:
            return
        member_info = Member.getById(member_id)
        if member_info:
            member_info.balance += unit
            db.session.add(member_info)

    @staticmethod
    def addSmsPkg(member_info=None):
        pkg = MemberSmsPkg(openid=member_info.openid,
                           member_id=member_info.id)
        db.session.add(pkg)

    @staticmethod
    def setRecommendStatus(member_id=0, goods_id=0, new_status=1, old_status=0):
        """
        从详情进入，推荐记录算已阅
        :param member_id:
        :param goods_id:
        :param new_status:
        :param old_status:
        :return:
        """
        # 假设第一点，一个用户不会发出大于一条的类似帖子，如果发了
        # 假设第二点，用户知道自己正在找的东西，还删除了推荐记录，所以会将所有相关的都置无效（无论因为哪一条推给了用户）
        Recommend.query.filter_by(found_goods_id=goods_id, target_member_id=member_id, status=old_status). \
            update({'status': new_status}, synchronize_session=False)

    @staticmethod
    def preMarkGoods(member_id=0, goods_id=0, business_type=1):
        """
        预认领
        :param business_type:
        :param member_id:
        :param goods_id:
        :return:
        """
        if not member_id or not goods_id:
            return False
        return Mark.pre(member_id=member_id, goods_id=goods_id, business_type=business_type)

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
        # 缓存中获取goods_id 对应的 member_id 集合
        mark_member_ids = CacheQueryService.getMarkCache(goods_id=goods_id)
        if not mark_member_ids:
            # 缓存不命中, 从数据库获取一个物品的所有认领人的id
            marks = Mark.getAllOn(goods_id=goods_id)
            mark_member_ids = CacheOpService.setMarkCache(goods_id=goods_id, marks=marks)
        return bool(str(member_id) in mark_member_ids)

    @staticmethod
    def cancelPremark(found_ids=None, member_id=0):
        """
        :param found_ids:
        :param member_id:
        :return: 外面修改Goods状态还要用的mark_key
        """
        Mark.mistaken(goods_ids=found_ids, member_id=member_id)

    @staticmethod
    def markedGoods(member_id=0, goods_ids=None):
        """
        确认取回物品
        :param member_id:
        :param goods_ids:
        :return:
        """
        Mark.done(goods_ids=goods_ids, member_id=member_id)
