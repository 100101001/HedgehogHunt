# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/3/10 下午11:03
@file: MemberService.py
@desc:
"""
import datetime
import json

import requests

from application import app, db
from common.cahce import CacheOpService, CacheQueryService, CacheOpUtil
from common.libs import LogService
from common.libs.recommend.v2 import SyncService
from common.models.ciwei.Appeal import Appeal
from common.models.ciwei.Goods import Good
from common.models.ciwei.Mark import Mark
from common.models.ciwei.Member import Member
from common.models.ciwei.MemberSmsPkg import MemberSmsPkg
from common.models.ciwei.Recommend import Recommend
from common.models.ciwei.User import User


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
            member_info = Member.query.filter_by(openid=openid).first()
            if member_info:
                CacheOpService.setMemberCache(member_info=member_info)
                user_info = User.query.filter_by(member_id=member_info.id).first()
                CacheOpService.setUsersCache(users=[user_info])
        return member_info, user_info

    @staticmethod
    def updateCredits(member_info=None, member_id=0, quantity=5):
        """
        更新会员积分
        :param member_id:
        :param quantity: 变更积分数，默认 5
        :param member_info:
        :return:
        """
        if not member_info and not member_id or not quantity:
            return
        # 发布成功，用户积分涨5
        if member_info:
            updated = {'credits': member_info.credits + quantity}
            Member.query.filter_by(id=member_info.id).update(updated, synchronize_session=False)
            CacheOpUtil.updateModelDict(model=member_info, updated=updated)
            CacheOpService.setMemberCache(member_info=member_info)
        else:
            member_info = Member.query.filter_by(id=member_id).first()
            if member_info:
                member_info.credits += quantity
                CacheOpService.setMemberCache(member_info=member_info)
                db.session.add(member_info)

    @staticmethod
    def updateName(member_info=None, member_id=0, name=""):
        """
        更新会员的姓名
        :param member_id:
        :param member_info:
        :param name:
        :return:
        """
        if not member_info and not member_id or not name:
            return
        if member_info:
            updated = {'name': name}
            Member.query.filter_by(id=member_info.id).update(updated, synchronize_session=False)
            CacheOpUtil.updateModelDict(model=member_info, updated=updated)
            CacheOpService.setMemberCache(member_info=member_info)
        else:
            member_info = Member.query.filter_by(id=member_id).first()
            if member_info:
                member_info.name = name
                CacheOpService.setMemberCache(member_info=member_info)
                db.session.add(member_info)

    @staticmethod
    def updateSmsNotify(member_info=None, member_id=0, sms_times=0):
        """
        更新剩余通知次数，缓存写入
        :param member_id:
        :param member_info:
        :param sms_times:
        :return:
        """
        if not sms_times or not member_info and not member_id:
            return
        if member_info:
            LogService.setMemberNotifyTimesChange(member_info=member_info, unit=sms_times,
                                                  old_times=member_info.left_notify_times, note="短信充值")
            updated = {'left_notify_times': member_info.left_notify_times + sms_times}
            Member.query.filter_by(id=member_info.id).update(updated, synchronize_session=False)
            CacheOpUtil.updateModelDict(model=member_info, updated=updated)
            CacheOpService.setMemberCache(member_info=member_info)
        else:
            member_info = Member.query.filter_by(id=member_id).first()

            if member_info:
                LogService.setMemberNotifyTimesChange(member_info=member_info, unit=sms_times,
                                                      old_times=member_info.left_notify_times, note="短信充值")
                member_info.left_notify_times += sms_times
                CacheOpService.setMemberCache(member_info=member_info)
                db.session.add(member_info)

    @staticmethod
    def updateBalance(member_info=None, member_id=0, unit=0, note=''):
        """
        余额在购物，(被)答谢，通知，充值等情况下更新
        :param member_id:
        :param member_info:
        :param unit:
        :param note:
        :return:
        """
        if not member_info and not member_id or not unit:
            return

        if not member_info:
            member_info = Member.query.filter_by(id=member_id).first()
            if member_info:
                LogService.setMemberBalanceChange(member_info=member_info, unit=unit, old_balance=member_info.balance,
                                                  note=note)
                member_info.balance += unit
                CacheOpService.setMemberCache(member_info=member_info)
                db.session.add(member_info)
        else:
            LogService.setMemberBalanceChange(member_info=member_info, unit=unit, old_balance=member_info.balance,
                                              note=note)
            updated = {'balance': member_info.balance + unit}
            Member.query.filter_by(id=member_info.id).update(updated, synchronize_session=False)
            CacheOpUtil.updateModelDict(model=member_info, updated=updated)
            CacheOpService.setMemberCache(member_info=member_info)

    @staticmethod
    def addSmsPkg(openid=''):
        pkg = MemberSmsPkg()
        pkg.open_id = openid
        pkg.left_notify_times = 50
        pkg.expired_time = datetime.datetime.now() + datetime.timedelta(weeks=156)
        db.session.add(pkg)

    @staticmethod
    def blockMember(member_id=0, user_id=0, goods_id=0, block_status=0, block_reason=""):
        """
        :param goods_id:
        :param block_reason:
        :param block_status: -1恶意举报, 0恶意发帖
        :param user_id:
        :param member_id:
        :return:
        """
        if not member_id or not user_id:
            return
        # 会员状态标记
        member_info = Member.query.filter_by(id=member_id).first()
        LogService.setMemberStatusChange(member_info=member_info, old_status=member_info.status,
                                         new_status=block_status, note=block_reason, user_id=user_id, goods_id=goods_id)
        member_info.status = block_status
        member_info.user_id = user_id
        CacheOpService.setMemberCache(member_info=member_info)
        db.session.commit()
        # 物品举报状态标记
        # 取出来id再更新是为了ES同步
        goods_ids = Good.query.filter(Good.member_id == member_id, Good.report_status == 0).with_entities(Good.id).all()
        if goods_ids:
            updated = {'report_status': 6, 'user_id': user_id}
            Good.query.filter(Good.id.in_(goods_ids)).update(updated, synchronize_session=False)
            db.session.commit()
            SyncService.syncUpdatedGoodsToESBulk(goods_ids=goods_ids, updated=updated)

    @staticmethod
    def restoreMember(member_id=0, user_id=0):
        """

        :param user_id:
        :param member_id:
        :return:
        """
        # 违规用户状态设置为0.则无法再正常使用
        if not member_id or not user_id:
            return
            # 会员状态标记
        member_info = Member.query.filter_by(id=member_id).first()
        LogService.setMemberStatusChange(member_info=member_info, old_status=member_info.status,
                                         new_status=1, note="账号解封", user_id=user_id)
        member_info.status = 1
        member_info.user_id = user_id
        CacheOpService.setMemberCache(member_info=member_info)
        db.session.commit()
        # 物品举报状态标记
        # 取出来id再更新是为了ES同步
        goods_ids = Good.query.filter(Good.member_id == member_id, Good.report_status == 6).with_entities(Good.id).all()
        if goods_ids:
            updated = {'report_status': 0, 'user_id': user_id}
            Good.query.filter(Good.id.in_(goods_ids)).update(updated, synchronize_session=False)
            db.session.commit()
            SyncService.syncUpdatedGoodsToESBulk(goods_ids=goods_ids, updated=updated)
        return True

    @staticmethod
    def appealStatusChangeRecord(log_id=0, reason=''):
        LogService.appealMemberStatusChangeLog(log_id=log_id, reason=reason)

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
        repeat_mark = Mark.query.filter_by(member_id=member_id, goods_id=goods_id).first()
        if repeat_mark:
            if repeat_mark.status == 7:
                # 将被删除的记录状态初始化
                repeat_mark.status = 0
                db.session.add(repeat_mark)
            return repeat_mark.status == 0
        pre_mark = Mark()
        pre_mark.business_type = business_type
        pre_mark.goods_id = goods_id
        pre_mark.member_id = member_id
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
        # 缓存中获取goods_id 对应的 member_id 集合
        mark_member_ids = CacheQueryService.getMarkCache(goods_id=goods_id)
        if not mark_member_ids:
            # 缓存不命中, 从数据库获取一个物品的所有认领人的id
            marks = Mark.query.filter(Mark.goods_id == goods_id,
                                      Mark.status != 7).all()
            mark_member_ids = CacheOpService.setMarkCache(goods_id=goods_id, marks=marks)
        return bool(str(member_id) in mark_member_ids)

    @staticmethod
    def cancelPremark(found_ids=None, member_id=0):
        """
        :param found_ids:
        :param member_id:
        :return: 外面修改Goods状态还要用的mark_key
        """
        Mark.query.filter(Mark.member_id == member_id,
                          Mark.goods_id.in_(found_ids),
                          Mark.status == 0).update({'status': 7}, synchronize_session=False)

    @staticmethod
    def markedGoods(member_id=0, goods_ids=None):
        """
        确认取回物品
        :param member_id:
        :param goods_ids:
        :return:
        """
        Mark.query.filter(Mark.member_id == member_id,
                          Mark.goods_id.in_(goods_ids),
                          Mark.status == 0).update({'status': 1}, synchronize_session=False)

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
