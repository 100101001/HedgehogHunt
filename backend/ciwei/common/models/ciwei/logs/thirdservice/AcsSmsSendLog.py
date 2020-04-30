# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/3/21 下午2:15
@file: AcsSmsSendLog.py
@desc:
"""

from datetime import datetime
import datetime as dt
from sqlalchemy import func
from sqlalchemy.dialects.mysql import INTEGER

from application import db, app


class AcsSmsSendLog(db.Model):
    __tablename__ = 'acs_sms_send_log'
    __table_args__ = ({'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4', 'comment': '阿里云服务短信发送调用日志'})

    id = db.Column(INTEGER(11, unsigned=True), primary_key=True, autoincrement=True)
    biz_uuid = db.Column(db.String(50), nullable=False, unique=True, comment='本地业务ID')
    trig_member_id = db.Column(INTEGER(11, unsigned=True), nullable=False, default=0, comment='触发发送短信的会员id')
    trig_openid = db.Column(db.String(32), nullable=False, default='', comment='触发发送短信的会员的第三方id')
    rcv_member_id = db.Column(INTEGER(11, unsigned=True), index=True, nullable=False, default=0, comment='收短信的会员id')
    rcv_openid = db.Column(db.String(32), nullable=False, index=True, default='', comment='收短信的会员的第三方id')
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

    @staticmethod
    def hasRecentLostNotify(openid='', now=datetime.now(), interval=dt.timedelta(weeks=1)):
        return db.session.query(func.count(AcsSmsSendLog.id)).filter(AcsSmsSendLog.rcv_openid == openid,
                                                                     AcsSmsSendLog.template_id ==
                                                                     app.config['ACS_SMS']['TEMP_IDS']['NOTIFY'],
                                                                     AcsSmsSendLog.acs_code == "OK",
                                                                     AcsSmsSendLog.created_time >= now - interval).scalar() > 0
