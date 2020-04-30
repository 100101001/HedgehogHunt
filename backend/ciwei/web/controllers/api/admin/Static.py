# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/4/21 上午2:36
@file: Static.py
@desc:
"""
from flask import g

from common.admin import StaticService
from common.loggin.time import time_log
from web.controllers.api import route_api


@route_api.route('/static/num', methods=['GET', 'POST'])
@time_log
def staticNumber():
    resp = {'code': -1, 'msg': '', 'data': {}}
    member_info = g.member_info
    if not member_info:
        resp['msg'] = "请先登录"
        return resp
    # 从ES统计各类发帖数据
    total_number, find_number, lost_number, lost_return_number, scan_return_number = StaticService.getGoodsStatics()

    # 取回和答谢（成果）
    gotback_number = StaticService.getGotBackStatics()
    thanks_number = StaticService.getThankStatics()
    # 物品浏览
    total_view_cnt = StaticService.getViewStatics()
    total_recommend, hit_recommend = StaticService.getRecommendStatics()
    # 举报和反馈
    report_number, feedback_num = StaticService.getReportAndFeedbackStatics()
    # 拉黑和会员
    member_number, block_member_number = StaticService.getMemberStatics()
    # 总收入
    total_count_income = StaticService.getSalesIncomeStatics()
    statics_table = [{
        "label": "总浏览量",  # 当天反应的是到前一天为止的不精确
        "num": str(total_view_cnt),  # sum 聚合返回的是Decimal
    }, {
        "label": "总物品数",
        "num": total_number,
    }, {
        "label": "失物招领数",  # 捡到
        "num": find_number,
    }, {
        "label": "寻物启事数",  # 丢失
        "num": lost_number,
    }, {
        "label": "寻物归还数",
        "num": lost_return_number
    }, {
        "label": "扫码归还数",
        "num": scan_return_number
    }, {
        "label": "总推荐数",
        "num": total_recommend
    }, {
        "label": "有效推荐",
        "num": hit_recommend
    }, {
        "label": "总取回数",
        "num": gotback_number,
    }, {
        "label": "总答谢数",
        "num": thanks_number,
    }, {
        "label": "总收入",  # 订单价格总和
        "num": str(total_count_income),
    }, {
        "label": "总会员数",  # 所有的注册用户
        "num": member_number,
    }, {
        "label": "黑名单数",  # 被拉黑的数量
        "num": block_member_number,
    }, {
        "label": "总举报数",
        "num": report_number,
    }, {
        "label": "总反馈数",
        "num": feedback_num,  # 改进意见
    }
    ]
    resp['code'] = 200
    resp['data']['items'] = statics_table
    return resp
