# coding: utf-8
import decimal

from sqlalchemy.dialects.mssql import TINYINT
from sqlalchemy.dialects.mysql import INTEGER
from application import db
from datetime import datetime


class Good(db.Model):
    __tablename__ = 'goods'
    __table_args__ = ({'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4', 'comment': '物品表'})

    id = db.Column(INTEGER(11, unsigned=True), primary_key=True, autoincrement=True)
    user_id = db.Column(INTEGER(11, unsigned=True), nullable=False, default=0, comment="拉黑会员的管理员id")
    member_id = db.Column(INTEGER(11, unsigned=True), nullable=False, index=True, default=0, comment="发布消息的会员id")
    openid = db.Column(db.String(80), nullable=False, default='', comment="第三方id")
    nickname = db.Column(db.String(100), nullable=False, default='', comment="发布消息的会员昵称")
    avatar = db.Column(db.String(200), nullable=False, default='', comment="发布消息的会员头像")
    mobile = db.Column(db.String(20), nullable=False, default='', comment="会员手机号码")
    owner_id = db.Column(INTEGER(11, unsigned=True), nullable=False, default=0, comment="最终取回物品的会员id")
    name = db.Column(db.String(80), nullable=False, default='', comment="商品名称")
    owner_name = db.Column(db.String(100), nullable=False, default='', comment="物主姓名")
    os_location = db.Column(db.String(100), nullable=False, default='', comment="物品发现和丢失地址")
    location = db.Column(db.String(100), nullable=False, default='', comment="物品放置地址和失主住址")
    target_price = db.Column(db.Numeric(10, 2), nullable=False, default=decimal.Decimal(0.00), comment="悬赏金额")
    main_image = db.Column(db.String(100), nullable=False, default='', comment="主图")
    pics = db.Column(db.String(1000), nullable=False, default='', comment="组图")
    summary = db.Column(db.String(1000), nullable=False, default='', comment="描述")
    business_type = db.Column(TINYINT(), nullable=False, default=1, comment="状态 1:失物招领 0:寻物启事 2:寻物归还与扫码归还")
    qr_code_openid = db.Column(db.String(80), nullable=True, index=True, default='', comment="扫描上传信息的二维码id")
    return_goods_id = db.Column(INTEGER(11, unsigned=True), nullable=True, default=0, comment="归还的寻物启示ID")
    return_goods_openid = db.Column(db.String(80), nullable=True, index=True, default='', comment="扫描上传信息的二维码id")
    status = db.Column(TINYINT(), index=True, nullable=False, default=7, comment="1:待, 2:预, "
                                                                                 "3:已, "
                                                                                 "4:已答谢 "
                                                                                 "5:管理员删, "
                                                                                 "7:发布者创建中, "
                                                                                 "8:发布者被管理员拉黑"
                                                                                 "1: 待取回归还"
                                                                                 "2：已取回归还")
    view_count = db.Column(INTEGER(11, unsigned=True), nullable=False, index=True,  default=0, comment="总浏览次数")
    top_expire_time = db.Column(db.DateTime, nullable=False, index=True, default=datetime.now,
                                comment='置顶过期时间')
    recommended_times = db.Column(INTEGER(11, unsigned=True), nullable=False, default=1, comment="有未读推荐")
    report_status = db.Column(TINYINT(), nullable=False, default=0, comment="被举报后的状态，用于存储举报的状态值")
    confirm_time = db.Column(db.DateTime, nullable=True, default=datetime.now, comment="在线认领时间")
    finish_time = db.Column(db.DateTime, nullable=True, default=datetime.now, comment="线下取回时间")
    thank_time = db.Column(db.DateTime, nullable=True, default=datetime.now, comment="答谢时间")
    appeal_time = db.Column(db.DateTime, nullable=True, default=datetime.now, comment="申诉时间")
    updated_time = db.Column(db.DateTime, nullable=False, default=datetime.now, comment="最后更新时间")
    created_time = db.Column(db.DateTime, nullable=False, default=datetime.now, comment="插入时间")

    @property
    def status_desc(self):
        if self.business_type == 1:
            status_mapping = {
                '1': '待认领',
                '2': '预认领',
                '3': '已认领',
                '4': '已答谢',
                '5': '申诉中',
                '7': '已删除',
            }
        elif self.business_type == 0:
            status_mapping = {
                '1': '待寻回',
                '2': '预寻回',
                '3': '已寻回',
                '4': '已答谢',
                '7': '已删除',
            }
        else:  # 归还贴子
            status_mapping = {
                '0': '已拒绝',
                '1': '待确认',
                '2': '待取回',
                '3': '已取回',
                '4': '已答谢',
                '7': '已删除',
            }
        return status_mapping[str(self.status)]

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

    @property
    def category_desc(self):
        category_mapping = {
            '1': '钱包',
            '2': '钥匙',
            "3": "卡类/证照",
            "4": "数码产品",
            "5": "手袋/挎包",
            "6": "衣服/鞋帽",
            "7": "首饰/挂饰",
            "8": "行李/包裹",
            "9": "书籍/文件",
            "10": "其它"
        }
        return category_mapping[str(self.category)]
