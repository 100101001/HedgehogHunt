# coding: utf-8
from sqlalchemy.dialects.mssql import TINYINT
from sqlalchemy.dialects.mysql import INTEGER
from application import db
from datetime import datetime


class Report(db.Model):
    __tablename__ = 'report'
    __table_args__ = ({'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4', 'comment': '举报消息表'})

    id = db.Column(INTEGER(11, unsigned=True), primary_key=True, autoincrement=True)
    user_id = db.Column(INTEGER(11, unsigned=True), nullable=False, default=0, comment="处理举报的管理员id")
    member_id = db.Column(INTEGER(11, unsigned=True), nullable=False, comment="发布消息的会员id")
    report_member_id = db.Column(INTEGER(11, unsigned=True), nullable=False, comment="举报消息的会员id")
    report_member_nickname = db.Column(db.String(100), nullable=False, default='', comment="举报消息的会员名")
    report_member_avatar = db.Column(db.String(200), nullable=False, default='', comment="举报消息的会员头像")
    record_id = db.Column(INTEGER(11, unsigned=True), nullable=False, index=True, comment="信息id，有可能是物品信息违规，也可能是用户的答谢违规")
    summary = db.Column(db.String(200), nullable=False, default='', comment="描述")
    status = db.Column(TINYINT(), nullable=False, default=1, index=True, comment="状态 1：已读 0：未读")
    record_type = db.Column(TINYINT(), nullable=False, default=1, index=True,
                            comment="状态 1：物品信息违规 0：答谢信息违规")
    deleted_by = db.Column(INTEGER(11, unsigned=True), index=True, default=0, comment="删除举报的管理员id")
    updated_time = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now, comment="最后更新时间")
    created_time = db.Column(db.DateTime, nullable=False, default=datetime.now, comment="插入时间")

    @property
    def report_status_desc(self):
        report_status_mapping = {
            '1': '待处理',
            '2': '已拉黑举报者',
            '3': '已拉黑发布者',
            '4': '无违规',  # 举报待处理
            '5': '商品违规但不拉黑人员，我也不看了的记录',  # 举报待处理
        }
        return report_status_mapping[str(self.status)]


    @staticmethod
    def create(record_type=0, reported_record=None, reporter=None):
        report = Report.query.filter_by(record_id=reported_record.id,
                                        record_type=record_type).first()
        if report:
            report.deleted_by = 0
            report.status = 1
        else:
            report = Report()
            # 被举报的物品信息链接
            report.record_id = reported_record.id
            report.record_type = record_type  # 标识举报链接的是物品ID或者答谢ID
            report.member_id = reported_record.member_id  # 被举报物品的作者或答谢者
        # 举报用户的身份信息
        report.report_member_id = reporter.id
        report.report_member_nickname = reporter.nickname
        report.report_member_avatar = reporter.avatar
        reported_record.report_status = 1  # 待处理举报
        db.session.add(reported_record)
        db.session.add(report)

    @staticmethod
    def setDealt(report=None, status=0, reported_record=None, record_status=0, user_id=0):
        report.status = status
        reported_record.report_status = record_status
        report.user_id = reported_record.user_id = user_id
        db.session.add(report)
        db.session.add(reported_record)