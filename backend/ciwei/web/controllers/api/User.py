# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/4/20 下午7:29
@file: User.py
@desc: 
"""
import operator

from flask import request, jsonify, g

from common.libs import UserService
from common.loggin.decorators import time_log
from common.models.ciwei.Member import Member
from web.controllers.api import route_api


@route_api.route("/user/get-user", methods=['GET', 'POST'])
@time_log
def getUserList():
    """
    获取添加的管理员列表
    :return:
    """
    resp = {'code': -1, 'msg': '', 'data': {}}

    member_info = g.member_info
    if not member_info:
        resp['msg'] = "请先登录"
        return jsonify(resp)

    users = UserService.getAllUsers()
    # ----排序操作 (按level排序)
    users.sort(key=operator.attrgetter('level'))
    # ----排序操作
    user_list = []
    if users:
        for u in users:
            tmp_data = {
                "uid": u.uid,
                "member_id": u.member_id,
                "name": u.name,
                "level": u.level,
                "mobile": u.mobile,
                "email": u.email,
                "status": u.status,
            }
            user_list.append(tmp_data)

    resp['user_list'] = user_list
    resp['code'] = 200
    return jsonify(resp)


@route_api.route("/user/register", methods=['GET', 'POST'])
@time_log
def userRegister():
    """
    添加管理员（）
    :return:
    """
    resp = {'code': -1, 'msg': '添加成功', 'data': {}}
    req = request.values
    member_info = g.member_info
    if not member_info:
        resp['msg'] = "请先登录"
        return jsonify(resp)
    member_id = int(req.get('member_id', -1))
    if  member_id == -1:
        resp['msg'] = "添加失败"
        return jsonify(resp)
    reg_member_info = Member.query.filter_by(id=member_id).first()
    if not reg_member_info:
        resp['msg'] = "添加失败，没有该用户"
        return jsonify(resp)

    UserService.addNewUser(user_info=req, member_info=reg_member_info)
    resp['code'] = 200
    return jsonify(resp)



