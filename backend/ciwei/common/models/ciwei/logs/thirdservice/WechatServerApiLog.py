# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/4/13 下午11:15
@file: WechatServerApiLog.py
@desc: 
"""


from datetime import datetime

from sqlalchemy.dialects.mysql import INTEGER

from application import db


class WechatServerApiLog(db.Model):
    __tablename__ = 'wechat_server_api_log'
    __table_args__ = ({'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4', 'comment': '微信服务端API调用日志'})

    id = db.Column(INTEGER(11, unsigned=True), primary_key=True, autoincrement=True)
    url = db.Column(db.String(128), nullable=False, index=True, comment='请求地址')
    token = db.Column(db.String(512), nullable=False, comment='请求令牌')
    req_data = db.Column(db.String(256), nullable=False, comment='请求数据')
    resp_data = db.Column(db.String(256), nullable=False, comment='响应数据')
    created_time = db.Column(db.DateTime, nullable=False, default=datetime.now, comment='创建时间')
