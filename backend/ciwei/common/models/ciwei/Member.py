# coding: utf-8
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.schema import FetchedValue
from flask_sqlalchemy import SQLAlchemy
from application import db


class Member(db.Model):
    __tablename__ = 'member'
    __table_args__ = ({'comment': '会员表'})

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), comment="拉黑会员的管理员id")
    qr_code_id = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), comment="小程序二维码id")
    nickname = db.Column(db.String(100), nullable=False, server_default=db.FetchedValue(), comment="会员名")
    salt = db.Column(db.String(255), nullable=False, server_default=db.FetchedValue(), comment="加密生成的字符串")
    credits = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), comment="会员积分")
    mobile = db.Column(db.String(20), nullable=False, server_default=db.FetchedValue(), comment="会员手机号码")
    name = db.Column(db.String(20), nullable=False, server_default=db.FetchedValue(), comment="注册会员的姓名，用于后期做匹配")
    location = db.Column(db.String(255), nullable=False, server_default=db.FetchedValue(), comment="会员收货地址")
    sex = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), comment="性别 1：男 2：女")
    avatar = db.Column(db.String(200), nullable=False, server_default=db.FetchedValue(), comment="会员头像")
    qr_code = db.Column(db.String(200), nullable=False, server_default=db.FetchedValue(), comment="会员的小程序二维码")
    openid = db.Column(db.String(80), nullable=False, server_default=db.FetchedValue(), comment="第三方id")
    status = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), comment="状态 1：有效 0：无效")
    updated_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), comment="最后一次更新时间")
    created_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), comment="插入时间")
    mark_id = db.Column(db.String(1000), nullable=False, server_default=db.FetchedValue(), comment="用户认领的物品id,字符串")
    gotback_id = db.Column(db.String(2000), nullable=False, server_default=db.FetchedValue(), comment="用户最终取回的物品id,字符串")
    recommend_id = db.Column(db.String(3000), nullable=False, server_default=db.FetchedValue(), comment="系统推荐的物品id,字符串")

    @property
    def has_qr_code(self):
        return self.qr_code != ""
