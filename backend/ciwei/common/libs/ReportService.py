# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/4/20 下午9:39
@file: ReportService.py
@desc: 
"""
from application import db
from common.libs import UserService
from common.models.ciwei.Goods import Good
from common.models.ciwei.Member import Member
from common.models.ciwei.Report import Report


def setGoodsReportStatus(goods_id=0, report_status=0, member_id=0):
    user = UserService.getUser(member_id=member_id)
    if not user:
        return False

    reported_goods = Good.query.filter_by(id=goods_id).join(Report, Report.record_id == Good.id).add_entity(
        Report).first()
    report, goods = reported_goods.Report, reported_goods.Good
    report.status = goods.report_status = report_status
    report.user_id = goods.user_id = user.uid

    report_member_id = report.report_member_id
    auther_id = report.member_id
    # 2: 拉黑举报者 3: 拉黑发布者
    if report_status in (2, 3):
        Member.query.filter_by(id=report_member_id if report_status == 2 else auther_id).update({'status': 0},
                                                                                                synchronize_session=False)
    else:  # 4无违规，因为操作可逆，一开始拉黑了，后面更改为无违规，所以需要同时更新两个人
        Member.query.filter(Member.id.in_([report_member_id, auther_id])).update({'status': 1},
                                                                                 synchronize_session=False)
    db.session.add(report)
    db.session.add(goods)
    db.session.commit()  # 更改提交
    return True