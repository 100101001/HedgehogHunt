# coding: utf-8
from datetime import datetime

from sqlalchemy.dialects.mysql import INTEGER

from application import db


class AcsSmsSendLog(db.Model):
    __tablename__ = 'acs_sms_send_log'
    __table_args__ = ({'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4', 'comment': '阿里云服务短信发送调用日志'})

    id = db.Column(INTEGER(11, unsigned=True), primary_key=True, autoincrement=True)
    biz_uuid = db.Column(db.String(50), nullable=False, unique=True, comment='本地业务ID')
    phone_number = db.Column(db.String(20), nullable=False, index=True, comment='手机号')
    sign_name = db.Column(db.String(20), nullable=False, default="", comment='阿里云签名名称')
    template_id = db.Column(db.String(32), nullable=False, index=True, server_default=db.FetchedValue(), comment='阿里云模板id')
    params = db.Column(db.Text, nullable=False, comment='模板消息参数')
    acs_product_name = db.Column(db.String(20), nullable=False, comment='阿里云产品名')
    acs_resp_data = db.Column(db.Text, nullable=False, comment="响应数据")
    acs_request_id = db.Column(db.String(50), nullable=False, comment='调用请求ID')
    acs_biz_id = db.Column(db.String(50), nullable=False, comment='调用业务ID')
    acs_code = db.Column(db.String(32), nullable=False, comment='调用结果代码')
    updated_time = db.Column(db.DateTime, nullable=False, default=datetime.now, comment='最后一次更新时间')
    created_time = db.Column(db.DateTime, nullable=False, default=datetime.now, comment='创建时间')
