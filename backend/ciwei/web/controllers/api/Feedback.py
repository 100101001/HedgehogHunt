#!/usr/bin/python3.6.8

from flask import request, jsonify, g

from application import db
from common.libs.Helper import getCurrentDate
from common.libs.Helper import getUuid
from common.libs.MemberService import MemberService
from common.libs.UploadService import UploadService
from common.libs.UrlManager import UrlManager
from common.models.ciwei.Feedback import Feedback
from common.models.ciwei.Goods import Good
# -*- coding:utf-8 -*-
from common.models.ciwei.Member import Member
from common.models.ciwei.User import User
from web.controllers.api import route_api


@route_api.route("/feedback/create", methods=['GET', 'POST'])
def createFeedback():
    """
    预创建反馈
    :return:反馈id和uuid
    """
    resp = {'code': -1, 'msg': 'create feedback data successfully', 'data': {}}
    req = request.values

    # 检查登陆
    # 检查参数: 描述summary
    member_info = g.member_info
    if not member_info:
        resp['msg'] = "用户信息异常"
        return jsonify(resp)
    summary = req["summary"] if 'summary' in req else ''
    if not summary:
        resp['msg'] = "参数为空"
        resp['data'] = req
        return jsonify(resp)

    # 新增uuid不重复的反馈, 控制提交频率
    model_feedback = Feedback()
    model_feedback.summary = summary
    uuid_now = getUuid()
    record = Feedback.query.filter_by(uu_id=uuid_now).first()
    if record:
        resp['msg'] = "系统繁忙，请稍候重试"
        resp['data'] = req
        return jsonify(resp)
    model_feedback.uu_id = uuid_now
    model_feedback.created_time = model_feedback.updated_time = getCurrentDate()
    model_feedback.member_id = member_info.id
    model_feedback.status = 2
    db.session.add(model_feedback)

    # 反馈成功，用户积分涨5
    MemberService.updateCredits(member_info)

    resp['code'] = 200
    resp['data']['id'] = model_feedback.id
    resp['data']['uuid'] = uuid_now
    return jsonify(resp)


@route_api.route("/feedback/add-pics", methods=['GET', 'POST'])
def addFeedbackPics():
    """
    上传反馈图片
    :return:成功
    """
    resp = {'code': -1, 'state': 'add pics success'}

    # 检查登陆
    # 检查参数：反馈id, 图片文件image
    req = request.values
    member_info = g.member_info
    if not member_info:
        resp['msg'] = "用户信息异常"
        return jsonify(resp)
    feedback_id = req['id'] if 'id' in req else None
    if not feedback_id:
        resp['msg'] = "参数为空"
        resp['req'] = req
        return jsonify(resp)
    images_target = request.files
    image = images_target['file'] if 'file' in images_target else None
    if image is None:
        resp['msg'] = '图片上传失败！'
        resp['state'] = '上传失败'
        return jsonify(resp)
    feedback_info = Feedback.query.filter_by(id=feedback_id).with_for_update().first()
    if not feedback_info:
        resp['msg'] = '参数错误'
        return jsonify(resp)


    # 保存图片到数据库和文件系统
    # 在反馈的pics中加入图片路径: 日期/文件名
    ret = UploadService.uploadByFile(image)
    if ret['code'] != 200:
        resp['msg'] = '图片上传失败！'
        resp['state'] = "上传失败" + ret['msg']
        return jsonify(resp)
    pic_url = ret['data']['file_key']
    if not feedback_info.pics:
        pics_list = []
    else:
        pics_list = feedback_info.pics.split(",")
    pics_list.append(pic_url)
    feedback_info.main_image = pics_list[0]
    feedback_info.pics = ",".join(pics_list)
    db.session.commit()

    resp['code'] = 200
    return jsonify(resp)


@route_api.route("/feedback/end-create", methods=['GET', 'POST'])
def endFeedbackCreate():
    """
    反馈的图片已全部上传,结束创建
    :return:成功
    """
    resp = {'code': -1, 'msg': 'create goods success', 'data': {}}

    # 检查登陆
    # 检查参数：反馈id
    req = request.values
    member_info = g.member_info
    if not member_info:
        resp['msg'] = "用户信息异常"
        return jsonify(resp)
    feedback_id = req['id'] if 'id' in req else None
    if not feedback_id:
        resp['msg'] = "参数为空"
        resp['req'] = req
        return jsonify(resp)
    feedback_info = Feedback.query.filter_by(id=feedback_id).with_for_update().first()
    if not feedback_info:
        resp['msg'] = '没有相关反馈记录'
        return jsonify(resp)

    # id号反馈状态更新1
    feedback_info.status = 1
    feedback_info.updated_time = getCurrentDate()
    db.session.commit()

    resp['code'] = 200
    return jsonify(resp)


# 查询所有举报信息
@route_api.route("/feedback/search", methods=['GET', 'POST'])
def feedbacksSearch():
    """
    按status获取一页反馈
    :return: 分页的反馈,是否还有更多页
    """

    resp = {'code': -1, 'msg': 'search record successfully(search)', 'data': {}}
    req = request.values

    # 检查登陆
    # 检查参数：反馈status
    member_info = g.member_info
    if not member_info:
        resp['msg'] = "用户信息异常"
        return jsonify(resp)
    status = int(req['status']) if 'status' in req else None
    if not status:
        resp['msg'] = '参数为空'
        return jsonify(resp)

    # 按status筛选反馈并分页排序
    # 取需要信息组成对象返回
    p = int(req['p']) if ('p' in req and req['p']) else 1
    if p < 1:
        p = 1
    page_size = 10
    offset = (p - 1) * page_size
    query = Feedback.query.filter_by(status=status)
    feedback_list = query.order_by(Feedback.updated_time.desc()).offset(offset).limit(10).all()
    data_feedback_list = []
    if feedback_list:
        for item in feedback_list:
            tmp_data = {
                "id": item.id,
                "created_time": str(item.created_time),
                "updated_time": str(item.updated_time),
                "main_image": UrlManager.buildImageUrl(item.main_image),
                "status": item.status,
                "summary": item.summary,
            }
            data_feedback_list.append(tmp_data)

    # 所有反馈,是否还有更多
    resp['code'] = 200
    resp['data']['list'] = data_feedback_list
    resp['data']['has_more'] = 0 if len(data_feedback_list) < page_size else 1
    return jsonify(resp)


# 查看举报详情
@route_api.route('/feedback/info')
def feedbackInfo():
    """

    :return:
    """

    resp = {'code': -1, 'msg': 'operate successfully(get info)', 'data': {}}
    req = request.values

    # 检查登陆
    # 检查参数：反馈id,反馈发布者auther_info
    member_info = g.member_info
    if not member_info:
        resp['msg'] = "用户信息异常"
        return jsonify(resp)
    id = int(req['id']) if 'id' in req else None
    if not id:
        resp['msg'] = "参数为空"
        return jsonify(resp)
    feedback_info = Feedback.query.filter_by(id=id).with_for_update().first()
    if not feedback_info:
        resp['msg'] = '参数错误'
        return jsonify(resp)
    auther_info = Member.query.filter_by(id=feedback_info.member_id).first()
    if not auther_info:
        resp['msg'] = '发布者信息缺失'
        return jsonify(resp)

    # 更新反馈已经读过
    # TODO：请求结束是否数据库锁会释放
    if feedback_info.status == 1:
        feedback_info.status = 0
        db.session.commit()

    # 组装需要的信息返回
    resp['code'] = 200
    resp['data']['info'] = {
        "summary": feedback_info.summary,
        "pics": [UrlManager.buildImageUrl(i) for i in feedback_info.pics.split(",")],
        "created_time": str(feedback_info.created_time),
        "updated_time": str(feedback_info.updated_time),
        # 用户信息
        "member_id": auther_info.id,
        "auther_name": auther_info.nickname,
        "avatar": auther_info.avatar,
        "feedback_id": feedback_info.id
    }
    return jsonify(resp)


# 拉黑发布者或者举报者
@route_api.route('/feedback/block')
def feedbackBlock():
    """
    后
    :return:
    """
    resp = {'code': -1, 'msg': 'operate successfully(get info)', 'data': {}}
    req = request.values

    # 检查登陆的是管理员
    # 检查参数：反馈id, 选中锁号的会员id
    member_info = g.member_info
    if not member_info:
        resp['msg'] = "用户信息异常"
        return jsonify(resp)
    select_member_id = int(req['select_member_id']) if 'select_member_id' in req else None
    feedback_id = int(req['feedback_id']) if 'feedback_id' in req else None
    if not select_member_id or not feedback_id:
        resp['msg'] = "参数为空"
        return jsonify(resp)
    user_info = User.query.filter_by(member_id=member_info.id).first()
    if not user_info:
        resp['msg'] = "没有管理员信息"
        resp['data'] = str(member_info.id) + "+" + member_info.name
        return jsonify(resp)
    feedback_info = Feedback.query.filter_by(id=feedback_id).with_for_update().first()
    if not feedback_info:
        resp['msg'] = "参数错误"
        return jsonify(resp)
    select_member_info = Member.query.filter_by(id=select_member_id).with_for_update().first()
    if not select_member_info:
        resp['msg'] = "参数错误"
        return jsonify(resp)

    # 更新反馈者为管理员id
    # 更新会员status为锁号状态,更新该会员曾发布的待物品为封锁态8
    feedback_info.user_id = user_info.uid
    feedback_info.updated_time = getCurrentDate()
    select_member_info.status = 0
    select_member_info.updated_time = getCurrentDate()
    goods_list = Good.query.filter(Good.member_id == select_member_id, Good.status == 1).all()
    for item in goods_list:
        item.status = 8
        item.updated_time = getCurrentDate()

    db.session.commit()

    resp['code'] = 200
    return jsonify(resp)
