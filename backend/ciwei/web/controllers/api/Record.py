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
from sqlalchemy import or_
from common.libs.Helper import getCurrentDate,selectFilterObj,getDictFilterField
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
    status = int(req['status']) if ('status' in req and req['status']) else 0
    query = Good.query.filter_by(status=status)

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

    #状态值的字典，先置空
    recommend_dict={}
    #获取操作值，看用户是查看哪种信息
    # op_status
    # 0 自己发布的
    # 1 自己认领的
    # 2 自己
    op_status=int(req['op_status']) if 'op_status' in req else ''
    if op_status==0:
        query=query.filter_by(member_id=member_info.id)
    #找出推荐列表里面的所有物品信息
    elif op_status==1:
        if member_info.mark_id:
            mark_id_list=member_info.mark_id.split('#')
            mark_id_list_int=[int(i) for i in mark_id_list]
            query=query.filter(Good.id.in_(mark_id_list_int))
        else:
            resp['data']['list'] = []
            resp['data']['has_more'] = 0
            return jsonify(resp)
    elif op_status==2:
        if member_info.recommend_id:
            #获取推荐列表的字典，格式{id:0或者1}{1000：0}表示id为1000的数据未读
            only_new=req['only_new']
            if only_new=='false':
                recommend_dict=MemberService.getRecommendDict(member_info.recommend_id,False)
            else:
                recommend_dict = MemberService.getRecommendDict(member_info.recommend_id, True)
            recommend_id_list_int=recommend_dict.keys()
            query = query.filter(Good.id.in_(recommend_id_list_int))
        else:
            resp['data']['list'] = []
            resp['data']['has_more'] = 0
            return jsonify(resp)

    goods_list = query.order_by(Good.id.desc()).offset(offset).limit(10).all()
    # #将对应的用户信息取出来，组合之后返回
    data_goods_list = []
    if goods_list:
        for item in goods_list:
            tmp_data = {
                "id": item.id,
                "new":recommend_dict[item.id] if recommend_dict else 1,#不存在时置1
                "goods_name": item.name,
                "owner_name": item.owner_name,
                "updated_time": str(item.updated_time),
                "business_type": item.business_type,
                "summary": item.summary,
                "main_image": UrlManager.buildImageUrl(item.main_image),
                "auther_name": member_info.nickname,
                "avatar": member_info.avatar,
                "selected": False,
                "status_desc": str(item.status_desc),  # 静态属性，返回状态码对应的文字
            }
            data_goods_list.append(tmp_data)

    resp['data']['list'] = data_goods_list
    resp['data']['has_more'] = 0 if len(data_goods_list) < page_size else 1
    return jsonify(resp)
#将商品移除自己的列表
@route_api.route("/record/delete",methods=['GET','POST'])
def recordDelete():
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
    op_status = int(req['op_status']) if 'op_status' in req else ''
    id_list=req['id_list'][1:-1].split(',')

    if op_status==0:
        for i in id_list:
            goods_info = Good.query.filter_by(id=int(i)).first()
            goods_info.status=7
            db.session.add(goods_info)
            db.session.commit()
    elif op_status==1:
        mark_id_list=member_info.mark_id.split('#')
        for i in id_list:
            mark_id_list.remove(i)
            member_info.mark_id='#'.join(mark_id_list)
    elif op_status==2:
        recommend_id_dict=MemberService.getRecommendDict(member_info.recommend_id,False)
        for i in id_list:
            del recommend_id_dict[int(i)]
        member_info.recommend_id=MemberService.joinRecommendDict(recommend_id_dict)
    elif op_status==4:
        id_list_int=[int(i) for i in id_list]
        goods_list=Good.query.filter(Good.id.in_(id_list_int)).all()
        report_map=getDictFilterField(Report, Report.record_id, "record_id",id_list_int)
        user_info = User.query.filter_by(member_id=member_info.id).first()
        if not user_info:
            resp['code'] = -1
            resp['msg'] = "没有相关管理员信息，如需操作请添加管理员"
            resp['data'] = str(member_info.id) + "+" + member_info.nickname
            return jsonify(resp)
        if goods_list:
            for item in goods_list:
                report_item=report_map[item.id]
                report_item.user_id=user_info.uid
                report_item.status=5

                item.user_id=user_info.uid
                item.report_status=5
                item.updated_time=report_item.updated_time=getCurrentDate()
                db.session.add(item)
                db.session.add(report_item)
                db.session.commit()

    db.session.add(member_info)
    db.session.commit()
    return jsonify(resp)
