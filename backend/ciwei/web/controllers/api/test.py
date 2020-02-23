#!/usr/bin/python3.6.8
# Editor weichaoxu

# -*- coding:utf-8 -*-
from application import app, db
from flask import jsonify
from common.models.ciwei.Member import Member
from common.libs.Helper import getCurrentDate
from web.controllers.api import route_api


@route_api.route("/member/create", methods=['GET', 'POST'])
def memberCreate():
    app_config = app.config
    image_root = app_config['APP']['domain'] + app_config['UPLOAD']['prefix_url']
    avatar_list = ["20191017/42726bc15c784ab79941894c87c3b0bd.jpg",
                   "20191017/fc448e06f5414855981cf4adcd2115a1.jpg",
                   "20191017/8a6ac5531b9346e6bca30d84487fcc77.jpg",
                   "20191017/d3e9259f57d9404d85e760ef4fcfdc6d.jpg",
                   "20191018/462054809e3b4a6bb7907180d49f6d31.jpg",
                   "20191018/46353d24acc64b028cdb11940fd1a40a.jpg",
                   "20191018/de77757ba88e487a8384fc45d6869955.jpg",
                   "20191018/edf5229036694feda651410469317364.jpg",
                   "20191018/46749ed5405842589e5541c508179380.jpg",
                   "20191018/df24cccf61514f5a80af69266cfc2b54.jpg",
                   "20191018/f686ecca89db47709387de244f79f87e.jpg",
                   "20191018/73b6fc2647b345f2a9eb7b179f8e8527.jpg"]
    model_member = Member()
    token_list = []
    count = 0
    for i in avatar_list:
        count = count + 1
        name = "July" + "+++" + str(count)
        model_member.nickname = name
        model_member.sex = 1
        avatar = image_root + i
        model_member.avatar = avatar
        model_member.qr_code = image_root + i
        model_member.openid = str(count)
        model_member.updated_time = model_member.created_time = getCurrentDate()
        db.session.add(model_member)
        db.session.commit()

        member_i = Member.query.filter_by(nickname=name).first()
        token = "{0}#{1}".format(member_i.openid, member_i.id)
        token_list.append(token)

    resp = {'token_list': token_list}
    return jsonify(resp)
