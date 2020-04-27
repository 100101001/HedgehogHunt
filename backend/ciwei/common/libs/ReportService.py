# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/4/20 下午9:39
@file: ReportService.py
@desc: 
"""
from application import db, APP_CONSTANTS, app
from common.libs.MemberService import MemberService
from common.models.ciwei.Goods import Good
from common.models.ciwei.Report import Report
from common.models.ciwei.Thanks import Thank

REPORT_CONSTANTS = APP_CONSTANTS['report']


def newGoodReport(reporting_goods=None, reporting_member=None):
    """
    新增举报（一条记录可被举报多次，状态变化 0->1->0->?）
    :param reporting_goods:
    :param reporting_member:
    :return:
    """
    report = Report.query.filter_by(record_id=reporting_goods.id, record_type=1).first()
    if report:
        report.deleted_by = 0
        report.status = 1
    else:
        report = Report()
        # 被举报的物品信息链接
        report.record_id = reporting_goods.id
        report.record_type = 1  # 标识举报链接的是物品ID
        report.member_id = reporting_goods.member_id  # 被举报物品的作者
    # 举报用户的身份信息
    report.report_member_id = reporting_member.id
    report.report_member_nickname = reporting_member.nickname
    report.report_member_avatar = reporting_member.avatar
    db.session.add(report)




def setStuffReportDealt(stuff_id=0, stuff_type=0, report_status=0, reported_stuff_status=0,
                        user_id=0):
    """
    设置举报处理标记
    :param stuff_id:
    :param stuff_type:
    :param report_status:
    :param reported_stuff_status:
    :param user_id:
    :return:
    """
    if stuff_type not in (0, 1):
        app.logger.error("{0}.{1}".format('错误的拉黑对象类型', 1))
        return None

    stuffs = [Thank, Good]
    Stuff = stuffs[stuff_type]
    reported_stuff = Stuff.query.filter_by(id=stuff_id).join(Report, Report.record_id == Stuff.id).add_entity(
        Report).first()
    report, stuff = reported_stuff.Report, reported_stuff.Stuff

    report.status = report_status
    stuff.report_status = reported_stuff_status
    report.user_id = stuff.user_id = user_id
    db.session.add(report)
    db.session.add(stuff)
    return reported_stuff


class GoodsReportHandler:
    __strategy_map = {2: '_recoverGoods',
                      3: '_blockGoods',
                      4: '_blockGoodsReporter',
                      5: '_blockGoodsReleaser'}

    @staticmethod
    def deal(op_status, goods_id, user_id):
        strategy = GoodsReportHandler.__strategy_map.get(op_status)
        handler = getattr(GoodsReportHandler, strategy, None)
        if handler:
            handler(goods_id=goods_id, user_id=user_id)

    @staticmethod
    def _recoverGoods(goods_id=0, user_id=0):
        """
        无违规，涉及Good标记清除和redis恢复
        :param goods_id:
        :param user_id:
        :return:
        """
        GoodsReportHandler.__setGoodReportDealt(goods_id=goods_id, report_status=2, reported_stuff_status=0, user_id=user_id)
        db.session.commit()

    @staticmethod
    def _blockGoods(goods_id=0, user_id=0):
        """
        违规物，删除
        :param goods_id:
        :param user_id:
        :return:
        """
        GoodsReportHandler.__setGoodReportDealt(goods_id=goods_id, report_status=3, reported_stuff_status=3, user_id=user_id)
        db.session.commit()

    @staticmethod
    def _blockGoodsReporter(goods_id=0, user_id=0):
        """
        拉黑举报用户，把其所有正常的帖子也软封锁
        涉及Good标记清除和redis恢复
        :param goods_id:
        :param user_id:
        :return:
        """
        reported_goods = GoodsReportHandler.__setGoodReportDealt(goods_id=goods_id, report_status=4,
                                                                 reported_stuff_status=0, user_id=user_id)
        # 软封锁账户，提前记录，避免后面再次查数据库
        blocked_member_id = reported_goods.Report.report_member_id
        # redis 候选同步，提交前提前转换，避免后面再次查数据库
        db.session.commit()
        # 因为会员被拉黑了，所以相当于所有的物品都因为被举报而封锁
        GoodsReportHandler.__blockGoodsMember(member_id=blocked_member_id, user_id=user_id, goods_id=goods_id, block_status=-1)

    @staticmethod
    def _blockGoodsReleaser(goods_id=0, user_id=0):
        """
        拉黑发布者，删除本举报贴，把其所有正常的帖子也软封锁
        :param goods_id:
        :param user_id:
        :return:
        """
        reported_goods = GoodsReportHandler.__setGoodReportDealt(goods_id=goods_id, report_status=5, reported_stuff_status=5,
                                            user_id=user_id)
        # 软封锁账户，提前记录，避免后面再次查数据库
        blocked_member_id = reported_goods.Report.member_id
        db.session.commit()
        # 因为会员被拉黑了，所以相当于所有的物品都因为被举报而封锁
        GoodsReportHandler.__blockGoodsMember(member_id=blocked_member_id, user_id=user_id, goods_id=goods_id, block_status=0)

    @staticmethod
    def __blockGoodsMember(member_id=0, user_id=0, goods_id=0, block_status=0):
        """
        因为物品举报而封锁用户账户的包装
        :param member_id:
        :param user_id:
        :param goods_id:
        :param block_status:
        :return:
        """
        MemberService.blockMember(member_id=member_id, user_id=user_id, stuff_id=goods_id,
                                  stuff_type=REPORT_CONSTANTS['stuff_type']['goods'],
                                  block_reason="恶意发帖" if not block_status else '恶意举报', block_status=block_status)

    @staticmethod
    def __setGoodReportDealt(goods_id=0, report_status=2, reported_stuff_status=0, user_id=0):
        """
        物品举报包装方法
        :param goods_id:
        :param report_status:
        :param reported_stuff_status:
        :param user_id:
        :return:
        """
        return setStuffReportDealt(stuff_id=goods_id,
                                   stuff_type=REPORT_CONSTANTS['stuff_type']['goods'],
                                   report_status=report_status,
                                   reported_stuff_status=reported_stuff_status,
                                   user_id=user_id)


class ThankReportHandler:
    __strategy_map = {2: '_recoverThanks',
                      3: '_blockThanks',
                      4: '_blockThankReceiver',
                      5: '_blockThankSender'}

    @staticmethod
    def deal(op_status, thank_id, user_id):
        strategy = ThankReportHandler.__strategy_map.get(op_status)
        handler = getattr(ThankReportHandler, strategy, None)
        if handler:
            handler(thank_id=thank_id, user_id=user_id)

    @staticmethod
    def _recoverThanks(thank_id=0, user_id=0):
        """
        答谢无违规
        :param thank_id:
        :param user_id:
        :return:
        """
        if not thank_id or not user_id:
            return
        ThankReportHandler.__setThankReportDealt(thank_id=thank_id, report_status=2, reported_stuff_status=0,
                                                 user_id=user_id)
        db.session.commit()

    @staticmethod
    def _blockThanks(thank_id=0, user_id=0):
        """
        屏蔽答谢
        :param thank_id:
        :param user_id:
        :return:
        """
        if not thank_id or not user_id:
            return
        ThankReportHandler.__setThankReportDealt(thank_id=thank_id, report_status=3, reported_stuff_status=3,
                                                 user_id=user_id)
        db.session.commit()

    @staticmethod
    def _blockThankReceiver(thank_id=0, user_id=0):
        """
        收到答谢的举报者
        :param thank_id:
        :param user_id:
        :return:
        """
        reported_thanks = ThankReportHandler.__setThankReportDealt(thank_id=thank_id, report_status=4,
                                                                   reported_stuff_status=0,
                                                                   user_id=user_id)
        blk_mid = reported_thanks.Report.report_member_id
        db.session.commit()
        ThankReportHandler.__blockThankMember(member_id=blk_mid, user_id=user_id,
                                              thank_id=thank_id, block_status=-1)

    @staticmethod
    def _blockThankSender(thank_id=0, user_id=0):
        """
        发出答谢的人，被举报的人
        :param thank_id:
        :param user_id:
        :return:
        """
        reported_thanks = ThankReportHandler.__setThankReportDealt(thank_id=thank_id, report_status=5,
                                                                   reported_stuff_status=5,
                                                                   user_id=user_id)
        blk_mid = reported_thanks.Report.member_id
        db.session.commit()
        ThankReportHandler.__blockThankMember(member_id=blk_mid, user_id=user_id,
                                              thank_id=thank_id, block_status=0)

    @staticmethod
    def __blockThankMember(member_id=0, user_id=0, thank_id=0, block_status=0):
        """
        因为答谢举报而封锁用户账户的包装
        :param member_id:
        :param user_id:
        :param thank_id:
        :param block_status:
        :return:
        """
        MemberService.blockMember(member_id=member_id, user_id=user_id,
                                  stuff_type=REPORT_CONSTANTS['stuff_type']['thanks'], stuff_id=thank_id,
                                  block_reason='恶意答谢' if not block_status else '恶意举报', block_status=block_status)

    @staticmethod
    def __setThankReportDealt(thank_id=0, report_status=2, reported_stuff_status=0, user_id=0):
        """
        答谢举报处理包装方法
        :param thank_id:
        :param report_status:
        :param reported_stuff_status:
        :param user_id:
        :return:
        """
        return setStuffReportDealt(stuff_id=thank_id,
                                   stuff_type=REPORT_CONSTANTS['stuff_type']['thanks'],
                                   report_status=report_status,
                                   reported_stuff_status=reported_stuff_status,
                                   user_id=user_id)


class ReportHandlers:
    __handler_map = {
        'goods': GoodsReportHandler,
        'thanks': ThankReportHandler
    }

    @staticmethod
    def getHandler(report_type):
        return ReportHandlers.__handler_map.get(report_type)
