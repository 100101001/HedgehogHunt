#!/usr/bin/python3.6.8
# Editor weichaoxu

# -*- coding:utf-8 -*-
from web.controllers.api import route_api
from flask import request, jsonify, g
from application import app, db
from common.libs.Helper import getCurrentDate
from common.models.ciwei.User import User
from common.models.ciwei.Member import Member




@route_api.route("/user/get-user", methods=['GET', 'POST'])
def getUserList():
    resp = {'code': 200, 'msg': 'getuser successfully(user/get-user)', 'data': {}}

    member_info = g.member_info
    if not member_info:
        resp['code'] = -1
        resp['msg'] = "用户信息异常"
        return jsonify(resp)

    user_list = User.query.order_by(User.level.asc()).all()
    data_user_list = []
    if user_list:
        for item in user_list:
            tmp_data = {
                "uid": item.uid,
                "name": item.name,
                "level": item.level,
                "mobile": item.mobile,
                "email": item.email,
                "status": item.status,
                "member_id": item.member_id,
            }
            data_user_list.append(tmp_data)

    resp['user_list'] = data_user_list
    return jsonify(resp)


@route_api.route("/user/delete", methods=['GET', 'POST'])
def deleteUser():
    resp = {'code': 200, 'msg': 'delete successfully(user/delete)', 'data': {}}
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
        return jsonify(resp)

    user_info = User.query.filter_by(uid=uid).first()
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
        resp['data'] = req
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
