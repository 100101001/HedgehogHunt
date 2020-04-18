# -*- coding:utf-8 -*-

from flask import jsonify, g
from sqlalchemy import func

from application import db
from common.models.ciwei.Feedback import Feedback
from common.models.ciwei.Goods import Good
from common.models.ciwei.Member import Member
from common.models.ciwei.Report import Report
from web.controllers.api import route_api


@route_api.route('/static/num', methods=['GET', 'POST'])
def staticNumber():
    resp = {'code': 200, 'msg': '获取数据成功'}
    member_info = g.member_info
    if not member_info:
        resp['code'] = -1
        resp['msg'] = "用户信息异常"
        return jsonify(resp)

    # 上架与下架的商品数量
    total_num = db.session.query(func.count(Good.id)).groupby(Good.business_type)
    find_num = total_num[1][0]
    lost_num = total_num[0][0]
    gotback_num = db.session.query(func.count(Good.id)).filter_by(business_type=3).scalar()
    thanks_num = db.session.query(func.count(Good.id)).filter_by(business_type=4).scalar()
    total_num = len(Good.query.all())

    # 总浏览量
    total_view_count = 0
    total_goods = Good.query.all()
    for item in total_goods:
        total_view_count = total_view_count + item.view_count

    # 举报数量
    report_num = len(Report.query.all())
    feedback_num = len(Feedback.query.all())

    # 黑名单数量
    block_member_num = len(Member.query.filter_by(status=0).all())
    member_num = len(Member.query.all())

    # 总收入
    total_count_in = 0
    items = [
        {
            "label": "总浏览量",
            "num": total_view_count,
        },
        {
            "label": "总收入",
            "num": total_count_in,
        },
        {
            "label": "会员数",
            "num": member_num,
        }, {
            "label": "黑名单数",
            "num": block_member_num,
        },
        {
            "label": "商品总数",
            "num": total_num,
        },
        {
            "label": "失物招领数",
            "num": find_num,
        },
        {
            "label": "寻物启事数",
            "num": lost_num,
        },
        {
            "label": "取回数",
            "num": gotback_num,
        },
        {
            "label": "答谢数",
            "num": thanks_num,
        },
        {
            "label": "举报数",
            "num": report_num,
        },
        {
            "label": "反馈数",
            "num": feedback_num,
        },
    ]

    resp = {'code': 200, 'data': {}}
    resp['data']['items'] = items

    return jsonify(resp)
