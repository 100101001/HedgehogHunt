# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/4/20 下午9:39
@file: ReportService.py
@desc: 
"""

from application import db
from common.libs.Helper import queryToDict
from common.libs.MemberService import MemberService
from common.libs.recommend.v2 import SyncService
from common.models.ciwei.Goods import Good
from common.models.ciwei.Report import Report
from common.tasks.sync import SyncTasks


def getReportedGoods(report_status=0):
    """
    :param report_status:
    :return:
    """
    return Good.query.join(Report, Report.record_id == Good.id).filter(Report.record_type == 1,
                                                                       Report.status == report_status,
                                                                       Report.deleted_by == 0)


def setGoodsReportDealt(goods_id=0, report_status=0, goods_report_status=0, user_id=0):
    """
    设置举报处理标记
    :param goods_id:
    :param report_status:
    :param goods_report_status:
    :param user_id:
    :return:
    """
    reported_goods = Good.query.filter_by(id=goods_id).join(Report, Report.record_id == Good.id).add_entity(
        Report).first()
    # 设置物品的举报状态和发布状态
    report, goods = reported_goods.Report, reported_goods.Good
    report.status = report_status
    goods.report_status = goods_report_status
    report.user_id = goods.user_id = user_id
    return reported_goods


def blockGoods(goods_id=0, user_id=0):
    """
    违规物，删除
    :param goods_id:
    :param user_id:
    :return:
    """
    reported_goods = setGoodsReportDealt(goods_id=goods_id, report_status=5, goods_report_status=5, user_id=user_id)
    goods = reported_goods.Good
    goods.status = 7
    # DB提交
    db.session.add(reported_goods.Report)
    db.session.add(reported_goods.Good)
    db.session.commit()
    # ES同步
    SyncService.syncUpdatedGoodsToES(goods_id=goods_id,
                                     updated={'report_status': 5, 'status': 7, 'user_id': user_id})


def recoverGoods(goods_id=0, user_id=0):
    """
    无违规，涉及Good标记清除和redis恢复
    :param goods_id:
    :param user_id:
    :return:
    """
    reported_goods = setGoodsReportDealt(goods_id=goods_id, report_status=4, goods_report_status=0, user_id=user_id)
    # DB 提交
    db.session.add(reported_goods.Report)
    db.session.add(reported_goods.Good)
    # redis 同步可能需要，提前记录，避免后面再次查数据库
    goods = queryToDict(reported_goods.Good)
    db.session.commit()
    # ES 同步
    SyncService.syncUpdatedGoodsToES(goods_id=goods_id,
                                     updated={'report_status': 0, 'user_id': user_id})
    # redis 同步
    if goods.get('status') == 1 and goods.get('business_type') != 2:
        # redis 候选去除(底层判断，上层透明)
        SyncTasks.syncNewGoodsToRedis.delay(goods_info=goods)


def blockReporter(goods_id=0, user_id=0):
    """
    拉黑举报用户，把其所有正常的帖子也软封锁
    涉及Good标记清除和redis恢复
    :param goods_id:
    :param user_id:
    :return:
    """
    reported_goods = setGoodsReportDealt(goods_id=goods_id, report_status=2, goods_report_status=0, user_id=user_id)
    # DB 提交
    db.session.add(reported_goods.Report)
    db.session.add(reported_goods.Good)
    # 软封锁账户，提前记录，避免后面再次查数据库
    blocked_member_id = reported_goods.Report.report_member_id
    # redis 候选同步，提交前提前转换，避免后面再次查数据库
    goods = queryToDict(reported_goods.Good)
    db.session.commit()
    # ES 同步
    SyncService.syncUpdatedGoodsToES(goods_id=goods_id,
                                     updated={'report_status': 0, 'user_id': user_id})
    # redis 同步
    if goods.get('status') == 1 and goods.get('business_type') != 2:
        # redis 候选去除(底层判断，上层透明)
        SyncTasks.syncNewGoodsToRedis.delay(goods_info=goods)
    # 因为会员被拉黑了，所以相当于所有的物品都因为被举报而封锁
    MemberService.blockMember(member_id=blocked_member_id, user_id=user_id)


def blockReleaser(goods_id=0, user_id=0):
    """
    拉黑发布者，删除本举报贴，把其所有正常的帖子也软封锁
    :param goods_id:
    :param user_id:
    :return:
    """
    reported_goods = setGoodsReportDealt(goods_id=goods_id, report_status=3, goods_report_status=3, user_id=user_id)
    # 删除当前用户的帖子
    goods = reported_goods.Good
    goods.status = 7
    db.session.add(reported_goods.Report)
    db.session.add(reported_goods.Good)
    # 软封锁账户，提前记录，避免后面再次查数据库
    blocked_member_id = goods.member_id
    db.session.commit()
    SyncService.syncUpdatedGoodsToES(goods_id=goods_id,
                                     updated={'report_status': 3, 'status': 7, 'user_id': user_id})
    # 因为会员被拉黑了，所以相当于所有的物品都因为被举报而封锁
    MemberService.blockMember(member_id=blocked_member_id, user_id=user_id)


def newGoodReport(reporting_goods=None, reporting_member=None):
    """
    新增举报（旧的记录可重用）
    :param reporting_goods:
    :param reporting_member:
    :return:
    """
    report = Report.query.filter_by(record_id=reporting_goods.id, record_type=1).first()
    if report:
        report.status = 1
    else:
        report = Report()
        # 被举报的物品信息链接
        report.record_id = reporting_goods.id
        report.record_type = 1  # 标识举报链接的是物品ID
        report.member_id = reporting_goods.member_id
    # 举报用户的身份信息
    report.report_member_id = reporting_member.id
    report.report_member_nickname = reporting_member.nickname
    report.report_member_avatar = reporting_member.avatar
    db.session.add(report)
