#!/usr/bin/python3.6.8
#Editor weichaoxu

# -*- coding:utf-8 -*-
from common.models.ciwei.Member import Member
from common.models.ciwei.User import User
from common.models.ciwei.Goods import Good
from common.models.ciwei.Report import Report
from web.controllers.api import route_api
from flask import request,jsonify,g
from application import app,db
from common.libs.Helper import getCurrentDate
from common.libs.MemberService import MemberService
from common.libs.UrlManager import UrlManager


#查询所有记录
@route_api.route("/record/search",methods=['GET','POST'])
def recordSearch():
    resp={'code':200,'msg':'search record successfully(search)','data':{}}
    req=request.values

    member_info = g.member_info
    if not member_info:
        resp['code'] = -1
        resp['msg'] = "没有相关用户信息"
        return jsonify(resp)

    p=int(req['p']) if ('p' in req and req['p']) else 1
    if p<1:
        p=1

    page_size=10
    offset=(p-1)*page_size

    #获取用户的发布信息
    query=Good.query.filter_by(member_id=member_info.id)
    business_type = int(req['business_type']) if 'business_type' in req else 'nono'
    if business_type==0 or business_type==1:
        query = query.filter_by(business_type=business_type)

    status=req['status'] if 'status' in req else "nonono"
    if business_type==0 or business_type==1:
        query = query.filter_by(status=status)

    goods_list=query.order_by(Good.updated_time.desc()).offset(offset).limit(10).all()
    #将对应的用户信息取出来，组合之后返回
    # goods_list=goods_list_onshow+goods_list_hide
    data_goods_list = []
    if goods_list:
        for item in goods_list:
            tmp_data = {
                "id": item.id,
                "goods_name":item.name,
                "created_time":str(item.created_time),
                "updated_time":str(item.updated_time),
                "business_type":item.business_type,
                "target_price":str(item.target_price),
                "main_image":UrlManager.buildImageUrl(item.main_image),
                "status":item.status
            }
            data_goods_list.append(tmp_data)

    resp['data']['list']=data_goods_list
    resp['data']['has_more']=0 if len(data_goods_list)<page_size else 1
    return jsonify(resp)

#上架与下架
@route_api.route("/record/change-status",methods=['GET','POST'])
def recordChangeStatus():
    resp={'code':200,'msg':'search record successfully(search)','data':{}}
    req=request.values

    member_info = g.member_info
    if not member_info:
        resp['code'] = -1
        resp['msg'] = "没有相关用户信息"
        return jsonify(resp)

    id=req['id'] if 'id' in req else 0
    goods_info = Good.query.filter_by(id=id).first()
    if not goods_info:
        resp['code'] = -1
        resp['msg'] = '没有找到该条记录'
        return jsonify(resp)
    goods_info.updated_time=getCurrentDate()

    if goods_info.status==1:
        goods_info.status=0
    elif goods_info.status==0:
        goods_info.status=1
    else:
        pass

    db.session.add(goods_info)
    db.session.commit()
    return jsonify(resp)
