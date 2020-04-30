# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/4/30 下午12:45
@file: AppealService.py
@desc: 
"""
from sqlalchemy.orm import aliased

from application import db
from common.admin import UserService
from common.admin.decorators import user_op
from common.cahce.GoodsCasUtil import GoodsCasUtil
from common.libs import LogService
from common.models.ciwei.Appeal import Appeal
from common.models.ciwei.Goods import Good
from common.models.ciwei.Member import Member
from common.models.ciwei.Thanks import Thank
from common.models.ciwei.logs.change.MemberStatusChangeLog import MemberStatusChangeLog
from common.search.decorators import db_search


class BlockAppealHandler:
    __strategy_map = {
        'init': '_createBlockAppeal',
        'search': '_getBlockAppeals',
        'accept': '_acceptBlockAppeal',
        'reject': '_turnDownBlockAppeal',
        'restore': '_restoreMember'
    }

    @classmethod
    def deal(cls, op, **kwargs):
        strategy = cls.__strategy_map.get(op)
        handler = getattr(cls, strategy, None)
        if handler:
            return handler(**kwargs)

    @staticmethod
    def _createBlockAppeal(log_id=0, reason='', **kwargs):
        """
        用户给出申诉理由
        :param log_id:
        :param reason:
        :return:
        """
        MemberStatusChangeLog.query.filter_by(id=log_id).update({'member_reason': reason, 'status': 1},
                                                                synchronize_session=False)

    @staticmethod
    @db_search()
    def _getBlockAppeals(member_id=0, stuff_type=0, **kwargs):
        """
        获取所有举报拉黑后用户的申诉记录
        :param member_id:
        :param stuff_type:
        :return:
        """
        stuffs = [Thank, Good]
        stuff = stuffs[stuff_type]
        query = MemberStatusChangeLog.query.join(stuff, stuff.id == MemberStatusChangeLog.stuff_id). \
            filter(MemberStatusChangeLog.member_id == member_id,
                   MemberStatusChangeLog.stuff_type == stuff_type).add_entity(stuff)
        return query

    @staticmethod
    @user_op
    def _acceptBlockAppeal(log_id=0, user=None, **kwargs):
        """
        管理员同意申诉，比较管理员级别
        :param user:
        :param log_id:
        :return:
        """
        log = MemberStatusChangeLog.query.filter_by(id=log_id).first()
        origin_user_id = log.user_id
        origin_user = UserService.getUserByUid(user_id=origin_user_id)
        if user.level > origin_user.level:
            return False, '您的级别过低，无权限进行此操作'
        MemberStatusChangeLog.query.filter_by(id=log_id).update({'status': 2, 'user_id': user.uid},
                                                                synchronize_session=False)
        return True, '操作成功'

    @staticmethod
    @user_op
    def _turnDownBlockAppeal(log_id=0, **kwargs):
        """
        管理员拒绝申诉
        :param log_id:
        :return:
        """
        MemberStatusChangeLog.query.filter_by(id=log_id).update({'status': 3},
                                                                synchronize_session=False)

    @staticmethod
    @user_op
    def _restoreMember(restore_member_id=0, user=None, **kwargs):
        """
        账号解封
        :param user:
        :param restore_member_id:
        :return:
        """
        # 违规用户状态设置为0.则无法再正常使用
        if not restore_member_id or not user:
            return
            # 会员状态标记
        user_id = user.uid
        member_info = Member.query.filter_by(id=restore_member_id).first()
        LogService.setMemberStatusChange(member_info=member_info, old_status=member_info.status,
                                         new_status=1, note="账号解封", user_id=user_id)
        member_info.status = 1
        member_info.user_id = user_id
        db.session.commit()
        # 物品举报状态标记
        updated = {'report_status': 0, 'user_id': user_id}
        Good.query.filter(Good.member_id == restore_member_id, Good.report_status == 6).update(updated)
        Thank.query.filter(Thank.member_id == restore_member_id, Thank.report_status == 6).update(updated,
                                                                                                  synchronize_session=False)
        db.session.commit()


class GoodsAppealHandler:
    __strategy_map = {
        'init': '_createGoodsAppeal',
        'search': '_getAppealedGoods',
        'dealt': '_setGoodsAppealDealt',
        'delete': '_userDelGoodsAppeal'
    }

    @classmethod
    def deal(cls, op, **kwargs):
        strategy = cls.__strategy_map.get(op)
        handler = getattr(cls, strategy, None)
        if handler:
            return handler(**kwargs)

    @staticmethod
    def _createGoodsAppeal(member_id=0, goods_id=0, status=-1, **kwargs):
        """
        新的待处理Appeal
        :param member_id:
        :param goods_id:
        :return:
        """
        if not member_id or not goods_id:
            return False, '操作失败'
        if not GoodsCasUtil.exec(goods_id, status, 5):
            return False, '操作冲突'

        # 公开信息的状态操作加锁
        goods_info = Good.query.filter_by(id=goods_id, status=status).first()
        if goods_info is None:
            return False, '申诉失败，请刷新后重试'
        Appeal.create(goods_id=goods_id, member_id=member_id)
        return True, ''

    @staticmethod
    @db_search()
    def _getAppealedGoods(status=0, **kwargs):
        appealing = aliased(Member)
        appealed = aliased(Member)
        return Appeal.query.filter_by(status=status).join(appealing,
                                                          appealing.id == Appeal.member_id).join(Good,
                                                                                                 Good.id == Appeal.goods_id).join(
            appealed, Good.owner_id == appealed.id).add_entity(Good).add_entity(appealing).add_entity(appealed)

    @staticmethod
    @user_op
    def _setGoodsAppealDealt(appeal_id=0, user=None, result='', **kwargs):
        Appeal.query.filter_by(id=appeal_id, status=0).update(
            {'result': result, 'status': 1, 'user_id': user.uid}, synchronize_session=False)
        return True, '操作成功'

    @staticmethod
    @user_op
    def _userDelGoodsAppeal(appeal_id=0, user=None, **kwargs):
        Appeal.query.filter_by(id=appeal_id, status=1).update({'deleted_by': user.uid}, synchronize_session=False)
        return True, '操作成功'


class AppealHandlers:
    __handlers = {
        'goods': GoodsAppealHandler,
        'block': BlockAppealHandler
    }

    @classmethod
    def get(cls, biz_type):
        return cls.__handlers.get(biz_type)
