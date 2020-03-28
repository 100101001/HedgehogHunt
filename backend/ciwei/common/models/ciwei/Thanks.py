# coding: utf-8
import decimal
from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.dialects.mssql import TINYINT
from sqlalchemy.dialects.mysql import INTEGER
from flask_sqlalchemy import SQLAlchemy
from application import db
from datetime import datetime


class Thank(db.Model):
    __tablename__ = 'thanks'
    __table_args__ = ({'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4', 'comment': '答谢表'})

    id = db.Column(INTEGER(11, unsigned=True), primary_key=True, autoincrement=True)
    user_id = db.Column(INTEGER(11, unsigned=True), nullable=False, default=0, comment="拉黑会员的管理员id")
    member_id = db.Column(INTEGER(11, unsigned=True), nullable=False, index=True, comment="发布感谢的会员id")
    order_id = db.Column(INTEGER(11, unsigned=True), nullable=False, comment="微信支付的订单id")
    thank_price = db.Column(db.Numeric(10, 2), nullable=False, default=decimal.Decimal(0.00), comment="答谢总金额")
    target_member_id = db.Column(INTEGER(11, unsigned=True), nullable=False, index=True, comment="接受消息的会员id")
    goods_id = db.Column(INTEGER(11, unsigned=True), nullable=False, comment="物品id")
    summary = db.Column(db.String(200), nullable=False, default='', comment="描述")
    goods_name = db.Column(db.String(30), nullable=False, default='', comment="物品名称")
    business_desc = db.Column(db.String(10), nullable=False, default='', comment="拾到或者丢失")
    owner_name = db.Column(db.String(80), nullable=False, default='', comment="用户的名称，可能只是微信昵称")
    status = db.Column(TINYINT(), nullable=False, default=0, comment="状态 1：已读 0：未读")
    report_status = db.Column(TINYINT(), nullable=False, default=1, comment="被举报后的状态，用于存储举报的状态值")
    updated_time = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now, comment="最后更新时间")
    created_time = db.Column(db.DateTime, nullable=False, default=datetime.now, comment="插入时间")
