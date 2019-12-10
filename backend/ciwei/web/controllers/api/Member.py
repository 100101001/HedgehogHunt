#!/usr/bin/python3.6.8
# Editor weichaoxu

# -*- coding:utf-8 -*-
from flask import Response
from common.models.ciwei.QrCode import QrCode
from web.controllers.api import route_api
from flask import request, jsonify, g
from application import app, db
import requests
import base64
import json
from common.models.ciwei.Member import Member
from common.models.ciwei.User import User
from common.libs.Helper import getCurrentDate
from common.libs.MemberService import MemberService
from common.libs.UrlManager import UrlManager
from common.libs.UploadService import UploadService
from common.models.ciwei.Goods import Good
from common.models.ciwei.Thanks import Thank
import time

@route_api.route("/member/login", methods=['GET', 'POST'])
def login():
    resp = {'code': 200, 'msg': 'login successfully(login)', 'data': {}}
    req = request.values

    code = req['code'] if 'code' in req else ''
    if not code or len(code) < 1:
        resp['code'] = -1
        resp['msg'] = "need code"
        return jsonify(resp)

    openid = MemberService.getWeChatOpenId(code)
    if openid is None:
        resp['code'] = -1
        resp['msg'] = "call wechat error "
        return jsonify(resp)

    nickname = req['nickName'] if 'nickName' in req else ''
    sex = req['gender'] if 'gender' in req else 0
    avatar = req['avatarUrl'] if 'avatarUrl' in req else ''
    '''
    判断是否已经注册过，注册了直接返回一些信息即可
    '''
    member_info = Member.query.filter_by(openid=openid, status=1).first()
    if not member_info:
        model_member = Member()
        model_member.nickname = nickname
        model_member.sex = sex
        model_member.avatar = avatar
        # model_member.updated_time = model_member.created_time = getCurrentDate()
        model_member.openid = openid
        db.session.add(model_member)
        db.session.commit()
        member_info = model_member
    token = "%s#%s" % (openid, member_info.id)
    resp['data'] = {'token': token}
    resp['req'] = req
    return jsonify(resp)

@route_api.route("/member/check-reg", methods=['GET', 'POST'])
def checkReg():
    resp = {'code': 200, 'msg': 'login successfully(check-reg)', 'data': {}}
    req = request.values

    code = req['code'] if 'code' in req else ''
    if not code or len(code) < 1:
        resp['code'] = -1
        resp['msg'] = "need code(check-reg)"
        return jsonify(resp)

    openid = MemberService.getWeChatOpenId(code)
    if openid is None:
        resp['code'] = -1
        resp['msg'] = "call wechat error"
        return jsonify(resp)

    member_info = Member.query.filter_by(openid=openid).first()
    if not member_info:
        resp['code'] = -1
        resp['member_status'] = -2
        resp['msg'] = "binding information not queried"
        return jsonify(resp)

    # 查询是否是管理员
    is_adm = False
    is_user = False
    has_qrcode = False
    user_info = User.query.filter_by(member_id=member_info.id).first()
    if user_info:
        if user_info.level == 1:
            is_adm = True
            is_user = True
        elif user_info.level > 1:
            is_user = True

    # 济人济市的openid if openid=="o9zh35M5dMt3SUeUcUcbASOLaZIQ":
    # uni-济旦财的openid if openid=="o1w1e5egBOLj5SjvPkNIsA3jpZFI":
    if openid == "o9zh35M5dMt3SUeUcUcbASOLaZIQ":
        is_adm = True
        is_user = True

    if member_info.qr_code:
        qr_code_url = UrlManager.buildImageUrl(member_info.qr_code)
        qr_code_list = [qr_code_url]
        has_qrcode = True
    else:
        qr_code_list = []

    token = "%s#%s" % (openid, member_info.id)
    resp['data'] = {
        'token': token,
        'is_adm': is_adm,
        'is_user': is_user,
        'has_qrcode': has_qrcode,
        'qr_code_list': qr_code_list,
        'member_status': member_info.status,
        'id': member_info.id,
    }
    return jsonify(resp)

@route_api.route("/member/info")
def memberInfo():
    resp = {'code': 200, 'msg': 'get_member_info successfully(share)', 'data': {}}

    member_info = g.member_info
    if not member_info:
        resp['code'] = -1
        resp['msg'] = "没有相关用户信息"
        return jsonify(resp)

    has_qrcode = False
    if member_info.qr_code:
        qr_code_url = UrlManager.buildImageUrl(member_info.qr_code)
        qr_code_list = [qr_code_url]
        has_qrcode = True
    else:
        qr_code_list = []
    resp['data']['info'] = {
        'nickname': member_info.nickname,
        'avatar_url': member_info.avatar,
        'qr_code_list': qr_code_list,
        'member_id': member_info.id,
        "credits": member_info.credits,
        "has_qrcode": has_qrcode
    }
    return jsonify(resp)

@route_api.route("/member/get-new-recommend")
def getNewRecommend():
    resp = {'code': 200, 'msg': 'get_member_info successfully(share)', 'data': {}}

    member_info = g.member_info
    if not member_info:
        resp['code'] = -1
        resp['msg'] = "没有相关用户信息"
        return jsonify(resp)
    #都先置零
    recommend_status_2=recommend_status_3=recommend_status_1=0
    recommend_new=thanks_new=0
    if member_info.recommend_id:
        recommend_dict=MemberService.getRecommendDict(member_info.recommend_id,True)
        query=Good.query.filter(Good.id.in_(recommend_dict.keys()))
        recommend_status_1=len(query.filter_by(status=1).all())
        recommend_status_2=len(query.filter_by(status=2).all())
        recommend_status_3=len(query.filter_by(status=3).all())
        recommend_new=len(recommend_dict) if len(recommend_dict)<=99 else 99

    #未读的答谢记录
    query=Thank.query.filter_by(member_id=member_info.id)
    thanks_list=query.filter_by(status=0).all()
    if thanks_list:
        thanks_new=len(thanks_list) if len(thanks_list)<=99 else 99

    total_new=recommend_new+thanks_new
    total_new=total_new if total_new<=99 else 99

    resp['data']= {
        'total_new': total_new,
        'recommend_new': recommend_new,
        'thanks_new': thanks_new,
        'recommend':{
            'wait':recommend_status_1 if recommend_status_1<=99 else 99,
            'doing':recommend_status_2 if recommend_status_2<=99 else 99,
            'done':recommend_status_3 if recommend_status_3<=99 else 99,
        }
    }
    return jsonify(resp)

@route_api.route("/member/add-qrcode", methods=['GET', 'POST'])
def addQrcode():
    resp = {'code': 200, 'state': 'add qrcode success', 'data': {}}

    member_info = g.member_info
    if not member_info:
        resp['code'] = -1
        resp['msg'] = "用户信息异常"
        return jsonify(resp)

    # 是否修改了二维码
    images_target = request.files
    image = images_target['file'] if 'file' in images_target else None

    if image is None:
        resp['code'] = -1
        resp['msg'] = "图片上传失败"
        resp['state'] = '上传失败'
        return jsonify(resp)

    ret = UploadService.uploadByFile(image)
    if ret['code'] != 200:
        resp['code'] = -1
        resp['msg'] = "图片上传失败"
        resp['state'] = "上传失败" + ret['msg']
        return jsonify(resp)

    # 将返回的本地链接加到列表，并且保存为字符串
    pic_url = ret['data']['file_key']
    member_info.qr_code = pic_url
    member_info.updated_time = getCurrentDate()
    db.session.add(member_info)
    db.session.commit()
    resp['msg'] = "change qr_code successfully"
    return jsonify(resp)

@route_api.route("/member/block-search", methods=['GET', 'POST'])
def blockMemberSearch():
    resp = {'code': 200, 'msg': 'search record successfully(search)', 'data': {}}
    req = request.values

    member_info = g.member_info
    if not member_info:
        resp['code'] = -1
        resp['msg'] = "用户信息异常"
        return jsonify(resp)

    p = int(req['p']) if ('p' in req and req['p']) else 1
    if p < 1:
        p = 1
    page_size = 10
    offset = (p - 1) * page_size

    status = int(req['status']) if 'status' in req else "nonono"
    query = Member.query.filter_by(status=status)
    member_list = query.order_by(Member.updated_time.desc()).offset(offset).limit(10).all()
    data_member_list = []

    if member_list:
        for item in member_list:
            tmp_data = {
                "id": item.id,
                "created_time": str(item.created_time),
                "updated_time": str(item.updated_time),
                "status": item.status,
                # 用户信息
                "member_id": item.id,
                "auther_name": item.nickname + "#####@id:" + str(item.id),
                "avatar": item.avatar,
            }
            # 如果已经被处理过
            data_member_list.append(tmp_data)

    resp['data']['list'] = data_member_list
    resp['data']['has_more'] = 0 if len(data_member_list) < page_size else 1
    return jsonify(resp)

# 恢复会员
@route_api.route('/member/restore-member')
def restoreMember():
    resp = {'code': 200, 'msg': 'operate successfully(get info)', 'data': {}}
    req = request.values

    select_member_id = int(req['id']) if ('id' in req and req['id']) else 0
    select_member_info = Member.query.filter_by(id=select_member_id).first()
    select_member_info.status = 1

    # 该用户下正常的账户
    goods_list = Good.query.filter(Good.member_id == select_member_id, Good.status == 8).all()
    for item in goods_list:
        item.status = 1
        item.updated_time = getCurrentDate()
        db.session.add(item)
        db.session.commit()

    select_member_info.updated_time = getCurrentDate()
    db.session.add(select_member_info)
    db.session.commit()

    return jsonify(resp)

@route_api.route('/member/share')
def memberShare():
    resp = {'code': 200, 'msg': 'operate successfully(get info)', 'data': {}}
    member_info = g.member_info
    if not member_info:
        resp['code'] = -1
        resp['msg'] = "用户信息异常"
        return jsonify(resp)

    member_info.credits = member_info.credits + 5
    member_info.updated_time = getCurrentDate()

    db.session.add(member_info)
    db.session.commit()

    return jsonify(resp)
