#!/usr/bin/python3.6.8
#Editor weichaoxu

# -*- coding:utf-8 -*-
from common.models.ciwei.Member import Member
from common.models.ciwei.User import User
from common.models.ciwei.Goods import Good
from common.models.ciwei.Thanks import Thank
from web.controllers.api import route_api
from flask import request,jsonify,g
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


# #查询所有举报信息
# @route_api.route("/thanks/search",methods=['GET','POST'])
# def thanksSearch():
#     resp={'code':200,'msg':'search record successfully(search)','data':{}}
#     req=request.values
#
#     member_info = g.member_info
#     if not member_info:
#         resp['code'] = -1
#         resp['msg'] = "用户信息异常"
#         return jsonify(resp)
#
#     p=int(req['p']) if ('p' in req and req['p']) else 1
#     if p<1:
#         p=1
#
#     page_size=10
#     offset=(p-1)*page_size
#
#     status=int(req['status']) if 'status' in req else "nonono"
#
#     report_list = Report.query.filter_by(status=status).all()
#     if not report_list:
#         resp['code'] = -1
#         resp['msg'] = '没有找到违规列表'
#         return jsonify(resp)
#
#     data_goods_list = []
#     #没有违规的状态也就是正常状态1
#     if status == 6:
#         status = 1
#     for report_i in report_list:
#         #将所有进过report表的id取出来
#         query = Good.query.filter_by(id=report_i.goods_id)
#         goods_info=query.filter_by(status=status).first()
#         #假如该条信息存在
#         if goods_info:
#             tmp_data = {
#                 "id": goods_info.id,
#                 "goods_name": goods_info.name,
#                 "created_time": str(goods_info.created_time),
#                 "updated_time": str(goods_info.updated_time),
#                 "business_type": goods_info.business_type,
#                 "target_price": str(goods_info.target_price),
#                 "main_image": UrlManager.buildImageUrl(goods_info.main_image),
#                 "status": goods_info.status,
#                 "status_desc": goods_info.status_desc
#             }
#             # 如果已经被处理过
#             user_info=User.query.filter_by(uid=report_i.user_id).first()
#             if user_info:
#                 tmp_data['status_desc']=user_info.name+goods_info.status_desc
#             else:
#                 tmp_data['status_desc'] = "管理员信息丢失"
#
#             data_goods_list.append(tmp_data)
#             if len(data_goods_list)>=page_size:
#                 break
#
#     resp['data']['list']=data_goods_list
#     resp['data']['has_more']=0 if len(data_goods_list)<page_size else 1
#     return jsonify(resp)
#
# #查看举报详情
# @route_api.route('/thanks/info')
# def thanksInfo():
#     resp = {'code': 200, 'msg': 'operate successfully(get info)', 'data': {}}
#     req = request.values
#
#     member_info = g.member_info
#     if not member_info:
#         resp['code'] = -1
#         resp['msg'] = "用户信息异常"
#         return jsonify(resp)
#
#     id = int(req['id']) if ('id' in req and req['id']) else 0
#
#     goods_info=Good.query.filter_by(id=id).first()
#     if not goods_info:
#         resp['code']=-1
#         resp['msg']='没有找到用户信息'
#         return jsonify(resp)
#
#
#     auther_info=Member.query.filter_by(id=goods_info.member_id).first()
#     if not auther_info:
#         resp = {'code': -1, 'msg': '没有找到用户信息', 'data': {}}
#         return jsonify(resp)
#
#     resp['data']['info']={
#         "id":goods_info.id,
#         "goods_name":goods_info.name,
#         "summary":goods_info.summary,
#         "view_count":goods_info.view_count+1,
#         "main_image":UrlManager.buildImageUrl(goods_info.main_image),
#         "target_price":str(goods_info.target_price),
#         "original_price":str(goods_info.original_price),
#         "stock":goods_info.stock,
#         "pics":[UrlManager.buildImageUrl(i) for i in goods_info.pics.split(",")],
#         "updated_time": str(goods_info.updated_time),
#         "cat_id":goods_info.cat_id,
#         "location":goods_info.location,
#         "qr_code_list":[UrlManager.buildImageUrl(auther_info.qr_code)],
#         "type_name":goods_info.type_name,
#         "business_type":goods_info.business_type,
#         "goods_status":goods_info.status,
#
#         #用户信息
#         "member_id":auther_info.id,
#         "auther_name": auther_info.nickname,
#         "avatar": auther_info.avatar,
#         "is_auth":False,
#         "check_report": True,
#         #实验代码，此处测试能否举报
#         # "is_auth":False
#     }
#
#     #如果同一个商品被多次举报，那么要除去它之前被举报但是没有违规的记录
#     report_query = Report.query.filter_by(goods_id=goods_info.id)
#     if goods_info.status==1:
#         report_info = report_query.filter_by(status=6).first()
#     else:
#         report_info = report_query.filter_by(status=goods_info.status).first()
#
#     if not report_info:
#         resp['code'] = -1
#         resp['msg'] = "没有找到相关记录"
#         return jsonify(resp)
#
#     report_member_info = Member.query.filter_by(id=report_info.report_member_id).first()
#     #没有找到用户信息则返回
#     if not report_member_info:
#         resp['data']['report_auth_info'] = {}
#         resp['msg']='举报者信息丢失'
#         resp['data']['report_id'] = report_info.id
#         return jsonify(resp)
#
#     resp['data']['report_auth_info']={
#         "avatar":report_member_info.avatar,
#         "auther_name":report_member_info.nickname,
#         "updated_time": str(report_member_info.updated_time),
#         "is_auth": False,
#         "check_report": True,
#         "member_id":report_member_info.id,
#         "goods_status":goods_info.status,
#     }
#
#     resp['data']['report_id']=report_info.id
#     return jsonify(resp)
#
# #该举报没有违规
# @route_api.route('/thanks/no-rule')
# def thanksNoRule():
#     resp = {'code': 200, 'msg': 'operate successfully(get info)', 'data': {}}
#     req = request.values
#
#     member_info = g.member_info
#     if not member_info:
#         resp['code'] = -1
#         resp['msg'] = "用户信息异常"
#         return jsonify(resp)
#
#     id = int(req['id']) if ('id' in req and req['id']) else 0
#     report_id = int(req['report_id']) if ('report_id' in req and req['report_id']) else 0
#
#     #如果同一个商品被多次举报，那么要除去她之前被举报但是没有违规的记录
#     report_info=Report.query.filter_by(id=report_id).first()
#     if not report_info:
#         resp['code'] = -1
#         resp['msg'] = '没有找到相关举报信息'
#         return jsonify(resp)
#
#     user_info=User.query.filter_by(member_id=member_info.id).first()
#     if not user_info:
#         resp['code']=-1
#         resp['msg']="没有找到管理员信息"
#         resp['data']=str(member_info.id)+"+"+member_info.name
#         return jsonify(resp)
#
#
#     report_info.status = 6
#     report_info.user_id=user_info.uid
#     report_info.updated_time = getCurrentDate()
#     db.session.add(report_info)
#     db.session.commit()
#
#     #解放商品信息
#     goods_info=Good.query.filter_by(id=id).first()
#     goods_info.status=1
#     goods_info.updated_time=getCurrentDate()
#     db.session.add(goods_info)
#     db.session.commit()
#
#     return jsonify(resp)
#
# #拉黑发布者或者举报者
# @route_api.route('/thanks/block')
# def thanksBlock():
#     resp = {'code': 200, 'msg': 'operate successfully(get info)', 'data': {}}
#     req = request.values
#
#     member_info = g.member_info
#     if not member_info:
#         resp['code'] = -1
#         resp['msg'] = "用户信息异常"
#         return jsonify(resp)
#
#     select_member_id = int(req['select_member_id']) if ('select_member_id' in req and req['select_member_id']) else 0
#     goods_id = int(req['goods_id']) if ('goods_id' in req and req['goods_id']) else 0
#     report_id = int(req['report_id']) if ('report_id' in req and req['report_id']) else 0
#     auth_id = int(req['auth_id']) if ('auth_id' in req and req['auth_id']) else 0
#     report_member_id = int(req['report_member_id']) if ('report_member_id' in req and req['report_member_id']) else 0
#
#     # 如果同一个商品被多次举报，那么要除去她之前被举报但是没有违规的记录
#     report_info = Report.query.filter_by(id=report_id).first()
#     if not report_info:
#         resp['code'] = -1
#         resp['msg'] = '没有找到相关举报信息'
#         return jsonify(resp)
#
#     goods_info = Good.query.filter_by(id=goods_id).first()
#     if not goods_info:
#         resp['code'] = -1
#         resp['msg'] = '没有找到相关商品信息'
#         return jsonify(resp)
#
#     if select_member_id==auth_id:
#         report_info.status = 4
#         goods_info.status=4
#     elif select_member_id==report_member_id:
#         report_info.status=5
#         goods_info.status =1
#     else:
#         pass
#
#     goods_info.updated_time = getCurrentDate()
#     db.session.add(goods_info)
#     db.session.commit()
#
#     user_info = User.query.filter_by(member_id=member_info.id).first()
#     if not user_info:
#         resp['code'] = -1
#         resp['msg'] = "没有相关管理员信息，如需操作请添加管理员"
#         resp['data'] = str(member_info.id) + "+" + member_info.nickname
#         return jsonify(resp)
#
#     #将报告信息及商品信息保存
#     report_info.user_id = user_info.uid
#     report_info.updated_time=getCurrentDate()
#     db.session.add(report_info)
#     db.session.commit()
#
#     #违规用户状态设置为0.则无法再正常使用
#     select_member_info = Member.query.filter_by(id=select_member_id).first()
#     if not member_info:
#         resp['code'] = -1
#         resp['msg'] = '没有找到该用户'
#         return jsonify(resp)
#
#     select_member_info.status = 0
#     select_member_info.updated_time = getCurrentDate()
#
#     # 该用户下正常的账户
#     goods_list = Good.query.filter(Good.member_id == select_member_id, Good.status == 1).all()
#     if goods_list:
#         for item in goods_list:
#             item.status = 8
#             item.updated_time = getCurrentDate()
#             db.session.add(item)
#             db.session.commit()
#
#         db.session.add(select_member_info)
#         db.session.commit()
#     return jsonify(resp)