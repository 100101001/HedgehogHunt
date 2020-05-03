# coding: utf-8
import decimal
from decimal import Decimal

from sqlalchemy.dialects.mssql import TINYINT
from sqlalchemy.dialects.mysql import INTEGER
from application import db
from datetime import datetime


class Thank(db.Model):
    __tablename__ = 'thanks'
    __table_args__ = ({'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4', 'comment': '答谢表'})

    id = db.Column(INTEGER(11, unsigned=True), primary_key=True, autoincrement=True)
    user_id = db.Column(INTEGER(11, unsigned=True), nullable=False, default=0, comment="拉黑会员的管理员id")
    member_id = db.Column(INTEGER(11, unsigned=True), nullable=False, index=True, comment="发布感谢的会员id")
    nickname = db.Column(db.String(100), nullable=False, default='', comment="发布感谢的会员昵称")
    avatar = db.Column(db.String(200), nullable=False, default='', comment="发布感谢的会员头像")
    order_sn = db.Column(db.String(40), nullable=False, unique=True, default='', comment="微信支付的订单流水号")
    thank_price = db.Column(db.Numeric(10, 2), nullable=False, default=decimal.Decimal(0.00), comment="答谢总金额")
    target_member_id = db.Column(INTEGER(11, unsigned=True), nullable=False, index=True, comment="接受消息的会员id")
    goods_id = db.Column(INTEGER(11, unsigned=True), nullable=False, comment="物品id")
    summary = db.Column(db.String(200), nullable=False, default='', comment="描述")
    goods_name = db.Column(db.String(30), nullable=False, default='', comment="物品名称")
    business_desc = db.Column(db.String(10), nullable=False, default='', comment="拾到或者丢失")
    owner_name = db.Column(db.String(80), nullable=False, default='', comment="用户的名称，可能只是微信昵称")
    status = db.Column(TINYINT(), nullable=False, default=0, comment="状态 1：已读 0：未读")
    report_status = db.Column(TINYINT(), nullable=False, default=0, comment="被举报后的状态，用于存储举报的状态值")
    updated_time = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now, comment="最后更新时间")
    created_time = db.Column(db.DateTime, nullable=False, default=datetime.now, comment="插入时间")



    def __init__(self, sender=None, gotback_goods=None, thank_info=None):
        self.member_id = sender.id  # 发出答谢的人
        self.nickname = sender.nickname  # 发出答谢的人
        self.avatar = sender.avatar  # 发出答谢的人
        # 被答谢物品信息
        self.target_member_id = int(gotback_goods.get('auther_id', 0))
        self.goods_id = int(gotback_goods.get('goods_id', 0))  # 答谢的物品id
        self.goods_name = gotback_goods.get('goods_name', '拾物')  # 答谢的物品名
        self.owner_name = gotback_goods.get('owner_name', '无')  # 答谢的物品的失主名
        business_type = int(gotback_goods.get('business_type', 1))  # 答谢的物品类型
        self.business_desc = "拾到" if business_type == 1 else "归还"
        # 答谢信息
        self.thank_price = Decimal(thank_info.get('target_price', '0')).quantize(Decimal('.00'))  # 答谢金额
        self.order_sn = thank_info.get('order_sn', '')  # 答谢支付订单
        self.summary = thank_info.get('thanks_text', '谢谢你的举手之劳！')  # 答谢文字，前端已判空
        db.session.add(self)

    @classmethod
    def readReceivedThanks(cls, member_id=0):
        cls.query.filter_by(target_member_id=member_id, status=0).update({'status': 1}, synchronize_session=False)