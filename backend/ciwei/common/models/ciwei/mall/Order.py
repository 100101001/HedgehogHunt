# coding: utf-8
import decimal
from datetime import datetime

from sqlalchemy.dialects.mssql import TINYINT
from sqlalchemy.dialects.mysql import INTEGER

from application import db


class Order(db.Model):
    __tablename__ = 'order'
    __table_args__ = (
        db.Index('idx_member_id_status', 'member_id', 'status'),
        {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4', 'comment': '周边购买订单表'}
    )

    id = db.Column(INTEGER(11, unsigned=True), primary_key=True, autoincrement=True)
    order_sn = db.Column(db.String(40), nullable=False, unique=True, default='', comment="随机订单号")
    member_id = db.Column(INTEGER(11, unsigned=True), nullable=False, default=0, comment="会员id")
    total_price = db.Column(db.Numeric(10, 2), nullable=False, default=decimal.Decimal(0.00), comment="订单应付金额")
    yun_price = db.Column(db.Numeric(10, 2), nullable=False, default=decimal.Decimal(0.00), comment="运费金额")
    pay_price = db.Column(db.Numeric(10, 2), nullable=False, default=decimal.Decimal(0.00), comment="订单实付金额")
    discount_price = db.Column(db.Numeric(10, 2), nullable=False, default=decimal.Decimal(0.00), comment="订单折扣金额")
    discount_type = db.Column(db.String(40), nullable=False, default='', comment="折扣类型")
    pay_sn = db.Column(db.String(128), nullable=False, default='', comment="第三方流水号")
    prepay_id = db.Column(db.String(128), nullable=False, default='', comment="第三方预付id")
    note = db.Column(db.Text, nullable=False, comment="备注信息")
    status = db.Column(TINYINT(), nullable=False, default=0, index=True, comment="1：支付完成 0 无效 -1 申请退款 -2 "
                                                                     "退款中 -9 退款成功  -8 待支付  -7"
                                                                     " 完成支付待确认")
    express_status = db.Column(TINYINT(), nullable=False, default=0, comment="快递状态，-8 待支付 -7 "
                                                                             "已付款待发货 1：确认收货 "
                                                                             "0：失败")
    express_address_id = db.Column(db.Integer, nullable=False, default=0, comment="快递地址id")
    express_info = db.Column(db.String(1000), nullable=False, default='', comment="快递信息")
    express_sn = db.Column(db.String(50), nullable=False, default='', comment="快递单号")
    comment_status = db.Column(TINYINT(), nullable=False, default=0, comment="评论状态")
    pay_time = db.Column(db.DateTime, nullable=False, default=datetime.now, comment="付款到账时间")
    updated_time = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now,
                             comment="最后一次更新时间")
    created_time = db.Column(db.DateTime, nullable=False, default=datetime.now, comment="插入时间")

    @property
    def pay_status(self):
        tmp_status = self.status
        if self.status == 1:
            tmp_status = self.express_status
            if self.express_status == 1 and self.comment_status == 0:
                tmp_status = -5
            if self.express_status == 1 and self.comment_status == 1:
                tmp_status = 1
        return tmp_status

    @property
    def status_desc(self):
        pay_status_display_mapping = {
            "0": "订单关闭",
            "1": "支付成功",
            "-8": "待支付",
            "-7": "待发货",
            "-6": "待确认",
            "-5": "待评价"
        }
        return pay_status_display_mapping[str(self.pay_status)]

    @property
    def order_number(self):
        order_number = self.created_time.strftime("%Y%m%d%H%M%S")
        order_number = order_number + str(self.id).zfill(5)
        return order_number
