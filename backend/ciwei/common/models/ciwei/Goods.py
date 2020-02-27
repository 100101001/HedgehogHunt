# coding: utf-8
from sqlalchemy import Column, DateTime, Integer, Numeric, String
from sqlalchemy.schema import FetchedValue
from flask_sqlalchemy import SQLAlchemy
from application import db


class Good(db.Model):
    __tablename__ = 'goods'
    __table_args__ = ({'comment': '物品表'})

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), comment="拉黑会员的管理员id")
    member_id = db.Column(db.Integer, nullable=False, index=True, server_default=db.FetchedValue(), comment="发布消息的会员id")
    openid = db.Column(db.String(80), nullable=False, server_default=db.FetchedValue(), comment="第三方id")
    qr_code_id = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), comment="扫描上传信息的二维码id")
    mobile = db.Column(db.String(20), nullable=False, server_default=db.FetchedValue(), comment="会员手机号码")
    owner_id = db.Column(db.String(20), nullable=False, server_default=db.FetchedValue(), comment="最终取回物品的会员id,还是换成字符串吧")
    name = db.Column(db.String(80), nullable=False, server_default=db.FetchedValue(), comment="商品名称")
    owner_name = db.Column(db.String(100), nullable=False, server_default=db.FetchedValue(), comment="物主姓名")
    location = db.Column(db.String(100), nullable=False, server_default=db.FetchedValue(), comment="物品放置地址")
    target_price = db.Column(db.Numeric(10, 2), nullable=False, server_default=db.FetchedValue(), comment="悬赏金额")
    main_image = db.Column(db.String(100), nullable=False, server_default=db.FetchedValue(), comment="主图")
    pics = db.Column(db.String(1000), nullable=False, server_default=db.FetchedValue(), comment="组图")
    summary = db.Column(db.String(1000), nullable=False, server_default=db.FetchedValue(), comment="描述")
    status = db.Column(db.Integer, index=True, nullable=False, server_default=db.FetchedValue(), comment="1:待, 2:预, "
                                                                                                         "3:已, "
                                                                                                         "5:管理员删, "
                                                                                                         "7:发布者创建中, "
                                                                                                         "8:发布者被管理员拉黑")
    recommended_times = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), comment="总匹配过失/拾物次数")
    report_status = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), comment="被举报后的状态，用于存储举报的状态值")
    business_type = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), comment="状态 1：失物招领 0：寻物启事")
    view_count = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), comment="总浏览次数")
    tap_count = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue(), comment="查看地址次数")
    mark_id = db.Column(db.String(400), nullable=False, server_default=db.FetchedValue(), comment="点击获取或者提交的用户id,列表")
    updated_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), comment="最后更新时间")
    created_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue(), comment="插入时间")

    @property
    def status_desc(self):
        if self.business_type == 1:
            status_mapping = {
                '1': '待认领',
                '2': '预认领',
                '3': '已认领',
                '4': '已答谢',
                '7': '发布、修改储存未完成或者被发布者下架',
            }
        else:
            status_mapping = {
                '1': '待找回',
                '2': '预找回',
                '3': '已找回',
                '4': '已答谢',
                '7': '发布、修改储存未完成或者被发布者下架',
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
