#!/usr/bin/python3.6.8
#Editor weichaoxu

# -*- coding:utf-8 -*-
from web.controllers.api import route_api
from flask import request,jsonify,g
from application import app,db
from common.libs.Helper import getCurrentDate
from common.models.ciwei.User import User
from common.models.ciwei.Member import Member

@route_api.route("/user/register",methods=['GET','POST'])
def register():
    resp={'code':200,'msg':'register successfully(user/register)','data':{}}
    req=request.values
    member_info=g.member_info
    if not member_info:
        resp['code']=-1
        resp['msg']="用户信息异常"
        return jsonify(resp)

    name=req["name"] if 'name' in req else ''
    if not name:
        resp['code']=-1
        resp['msg']="data transport failed(user/register)"
        resp['data']=req
        return jsonify(resp)

    #添加管理员时验证是否注册
    member_id=int(req['member_id']) if ('member_id' in req and int(req['member_id'])) else 0
    if member_id==0:
        resp['code'] = -1
        resp['msg'] = "no member(user/register)"
        resp['data'] = req
        return jsonify(resp)

    reg_member_info=Member.query.filter_by(id=member_id).first()
    if not reg_member_info:
        resp['code'] = -1
        resp['msg'] = "没有找到用户信息"
        resp['data'] = req
        return jsonify(resp)

    user_model=User()
    user_model.name=name
    user_model.mobile=req['mobile']
    user_model.email=req['email']
    user_model.level=req['level']
    user_model.updated_time=user_model.created_time=getCurrentDate()
    user_model.sex=member_info.sex
    user_model.avatar=member_info.avatar
    user_model.member_id=req['member_id']

    db.session.add(user_model)
    db.session.commit()

    return jsonify(resp)

@route_api.route("/user/get-user",methods=['GET','POST'])
def getUserList():
    resp = {'code': 200, 'msg': 'getuser successfully(user/get-user)', 'data': {}}

    member_info = g.member_info
    if not member_info:
        resp['code'] = -1
        resp['msg'] = "用户信息异常"
        return jsonify(resp)

    user_list=User.query.order_by(User.level.asc()).all()
    data_user_list=[]
    if user_list:
        for item in user_list:
            tmp_data={
                "uid":item.uid,
                "name":item.name,
                "level":item.level,
                "mobile":item.mobile,
                "email":item.email,
                "status":item.status,
                "member_id":item.member_id,
            }
            data_user_list.append(tmp_data)

    resp['user_list']=data_user_list
    return jsonify(resp)

@route_api.route("/user/delete",methods=['GET','POST'])
def deleteUser():
    resp = {'code': 200, 'msg': 'delete successfully(user/delete)', 'data': {}}
    req=request.values

    member_info = g.member_info
    if not member_info:
        resp['code'] = -1
        resp['msg'] = "用户信息异常"
        return jsonify(resp)

    uid=req['uid'] if 'uid' in req else 0
    if uid==0:
        resp['code']=-1
        resp['msg']="no uid"
        return jsonify(resp)

    user_info=User.query.filter_by(uid=uid).first()
    if not user_info:
        resp['code'] = -1
        resp['msg'] = "没有找到管理员"
        return jsonify(resp)

    db.session.delete(user_info)
    db.session.commit()
    return jsonify(resp)


@route_api.route("/user/restore", methods=['GET', 'POST'])
def restoreUser():
    resp = {'code': 200, 'msg': 'restore successfully(user/restore)', 'data': {}}
    req = request.values

    member_info = g.member_info
    if not member_info:
        resp['code'] = -1
        resp['msg'] = "用户信息异常"
        return jsonify(resp)

    uid = req['uid'] if 'uid' in req else 0
    if uid == 0:
        resp['code'] = -1
        resp['msg'] = "no uid"
        resp['data']=req
        return jsonify(resp)

    user_info = User.query.filter_by(uid=uid).first()
    if not user_info:
        resp['code'] = -1
        resp['msg'] = "no user_info"
        resp['data'] = req
        return jsonify(resp)

    user_info.status = 1
    db.session.add(user_info)
    db.session.commit()
    return jsonify(resp)
