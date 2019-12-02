#!/usr/bin/python3.6.8
#Editor weichaoxu

# -*- coding:utf-8 -*-

from common.models.ciwei.Feedback import Feedback
from common.models.ciwei.Member import Member
from common.models.ciwei.Goods import Good
from common.models.ciwei.Report import Report
from web.controllers.api import route_api
from flask import request,jsonify,g
from application import app,db

@route_api.route('/static/num', methods=['GET', 'POST'])
def staticNumber():
    resp={'code':200,'msg':'获取数据成功'}
    member_info = g.member_info
    if not member_info:
        resp['code'] = -1
        resp['msg'] = "用户信息异常"
        return jsonify(resp)

    #上架与下架的商品数量
    on_sell_num=len(Good.query.filter_by(status=1).all())
    on_hide_num=len(Good.query.filter_by(status=0).all())
    total_num=len(Good.query.filter(Good.status!=2).all())

    #总浏览量
    total_view_count=0
    total_goods=Good.query.all()
    for item in total_goods:
        total_view_count=total_view_count+item.view_count


    #闲置的数量
    sell_num=len(Good.query.filter_by(business_type=1).all())
    buy_num=len(Good.query.filter_by(business_type=0).all())

    #举报数量
    report_num=len(Report.query.all())
    feedback_num=len(Feedback.query.all())

    #黑名单数量
    block_member_num=len(Member.query.filter_by(status=0).all())
    member_num=len(Member.query.all())

    items=[
        {
            "label": "总浏览量",
            "num": total_view_count,
        },
        {
            "label": "会员数",
            "num": member_num,
        },{
            "label": "黑名单数",
            "num": block_member_num,
        },
        {
            "label": "商品总数",
            "num": total_num,
        },
        {
            "label": "在线数",
            "num": on_sell_num,
        },
        {
            "label": "下架数",
            "num": on_hide_num,
        },
        {
            "label": "闲置数",
            "num": sell_num,
        },
        {
            "label": "求购数",
            "num": buy_num,
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

    resp={'code':200,'data':{}}
    resp['data']['items']=items

    return jsonify(resp)