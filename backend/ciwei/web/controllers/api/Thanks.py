#!/usr/bin/python3.6.8
#Editor weichaoxu

# -*- coding:utf-8 -*-
from common.models.ciwei.Member import Member
from common.models.ciwei.User import User
from common.models.ciwei.Goods import Good
from common.models.ciwei.Thanks import Thank
from web.controllers.api import route_api
from flask import request,jsonify,g
import json
from sqlalchemy import or_
from application import app,db
from common.libs.Helper import getCurrentDate
from common.libs.MemberService import MemberService
from common.libs.UrlManager import UrlManager
from decimal import Decimal

@route_api.route("/thanks/create",methods=['GET','POST'])
def thanksCreate():
    resp={'code':200,'msg':'create thanks record successfully(search)','data':{}}
    req=request.values

    member_info = g.member_info
    if not member_info:
        resp['code'] = -1
        resp['msg'] = "用户信息异常"
        return jsonify(resp)

    thanks_model = Thank()
    thanks_model.member_id=member_info.id

    target_member_id=int(req['auther_id']) if 'auther_id' in req else 0
    thanks_model.target_member_id=target_member_id
    business_type=int(req['business_type'])
    if business_type==1:
        thanks_model.business_desc="拾到"
    else:
        thanks_model.business_desc="丢失"
    goods_id=int(req['goods_id']) if 'goods_id' in req else 0
    goods_name=req['goods_name'] if 'goods_name' in req else 0
    owner_name=req['owner_name'] if 'owner_name' in req else 0
    thanks_model.goods_name=goods_name
    thanks_model.owner_name=owner_name
    thanks_model.price=Decimal(req['target_price']).quantize(Decimal('0.00')) if  'target_price' in req else 0.00
    if thanks_model.price==0.00:
        thanks_model.order_id=0
    thanks_model.summary=req['thanks_text'] if 'thanks_text' in req else ''
    thanks_model.goods_id=goods_id

    thanks_model.created_time=thanks_model.updated_time=getCurrentDate()

    db.session.add(thanks_model)
    db.session.commit()

    return jsonify(resp)


#查询所有记录
@route_api.route("/thanks/search",methods=['GET','POST'])
def thanksSearch():
    resp={'code':200,'msg':'search thanks successfully(thanks)','data':{}}
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
    query = Thank.query.filter(Thank.status!=7)
    query = query.filter(Thank.status!=6)
    query = query.filter(Thank.status!=5)
    query = query.filter(Thank.status!=4)

    owner_name = req['owner_name'] if 'owner_name' in req else ''
    if owner_name:
        rule = or_(Good.owner_name.ilike("%{0}%".format(owner_name)))
        query = query.filter(rule)

    mix_kw = str(req['mix_kw']) if 'mix_kw' in req else ''
    if mix_kw:
        fil_str = "%{0}%".format(mix_kw[0])
        for i in mix_kw[1:]:
            fil_str = fil_str + "%{0}%".format(i)
        rule = or_(Good.name.ilike("%{0}%".format(fil_str)), Good.member_id.ilike("%{0}%".format(mix_kw)))
        query = query.filter(rule)

    #获取操作值，看用户是查看收到的还是发出的答谢信息
    status=int(req['op_status']) if 'op_status' in req else ''
    if status==0:
        query=query.filter_by(target_member_id=member_info.id)
    elif status==1:
        query=query.filter_by(member_id=member_info.id)
    elif status==2:
        pass

    only_new=req['only_new']
    if only_new=="true":
        query=query.filter_by(status=0)
    goods_list = query.order_by(Thank.id.desc()).offset(offset).limit(10).all()
    # #将对应的用户信息取出来，组合之后返回
    data_goods_list = []
    if goods_list:
        for item in goods_list:
            item_auther_info=Member.query.filter_by(id=item.member_id).first()
            tmp_data = {
                "id": item.id,
                "status":item.status,#不存在时置1
                "goods_name": item.goods_name,
                "owner_name": item.owner_name,
                "updated_time": str(item.updated_time),
                "business_desc":item.business_desc,
                "summary": item.summary,
                "reward":"0.00",
                "auther_name": item_auther_info.nickname,
                "avatar": item_auther_info.avatar,
                "selected": False,
            }
            data_goods_list.append(tmp_data)
            if item.status==0 and member_info.id==item.target_member_id:
                item.status=1
                item.updated_time=getCurrentDate()
                db.session.add(item)
                db.session.commit()


    resp['data']['list'] = data_goods_list
    resp['data']['has_more'] = 0 if len(data_goods_list) < page_size else 1
    return jsonify(resp)
#将商品移除自己的列表
@route_api.route("/thanks/delete",methods=['GET','POST'])
def thanksDelete():
    resp={'code':200,'msg':'delete record successfully','data':{}}
    req=request.values

    member_info = g.member_info
    if not member_info:
        resp['code'] = -1
        resp['msg'] = "没有相关用户信息"
        return jsonify(resp)

    """
    op_status=0,用户的发布记录
    op_statis=1,用户的认领记录
    op_status=2,用户的推荐列表
    """

    id_list=req['id_list'][1:-1].split(',')
    for i in id_list:
        goods_info = Thank.query.filter_by(id=int(i)).first()
        goods_info.status=7
        db.session.add(goods_info)
        db.session.commit()

    return jsonify(resp)