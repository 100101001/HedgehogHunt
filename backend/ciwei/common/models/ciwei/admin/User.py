# coding: utf-8
from datetime import datetime

from sqlalchemy.dialects.mssql import TINYINT
from sqlalchemy.dialects.mysql import INTEGER

from application import db


class User(db.Model):
    __tablename__ = 'user'
    __table_args__ = ({'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4', 'comment': '管理员表'})

    uid = db.Column(INTEGER(11, unsigned=True), primary_key=True, autoincrement=True, comment="管理员id")
    member_id = db.Column(INTEGER(11, unsigned=True), nullable=False, comment="注册会员id")
    level = db.Column(INTEGER(11, unsigned=True), nullable=False, comment="管理员等级")
    name = db.Column(db.String(100), nullable=False, default='', comment="用户名")
    mobile = db.Column(db.String(20), nullable=False, default='', comment="手机号码")
    email = db.Column(db.String(100), nullable=False, default='', comment="邮箱地址")
    sex = db.Column(TINYINT(), nullable=False, default=0, comment="1：男 2：女 0：没填写")
    avatar = db.Column(db.String(200), nullable=False, default='', comment="头像")
    op_uid = db.Column(INTEGER(11, unsigned=True), nullable=False, comment="操作的管理员id")
    status = db.Column(TINYINT(), nullable=False, default=1, comment="1：有效 0：无效")
    updated_time = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now,
                             comment="最后一次更新时间")
    created_time = db.Column(db.DateTime, nullable=False, default=datetime.now, comment="插入时间")


    def __init__(self, reg_info=None, member_info=None, op_user=None):
        self.name = reg_info.get('name', '')
        self.mobile = reg_info.get('mobile', '')
        self.email = reg_info.get('email', '')
        self.level = reg_info.get('level', 1)
        self.sex = member_info.sex
        self.avatar = member_info.avatar
        self.member_id = member_info.id
        self.op_uid = op_user.uid  # 操作新增管理员的管理员ID
        db.session.add(self)




