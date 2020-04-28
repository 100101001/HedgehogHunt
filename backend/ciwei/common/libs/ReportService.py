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
from common.libs.UrlManager import UrlManager
from common.models.ciwei.Goods import Good
from common.models.ciwei.Report import Report
from common.models.ciwei.Thanks import Thank


class ReportHandler:
    """
    各类举报通用方法，如：
    新增举报
    设置举报标记
    """

    @staticmethod
    def newStuffReport(reporting_stuff=None, reporting_member=None, record_type='goods'):
        """
        新增举报（一条记录可被举报多次，状态变化 0->1->0->?）
        :param record_type:
        :param reporting_stuff:
        :param reporting_member:
        :return:
        """
        report = Report.query.filter_by(record_id=reporting_stuff.id,
                                        record_type=APP_CONSTANTS['stuff_type'][record_type]).first()
        if report:
            report.deleted_by = 0
            report.status = 1
        else:
            report = Report()
            # 被举报的物品信息链接
            report.record_id = reporting_stuff.id
            report.record_type = 1  # 标识举报链接的是物品ID
            report.member_id = reporting_stuff.member_id  # 被举报物品的作者
        # 举报用户的身份信息
        report.report_member_id = reporting_member.id
        report.report_member_nickname = reporting_member.nickname
        report.report_member_avatar = reporting_member.avatar
        reporting_stuff.report_status = 1
        db.session.add(reporting_stuff)
        db.session.add(report)

    @staticmethod
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
        report, stuff = reported_stuff[1], reported_stuff[0]

        report.status = report_status
        stuff.report_status = reported_stuff_status
        report.user_id = stuff.user_id = user_id
        db.session.add(report)
        db.session.add(stuff)
        return reported_stuff


class GoodsReportHandler(ReportHandler):
    __strategy_map = {1: '_reportGoods',
                      2: '_recoverGoods',
                      3: '_blockGoods',
                      4: '_blockGoodsReporter',
                      5: '_blockGoodsReleaser'}

    @staticmethod
    def deal(op_status, **kwargs):
        strategy = GoodsReportHandler.__strategy_map.get(op_status)
        handler = getattr(GoodsReportHandler, strategy, None)
        if handler:
            handler(**kwargs)

    @classmethod
    def _reportGoods(cls, reporting_goods=None, reporting_member=None):
        super().newStuffReport(reporting_stuff=reporting_goods, reporting_member=reporting_member,
                               record_type='goods')

    @classmethod
    def _recoverGoods(cls, goods_id=0, user_id=0):
        """
        无违规，涉及Good标记清除和redis恢复
        :param goods_id:
        :param user_id:
        :return:
        """
        cls.__setGoodReportDealt(goods_id=goods_id, report_status=2, reported_stuff_status=0,
                                 user_id=user_id)
        db.session.commit()

    @classmethod
    def _blockGoods(cls, goods_id=0, user_id=0):
        """
        违规物，删除
        :param goods_id:
        :param user_id:
        :return:
        """
        cls.__setGoodReportDealt(goods_id=goods_id, report_status=3, reported_stuff_status=3,
                                 user_id=user_id)
        db.session.commit()

    @classmethod
    def _blockGoodsReporter(cls, goods_id=0, user_id=0):
        """
        拉黑举报用户，把其所有正常的帖子也软封锁
        涉及Good标记清除和redis恢复
        :param goods_id:
        :param user_id:
        :return:
        """
        reported_goods = cls.__setGoodReportDealt(goods_id=goods_id, report_status=4,
                                                  reported_stuff_status=0, user_id=user_id)
        # 软封锁账户，提前记录，避免后面再次查数据库
        blocked_member_id = reported_goods.Report.report_member_id
        # redis 候选同步，提交前提前转换，避免后面再次查数据库
        db.session.commit()
        # 因为会员被拉黑了，所以相当于所有的物品都因为被举报而封锁
        cls.__blockGoodsMember(member_id=blocked_member_id, user_id=user_id, goods_id=goods_id,
                               block_status=-1)

    @classmethod
    def _blockGoodsReleaser(cls, goods_id=0, user_id=0):
        """
        拉黑发布者，删除本举报贴，把其所有正常的帖子也软封锁
        :param goods_id:
        :param user_id:
        :return:
        """
        reported_goods = cls.__setGoodReportDealt(goods_id=goods_id, report_status=5,
                                                  reported_stuff_status=5,
                                                  user_id=user_id)
        # 软封锁账户，提前记录，避免后面再次查数据库
        blocked_member_id = reported_goods.Report.member_id
        db.session.commit()
        # 因为会员被拉黑了，所以相当于所有的物品都因为被举报而封锁
        cls.__blockGoodsMember(member_id=blocked_member_id, user_id=user_id, goods_id=goods_id,
                               block_status=0)

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
                                  stuff_type=APP_CONSTANTS['stuff_type']['goods'],
                                  block_reason="恶意发帖" if not block_status else '恶意举报', block_status=block_status)

    @classmethod
    def __setGoodReportDealt(cls, goods_id=0, report_status=2, reported_stuff_status=0, user_id=0):
        """
        物品举报包装方法
        :param goods_id:
        :param report_status:
        :param reported_stuff_status:
        :param user_id:
        :return:
        """
        return super().setStuffReportDealt(stuff_id=goods_id,
                                           stuff_type=APP_CONSTANTS['stuff_type']['goods'],
                                           report_status=report_status,
                                           reported_stuff_status=reported_stuff_status,
                                           user_id=user_id)


class ThankReportHandler(ReportHandler):
    __strategy_map = {1: '_reportThanks',
                      2: '_recoverThanks',
                      3: '_blockThanks',
                      4: '_blockThankReceiver',
                      5: '_blockThankSender'}

    @staticmethod
    def deal(op_status, **kwargs):
        strategy = ThankReportHandler.__strategy_map.get(op_status)
        handler = getattr(ThankReportHandler, strategy, None)
        if handler:
            handler(**kwargs)

    @classmethod
    def _reportThanks(cls, reporting_thanks=None, reporting_member=None):
        super().newStuffReport(reporting_stuff=reporting_thanks, reporting_member=reporting_member,
                               record_type='thanks')

    @classmethod
    def _recoverThanks(cls, thank_id=0, user_id=0):
        """
        答谢无违规
        :param thank_id:
        :param user_id:
        :return:
        """
        if not thank_id or not user_id:
            return
        cls.__setThankReportDealt(thank_id=thank_id, report_status=2, reported_stuff_status=0,
                                  user_id=user_id)
        db.session.commit()

    @classmethod
    def _blockThanks(cls, thank_id=0, user_id=0):
        """
        屏蔽答谢
        :param thank_id:
        :param user_id:
        :return:
        """
        if not thank_id or not user_id:
            return
        cls.__setThankReportDealt(thank_id=thank_id, report_status=3, reported_stuff_status=3,
                                  user_id=user_id)
        db.session.commit()

    @classmethod
    def _blockThankReceiver(cls, thank_id=0, user_id=0):
        """
        收到答谢的举报者
        :param thank_id:
        :param user_id:
        :return:
        """
        reported_thanks = cls.__setThankReportDealt(thank_id=thank_id, report_status=4,
                                                    reported_stuff_status=0,
                                                    user_id=user_id)
        blk_mid = reported_thanks.Report.report_member_id
        db.session.commit()
        cls.__blockThankMember(member_id=blk_mid, user_id=user_id,
                               thank_id=thank_id, block_status=-1)

    @classmethod
    def _blockThankSender(cls, thank_id=0, user_id=0):
        """
        发出答谢的人，被举报的人
        :param thank_id:
        :param user_id:
        :return:
        """
        reported_thanks = cls.__setThankReportDealt(thank_id=thank_id, report_status=5,
                                                    reported_stuff_status=5,
                                                    user_id=user_id)
        blk_mid = reported_thanks.Report.member_id
        db.session.commit()
        cls.__blockThankMember(member_id=blk_mid, user_id=user_id,
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
                                  stuff_type=APP_CONSTANTS['stuff_type']['thanks'], stuff_id=thank_id,
                                  block_reason='恶意答谢' if not block_status else '恶意举报', block_status=block_status)

    @classmethod
    def __setThankReportDealt(cls, thank_id=0, report_status=2, reported_stuff_status=0, user_id=0):
        """
        答谢举报处理包装方法
        :param thank_id:
        :param report_status:
        :param reported_stuff_status:
        :param user_id:
        :return:
        """
        return super().setStuffReportDealt(stuff_id=thank_id,
                                           stuff_type=APP_CONSTANTS['stuff_type']['thanks'],
                                           report_status=report_status,
                                           reported_stuff_status=reported_stuff_status,
                                           user_id=user_id)


class ReportHandlers:
    __handlers = [ThankReportHandler, GoodsReportHandler]

    @staticmethod
    def get(report_type):
        if report_type not in ('goods', 'thanks'):
            return None
        return ReportHandlers.__handlers[APP_CONSTANTS['stuff_type'][report_type]]


class ReportRecordMakers:
    __strategy_map = {'thanks': '_makeThankDetail',
                      'goods_detail': '_makeGoodsDetail',
                      'goods_record': '_makeGoodsRecord'}

    @staticmethod
    def get(op_status):
        strategy = ReportRecordMakers.__strategy_map.get(op_status)
        return getattr(ReportRecordMakers, strategy, ReportRecordMakers._dummyMaker)

    @staticmethod
    def _makeThankDetail(reported_thank=None, **kwargs):
        """
        组装有举报者的答谢举报记录
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

    @staticmethod
    def _makeGoodsDetail(reported_goods=None, **kwargs):
        goods, report = reported_goods.Good, reported_goods.Report
        location_list = goods.location.split("###")
        location_list[2] = eval(location_list[2])
        location_list[3] = eval(location_list[3])
        goods_info = {
            "id": goods.id,
            "goods_name": goods.name,
            "owner_name": goods.owner_name,
            "summary": goods.summary,
            "view_count": goods.view_count,
            "main_image": UrlManager.buildImageUrl(goods.main_image),
            "pics": [UrlManager.buildImageUrl(i) for i in goods.pics.split(",")],
            "updated_time": str(goods.updated_time),
            "location": location_list,
            "business_type": goods.business_type,
            "mobile": goods.mobile,
            "status_desc": str(goods.status_desc),
            "status": goods.status,
            # 作者和举报信息
            "auther_name": goods.nickname,
            "avatar": goods.avatar,
            "report_status": report.status
        }
        # 举报者身份信息
        reporter = {
            "avatar": report.report_member_avatar,
            "auther_name": report.report_member_nickname,
            "updated_time": str(report.updated_time),
            "is_auth": False,
            "is_reporter": True,
            "goods_status": goods.status,
        }
        return goods_info, reporter

    @staticmethod
    def _makeGoodsRecord(reported_goods=None, **kwargs):
        return {
            "id": reported_goods.id,  # 物品id
            "goods_name": reported_goods.name,  # 物品名
            "owner_name": reported_goods.owner_name,  # 物主
            "updated_time": str(reported_goods.updated_time),  # 编辑 or 新建时间
            "business_type": reported_goods.business_type,  # 寻物/失物招领
            "summary": reported_goods.summary,  # 描述
            "main_image": UrlManager.buildImageUrl(reported_goods.main_image),  # 首图
            "auther_name": reported_goods.nickname,  # 作者昵称
            "avatar": reported_goods.avatar,  # 作者头像
            "selected": False,  # 前段编辑属性
            "location": reported_goods.location.split("###")[1],  # 概要显示
            "status_desc": str(reported_goods.status_desc),  # 静态属性，返回状态码对应的文字
        }

    @staticmethod
    def _dummyMaker(**kwargs):
        return {}
