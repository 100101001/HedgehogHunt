# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/4/26 下午3:16
@file: GoodProxy.py
@desc: 
"""

from datetime import datetime
from decimal import Decimal


class GoodProxy:
    now = datetime.now()
    id = 0
    user_id = 0
    member_id = 100001
    openid = ""
    nickname = ""
    avatar = ""
    mobile = ""
    owner_id = 100002
    name = ""
    owner_name = ""
    os_location = ""
    location = ""
    target_price = Decimal("0.00")
    main_image = ""
    pics = ""
    summary = ""
    business_type = 1
    qr_code_openid = ""
    return_goods_id = 0
    return_goods_openid = ""
    status = 1
    view_count = 0
    top_expire_time = now
    recommended_times = 0
    report_status = 0
    confirm_time = now
    finish_time = now
    thank_time = now
    appeal_time = now
    updated_time = now
    created_time = now

    @property
    def status_desc(self):
        if self.report_status != 0:
            # 作者可以看到 1的帖子
            return self.report_status_desc
        if self.business_type == 1:
            status_mapping = {
                '1': '待认领',
                '2': '预认领',
                '3': '已认领',
                '4': '已答谢',
                '5': '申诉中',
                '-1': '已删除',
                '-2': '已删除',
                '-3': '已删除',
                '-4': '已删除',
            }
        elif self.business_type == 0:
            status_mapping = {
                '1': '待寻回',
                '2': '预寻回',
                '3': '已寻回',
                '4': '已答谢',
                '-1': '已删除',
                '-2': '已删除',
                '-3': '已删除',
                '-4': '已删除',
            }
        else:  # 归还贴子
            status_mapping = {
                '0': '已拒绝',
                '1': '待确认',
                '2': '待取回',
                '3': '已取回',
                '4': '已答谢',
                '-1': '已删除',
                '-2': '已删除',
                '-3': '已删除',
                '-4': '已删除',
            }
        return status_mapping[str(self.status)]

    @property
    def report_status_desc(self):
        report_status_mapping = {
            '1': '待处理',
            '2': '无违规',
            '3': '已屏蔽',  # 同时作者账号被拉黑，即使恢复账号后也不在恢复的帖子
            '4': '封举报者',
            '5': '封发布者',
        }
        return report_status_mapping[str(self.report_status)]
