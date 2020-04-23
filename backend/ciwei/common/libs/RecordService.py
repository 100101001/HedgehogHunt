# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/4/19 上午1:24
@file: RecordService.py
@desc: 
"""
from sqlalchemy import and_, or_

from application import db, APP_CONSTANTS
from common.cahce import cas, CacheQueryService
from common.libs.UrlManager import UrlManager
from common.libs.recommend.v2 import SyncService
from common.models.ciwei.Appeal import Appeal
from common.models.ciwei.Goods import Good
from common.models.ciwei.Mark import Mark
from common.models.ciwei.Recommend import Recommend
from common.models.ciwei.Report import Report
from common.models.ciwei.Thanks import Thank
from common.tasks.sync import SyncTasks


def deleteMyRelease(goods_ids=None, biz_type=0, status=0):
    """
    删除了曾发帖子
    :param goods_ids:
    :param biz_type:
    :param status:
    :return:
    """
    if not goods_ids or biz_type not in (0, 1, 2) or status not in (0, 1, 2, 3, 4):
        return False
    ok_ids = []
    for item_id in goods_ids:
        # 保证申诉和删除不冲突
        if cas.exec(item_id, status, 7):
            ok_ids.append(item_id)
    Good.query.filter(Good.id.in_(ok_ids), Good.status == status).update({'status': 7}, synchronize_session=False)
    db.session.commit()
    SyncService.syncSoftDeleteGoodsToESBulk(goods_ids=goods_ids)
    if status == 1 and biz_type != 2:
        # 删除了待匹配的物品(失物招领和寻物启事的biz_type=1/0)
        SyncTasks.syncDelGoodsToRedis.delay(goods_ids=goods_ids, business_type=biz_type)
    return True


def deleteMyMark(goods_ids=None, member_id=0, status=0):
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
                      Mark.goods_id.in_(goods_ids)).update({'status': 7}, synchronize_session=False)
    db.session.commit()
    return True


def deleteReturnNotice(goods_ids=None, status=0):
    """
    删除归还帖与失主的链接关系
    :param goods_ids:
    :param status:
    :return:
    """
    if not goods_ids or status not in (1, 3, 4):
        return False
    Good.query.filter(Good.id.in_(goods_ids), Good.status == status). \
        update({'return_goods_openid': '',
                'qr_code_openid': ''}, synchronize_session=False)
    db.session.commit()
    return True


def deleteRecommendNotice(goods_ids=None, member_id=0):
    """
    删除匹配推荐
    :param goods_ids:
    :param member_id:
    :return:
    """
    if not goods_ids or not member_id:
        return
    Recommend.query.filter(Recommend.target_member_id == member_id,
                           Recommend.found_goods_id.in_(goods_ids)).update({'status': 7}, synchronize_session=False)
    db.session.commit()
    return True


def deleteMyAppeal(goods_ids=None, member_id=0):
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


def deleteGoodsReport(goods_ids=None, user_id=0):
    """
    管理员删除被举报的物品帖子
    :param goods_ids:
    :param user_id:
    :return:
    """
    if not goods_ids or not user_id:
        return False
    Report.query.filter(Report.record_type == 1, Report.record_id.in_(goods_ids)). \
        update({'deleted_by': user_id}, synchronize_session=False)
    db.session.commit()
    return True


def getMyRelease(member_id=0, biz_type=0, status=0):
    return Good.query.filter_by(member_id=member_id, status=status, business_type=biz_type)


def getMyMark(member_id=0, mark_status=0):
    """
    获取认领记录
    :param member_id:
    :param mark_status:
    :return:
    """
    return Good.query.join(Mark, Good.id == Mark.goods_id).filter(Mark.member_id == member_id,
                                                                  Mark.status == mark_status,
                                                                  Good.business_type == 1)


def getMyReturnNotice(member_openid='', return_status=0):
    """
    获取归还通知的SQL
    :param member_openid:
    :param return_status:
    :return:
    """
    return Good.query.filter(and_(Good.business_type == 2,
                                  Good.status == return_status,
                                  # 两类归还都要
                                  or_(Good.return_goods_openid == member_openid,
                                      Good.qr_code_openid == member_openid)))


def getMyAppeal(member_id=0, appeal_status=0):
    """

    :param member_id:
    :param appeal_status:
    :return:
    """
    return Good.query.join(Appeal, Good.id == Appeal.goods_id).filter(Appeal.member_id == member_id,
                                                                      Appeal.status == appeal_status)


def getMyRecommend(member_id=0, goods_status=0, only_new=True):
    """

    :param member_id:
    :param goods_status:
    :param only_new:
    :return:
    """
    rule = and_(Recommend.target_member_id == member_id,
                Recommend.status == 0 if only_new else Recommend.status != 7,
                Good.status == goods_status)
    return Good.query.join(Recommend,
                           Recommend.found_goods_id == Good.id).add_entity(Recommend).filter(rule)


def searchBarFilter(owner_name='', address='', goods_name=''):
    """
    获取记录页的搜索过滤条件
    :param owner_name:
    :param address:
    :param goods_name:
    :return:
    """
    # 搜索框筛选
    # 物主名 owner_name 或 物品名name
    rules = []
    if owner_name:
        fil_str = '%'.join([ch for ch in owner_name])
        rules.append(Good.owner_name.ilike("%{0}%".format(fil_str)))
    if goods_name:
        fil_str = '%'.join([ch for ch in goods_name])
        rules.append(Good.name.ilike("%{0}%".format(fil_str)))
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
    if not cas.exec_wrap(item_id, [item_status, 'nil'], item_status):  # 物品状态发生了变更
        return None
    is_pre_mark_fail = item_status != 2 and status == 0 and op_status == 1  # 物品状态已经不是预认领，但认领记录确是预认领
    is_appealed = item_status == 5  # 物品状态为 5 标示正在做申诉处理
    # 查看状态为预寻回的发布过的寻物记录，且还没有查看过，说明没有确认是自己的，搜易不能批量操作确认取回
    unconfirmed_returned_lost = item.business_type == 0 and op_status == 0 and item.status == 2 \
                                and not cas.exec(item.return_goods_id, 2, 2)  # 如果看过那么一定有状态记录
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
        "status_desc": str(item.status_desc),  # 静态属性，返回状态码对应的文字
        "main_image": UrlManager.buildImageUrl(item.main_image),
        "selected": False,  # 供前端选中删除记录用的属性
        "unselectable": is_appealed or is_pre_mark_fail or unconfirmed_returned_lost or is_reported,  # 前端编辑禁止选中
        "top": item.top_expire_time > now,  # 是否为置顶记录
        "updated_time": str(item.updated_time)
    }
    return record


"""
后半部分与答谢记录查看与举报相关
"""


def deleteMyThanks(thank_ids=None):
    """
    删除答谢记录
    :param thank_ids:
    :return:
    """
    if not thank_ids:
        return False
    Thank.query.filter(Thank.id.in_(thank_ids)).update({'status': 7}, synchronize_session=False)
    db.session.commit()
    return True


def deleteReportedThanks(thank_ids=None, user_id=0):
    """
    同时删除答谢和答谢举报记录
    :param thank_ids:
    :param user_id:
    :return:
    """
    if not thank_ids or not user_id:
        return False
    Thank.query.filter(Thank.id.in_(thank_ids)). \
        update({'user_id': user_id, 'report_status': 5}, synchronize_session=False)
    Report.query.filter(Report.record_type == 0, Report.record_id.in_(thank_ids)). \
        update({'user_id': user_id, 'status': 5}, synchronize_session=False)
    db.session.commit()
    return True


def getMyReceivedThanks(member_id=0, only_new=False):
    """
    获取我收到的别人对我的答谢记录
    :param member_id:
    :param only_new:
    :return:
    """

    status_rule = Thank.status == 0 if only_new else Thank.status.in_([0, 1])
    query = Thank.query.filter(Thank.target_member_id == member_id, status_rule)
    return query


def getMySendThanks(member_id=0, only_new=False):
    """
    获取我发出的答谢记录
    :param member_id:
    :param only_new:
    :return:
    """
    status_rule = Thank.status == 0 if only_new else Thank.status.in_([0, 1])
    query = Thank.query.filter(Thank.member_id == member_id, status_rule)
    return query


def getReportedThanks(report_status=0, p=1):
    """
    获取特定页的举报记录
    :param report_status:
    :param p:
    :return:
    """
    p = max(p, 1)
    page_size = APP_CONSTANTS['page_size']
    offset = (p - 1) * page_size
    # 同时返回 Report和Thank
    return Thank.query.join(Report, Report.record_id == Thank.id).add_entity(Report).filter(
        Report.status == report_status,
        Report.record_type == 0).order_by(Report.id.desc()).offset(offset).limit(page_size).all()


def makeReportThankRecord(reported_thank=None):
    """
    组装答谢举报记录
    :param reported_thank:
    :return:
    """
    report, thank = reported_thank.Report, reported_thank.Thank
    reported_thank_record = {
        # 答谢记录本身的信息
        "id": thank.id,
        "status": thank.status,  # 不存在时置1
        "goods_name": thank.goods_name,
        "owner_name": thank.owner_name,
        "updated_time": str(thank.updated_time),
        "business_desc": thank.business_desc,
        "summary": thank.summary,  # 答谢文字
        "reward": str(thank.thank_price),
        "member_id": thank.id,
        "auther_name": thank.nickname,
        "avatar": thank.avatar,
        "selected": False,
        # 答谢举报的信息
        "report_member_id": report.report_member_id,
        "report_member_avatar": report.report_member_avatar,
        "report_member_name": report.report_member_nickname,
        "report_updated_time": str(report.updated_time),
        "report_id": report.id,
    }
    return reported_thank_record
