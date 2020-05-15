# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/4/19 上午1:24
@file: RecordService.py
@desc: 
"""
import datetime

from sqlalchemy import and_, or_

from application import db, APP_CONSTANTS
from common.admin import UserService
from common.admin.decorators import user_op
from common.cahce.GoodsCasUtil import GoodsCasUtil
from common.libs.UrlManager import UrlManager
from common.models.ciwei.admin.Appeal import Appeal
from common.models.ciwei.Goods import Good
from common.models.ciwei.Mark import Mark
from common.models.ciwei.Recommend import Recommend
from common.models.ciwei.admin.Report import Report
from common.models.ciwei.Thanks import Thank
from common.search.decorators import db_search, es_search


def searchBarFilter(owner_name='', address='', goods_name='', record_type=0):
    """
    获取记录页的搜索过滤条件
    :param record_type:
    :param owner_name:
    :param address:
    :param goods_name:
    :return:
    """
    # 搜索框筛选
    # 物主名 owner_name 或 物品名name
    stuffs = [Thank, Good]
    stuff = stuffs[record_type]
    rules = []
    if owner_name:
        fil_str = '%'.join([ch for ch in owner_name])
        rules.append(stuff.owner_name.ilike("%{0}%".format(fil_str)))
    if goods_name:
        fil_str = '%'.join([ch for ch in goods_name])
        if hasattr(stuff, 'name'):
            rules.append(stuff.name.ilike("%{0}%".format(fil_str)))
        elif hasattr(stuff, 'goods_name'):
            rules.append(stuff.goods_name.ilike("%{0}%".format(fil_str)))
    return and_(*rules)


def makeRecordData(item=None, op_status=0, status=0, now=None):
    """
    拼装记录数据
    :param now:
    :param item:
    :param op_status:
    :param status:
    :return:
    """
    recommend_status = 1
    if op_status == 2:
        item, recommend_status = item.Good, item.Recommend.status
    item_id = item.id
    item_status = item.status
    if not GoodsCasUtil.exec_wrap(item_id, [item_status, 'nil'], item_status):  # 物品状态发生了变更
        return None
    is_pre_mark_fail = item_status != 2 and status == 0 and op_status == 1  # 物品状态已经不是预认领，但认领记录确是预认领
    is_appealed = item_status == 5 and op_status in (0, 1, 6)  # 物品状态为 5 标示正在做申诉处理
    # 查看状态为预寻回的发布过的寻物记录，没有确认归还是自己的，所以不能批量操作确认取回
    unconfirmed_returned_lost = item.business_type == 0 and op_status == 0 and item.status == 2 \
                                and not GoodsCasUtil.exec(item.return_goods_id, 2, 2)  # 如果看过那么一定有状态记录
    is_reported = item.report_status != 0
    show_record_loc = op_status == 0 or op_status == 5
    record = {
        "id": item.id,  # 供前端用户点击查看详情用的
        "new": recommend_status,
        # 不存在时置不是new记录
        "auther_name": item.nickname,
        "avatar": item.avatar,
        "goods_name": item.name,
        "owner_name": item.owner_name,
        "location": item.location.split("###")[1] if show_record_loc else "",  # 归还贴和发布贴概要可看地址
        "summary": item.summary,
        "business_type": item.business_type,
        "status": int(item.status),
        "status_desc": str(item.status_desc),  # 静态属性，返回状态码对应的文字
        "main_image": UrlManager.buildImageUrl(item.main_image),
        "selected": False,  # 供前端选中删除记录用的属性
        "unselectable": is_appealed or is_pre_mark_fail or unconfirmed_returned_lost or is_reported,  # 前端编辑禁止选中
        "top": item.top_expire_time > now if op_status else datetime.datetime.strptime(item.top_expire_time,
                                                                                       "%Y-%m-%dT%H:%M:%S") > now,
        # 是否为置顶记录
        "updated_time": str(item.updated_time)
    }
    return record


class GoodsOpRecordDeleteHandler:
    """
    删除和物品相关的记录
    具体有以下6种
    """
    __strategy_map = {
        0: '_deleteMyRelease',
        1: '_deleteMyMark',
        2: '_deleteRecommendNotice',
        4: '_deleteGoodsReport',
        5: '_deleteReturnNotice',
        6: '_deleteMyAppeal'
    }

    @classmethod
    def deal(cls, op_status, **kwargs):
        strategy = cls.__strategy_map.get(op_status)
        handler = getattr(cls, strategy, None)
        if handler:
            return handler(**kwargs)

    @staticmethod
    def _deleteMyRelease(goods_ids=None, biz_type=0, status=0, **kwargs):
        """
        删除了曾发帖子
        :param goods_ids:
        :param biz_type:
        :param status:
        :return:
        """
        if not goods_ids or biz_type not in (0, 1, 2) or status not in (0, 1, 2, 3, 4):
            return False
        ok_ids = GoodsCasUtil.filter(goods_ids, exp_val=status, new_val=-status)
        if ok_ids:
            Good.batch_update(Good.id.in_(ok_ids), Good.status == status, val={'status': -status}, rds=-int(biz_type))
        db.session.commit()
        return True

    @staticmethod
    def _deleteMyMark(goods_ids=None, member_id=0, status=0, **kwargs):
        """
        删除认领记录（软删除）
        :param goods_ids:
        :param member_id:
        :param status:
        :return:
        """
        if not goods_ids or not member_id or status not in (0, 1, 2):
            return False
        Mark.query.filter(Mark.member_id == member_id,
                          Mark.status == status,
                          Mark.goods_id.in_(goods_ids)).update({'status': -Mark.status-1}, synchronize_session=False)
        db.session.commit()
        return True

    @staticmethod
    def _deleteReturnNotice(goods_ids=None, status=0, **kwargs):
        """
        删除归还帖与失主的链接关系
        :param goods_ids:
        :param status:
        :return:
        """
        if not goods_ids or status not in (1, 3, 4):
            return False
        Good.batch_update(Good.id.in_(goods_ids), Good.status == status,
                          val={'return_goods_openid': '', 'qr_code_openid': ''})
        db.session.commit()
        return True

    @staticmethod
    def _deleteRecommendNotice(goods_ids=None, member_id=0, **kwargs):
        """
        删除匹配推荐
        :param goods_ids:
        :param member_id:
        :return:
        """
        if not goods_ids or not member_id:
            return
        Recommend.query.filter(Recommend.target_member_id == member_id,
                               Recommend.found_goods_id.in_(goods_ids)).update({'status': -Recommend.status-1}, synchronize_session=False)
        db.session.commit()
        return True

    @staticmethod
    def _deleteMyAppeal(goods_ids=None, member_id=0, **kwargs):
        """
        用户删除申诉记录
        :param goods_ids:
        :param member_id:
        :return:
        """
        if not goods_ids or not member_id:
            return False
        Appeal.query.filter(Appeal.member_id == member_id,
                            Appeal.status == 1,
                            Appeal.goods_id.in_(goods_ids)).update({'status': 7}, synchronize_session=False)
        db.session.commit()
        return True

    @staticmethod
    @user_op
    def _deleteGoodsReport(goods_ids=None, user=None, **kwargs):
        """
        管理员删除被举报的物品帖子
        :param goods_ids:
        :param user:
        :return:
        """
        Report.query.filter(Report.record_type == 1, Report.record_id.in_(goods_ids), Report.deleted_by == 0,
                            Report.status != 1). \
            update({'deleted_by': user.uid}, synchronize_session=False)
        db.session.commit()


class GoodsRecordSearchHandler:
    """
    搜索物品相关的记录，具体有以下7种
    """
    __strategy_map = {
        -1: '_getPublicRelease',
        0: '_getMyRelease',
        1: '_getMyMark',
        2: '_getMyRecommend',
        4: '_getReportedGoods',
        5: '_getMyReturnNotice',
        6: '_getMyAppeal'
    }

    @classmethod
    def deal(cls, op_status, **kwargs):
        strategy = cls.__strategy_map.get(op_status)
        handler = getattr(cls, strategy, None)
        if handler:
            return handler(record_type=APP_CONSTANTS['stuff_type']['goods'], **kwargs)

    @staticmethod
    @db_search()
    def _getReportedGoods(report_status=0, **kwargs):
        """7
        获取所有举报物品
        :param report_status:
        :param kwargs:
        :return:
        """
        return Good.query.join(Report, Report.record_id == Good.id).filter(Report.record_type == 1,
                                                                           Report.status == report_status,
                                                                           Report.deleted_by == 0)

    @staticmethod
    @es_search
    def _getPublicRelease(biz_type=0, status=0, **kwargs):
        """
        公开的物品帖子记录
        :param biz_type:
        :param status:
        :param kwargs:
        :return:
        """
        report_status_must = {"match": {"report_status": 0}}  # 举报帖子将暂时隐藏
        biz_type_must = {"match": {"business_type": biz_type}}
        # status_must = {"match": {"status": status}} if status != 0 else {}
        # must = [biz_type_must, report_status_must, status_must]
        must = [biz_type_must, report_status_must]
        status_should = [{"match": {"status": status}}] if status != 0 else [{"match": {"status": 1}}, {"match": {"status": 2}}, {"match": {"status": 3}}, {"match": {"status": 4}}]
        query = {
            'query': {
                "bool": {
                    'must': must,
                    'should': status_should,
                    "minimum_should_match": 1
                }
            },
            "from": 0,
            "size": 0,
            "sort": [
                {"_score": {"order": "desc"}},
                {"top_expire_time": {"order": "desc"}}
            ]
        }
        return query

    @staticmethod
    @es_search
    def _getMyRelease(member_id=0, biz_type=0, status=0, **kwargs):
        """
        发布记录
        :param member_id:
        :param biz_type:
        :param status:
        :param kwargs:
        :return:
        """
        report_status_should = [{"match": {"report_status": 0}}, {"match": {"report_status": 1}}]  # 举报帖子将暂时隐藏
        biz_type_must = {"match": {"business_type": biz_type}}
        status_must = {"match": {"status": status}}
        member_must = {"match": {"member_id": member_id}}
        must = [member_must, biz_type_must, status_must]
        query = {
            'query': {
                "bool": {
                    'must': must,
                    'should': report_status_should,
                    'minimum_should_match': 1
                },
            },
            "from": 0,
            "size": 0,
            "sort": [{"_score": {"order": "desc"}},
                     {"id": {"order": "desc"}}]
        }
        return query

    @staticmethod
    @db_search()
    def _getMyMark(member_id=0, status=0, **kwargs):
        """
        获取认领记录
        :param member_id:
        :param status:
        :return:
        """
        return Good.query.join(Mark, Good.id == Mark.goods_id).filter(Mark.member_id == member_id,
                                                                      Mark.status == status,
                                                                      Good.business_type == 1)

    @staticmethod
    @db_search()
    def _getMyReturnNotice(member_openid='', status=0, **kwargs):
        """
        获取归还通知
        :param member_openid:
        :param status:
        :return:
        """
        return Good.query.filter(and_(Good.business_type == 2,
                                      Good.status == status,
                                      # 两类归还都要
                                      or_(Good.return_goods_openid == member_openid,
                                          Good.qr_code_openid == member_openid)))

    @staticmethod
    @db_search()
    def _getMyAppeal(member_id=0, status=0, **kwargs):
        """
        获取申诉记录
        :param member_id:
        :param status:
        :return:
        """
        return Good.query.join(Appeal, Good.id == Appeal.goods_id).filter(Appeal.member_id == member_id,
                                                                          Appeal.status == status)

    @staticmethod
    @db_search()
    def _getMyRecommend(member_id=0, status=0, only_new=True, **kwargs):
        """
        获取推荐记录
        :param member_id:
        :param status:
        :param only_new:
        :return:
        """
        rule = and_(Recommend.target_member_id == member_id,
                    Recommend.status == 0 if only_new else Recommend.status >= 0,
                    Good.status == status)
        return Good.query.join(Recommend,
                               Recommend.found_goods_id == Good.id).add_entity(Recommend).filter(rule)


class ThanksRecordDeleteHandler:
    """
    删除答谢相关的记录
    具体有以下三种
    """
    __strategy_map = {
        0: '_deleteMyReceivedThanks',
        1: '_deleteMyThanks',
        4: '_deleteReportedThanks'
    }

    @staticmethod
    def deal(op_status, **kwargs):
        strategy = ThanksRecordDeleteHandler.__strategy_map.get(op_status)
        handler = getattr(ThanksRecordDeleteHandler, strategy, None)
        if handler:
            return handler(**kwargs)

    @staticmethod
    def _deleteMyReceivedThanks(thank_ids=None, **kwargs):
        """
        删除收到答谢记录
        :param thank_ids:
        :return:
        """
        if not thank_ids:
            return False
        Thank.query.filter(Thank.id.in_(thank_ids)).update({'status': 2}, synchronize_session=False)
        db.session.commit()
        return True

    @staticmethod
    def _deleteMyThanks(thank_ids=None, **kwargs):
        """
        删除发出答谢记录
        :param thank_ids:
        :return:
        """
        if not thank_ids:
            return False
        Thank.query.filter(Thank.id.in_(thank_ids)).update({'status': 7}, synchronize_session=False)
        db.session.commit()
        return True

    @staticmethod
    @user_op
    def _deleteReportedThanks(thank_ids=None, user=None, **kwargs):
        """
        删除已处理过的答谢举报记录
        管理员必须是admin
        :param thank_ids:
        :param user:
        :return:
        """
        Report.query.filter(Report.record_type == 0, Report.record_id.in_(thank_ids)). \
            update({'deleted_by': user.uid}, synchronize_session=False)
        db.session.commit()


class ThanksRecordSearchHandler:
    """
    搜索答谢相关的记录
    具体有以下三种
    """
    __strategy_map = {
        0: '_getMyReceivedThanks',
        1: '_getMySendThanks',
        2: '_getReportedThanks'
    }

    @staticmethod
    def deal(op_status, **kwargs):
        strategy = ThanksRecordSearchHandler.__strategy_map.get(op_status)
        handler = getattr(ThanksRecordSearchHandler, strategy, None)
        if handler:
            return handler(record_type=APP_CONSTANTS['stuff_type']['thanks'], **kwargs)

    @staticmethod
    @db_search()
    def _getMyReceivedThanks(member_id=0, only_new=False, **kwargs):
        """
        获取我收到的别人对我的答谢记录
        :param member_id:
        :param only_new:
        :return:
        """

        status_rule = Thank.status == 0 if only_new else Thank.status != 2
        query = Thank.query.filter(Thank.target_member_id == member_id, status_rule)
        return query

    @staticmethod
    @db_search()
    def _getMySendThanks(member_id=0, only_new=False, **kwargs):
        """
        获取我发出的答谢记录
        :param member_id:
        :param only_new:
        :return:
        """
        status_rule = Thank.status == 0 if only_new else Thank.status != 7
        query = Thank.query.filter(Thank.member_id == member_id, status_rule)
        return query

    @staticmethod
    @db_search()
    def _getReportedThanks(report_status=0, **kwargs):
        """
        获取特定页的举报记录
        :param report_status:
        :param p:
        :return:
        """
        # 同时返回 Report和Thank
        return Thank.query.join(Report, Report.record_id == Thank.id).add_entity(Report).filter(
            Report.status == report_status,
            Report.record_type == 0,
            Report.deleted_by == 0)


class RecordHandlers:
    """
    获取记录操作对象
    按对象分为 物品相关和答谢相关
    按操作类型分为 搜索和答谢
    """
    __search_handlers = [ThanksRecordSearchHandler, GoodsRecordSearchHandler]

    __delete_handlers = [ThanksRecordDeleteHandler, GoodsOpRecordDeleteHandler]

    def __init__(self, handler_index=0):
        self.index = handler_index

    @staticmethod
    def get(record_type):
        return RecordHandlers(handler_index=APP_CONSTANTS['stuff_type'][record_type])

    def search(self):
        """
        获取搜索的
        :return:
        """
        return self.__search_handlers[self.index]

    def delete(self):
        """
        获取删除的
        :return:
        """
        return self.__delete_handlers[self.index]
