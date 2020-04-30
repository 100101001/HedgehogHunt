# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/4/24 下午6:43
@file: Feedback.py
@desc:
"""
from flask import request, jsonify, g

from application import db, APP_CONSTANTS
from common.admin.FeedbackService import FeedbackHandler
from common.libs.Helper import param_getter
from common.libs.UrlManager import UrlManager
from common.models.ciwei.Feedback import Feedback
from web.controllers.api import route_api


@route_api.route("/feedback/create", methods=['GET', 'POST'])
def createFeedback():
    """
    预创建反馈
    :return:反馈id和uuid
    """
    resp = {'code': -1, 'msg': '', 'data': {}}
    req = request.values

    # 检查登陆
    # 检查参数: 描述summary
    member_info = g.member_info
    if not member_info:
        resp['msg'] = "请先登录"
        return resp
    summary = req.get('summary', '')
    if not summary:
        resp['msg'] = "请填写反馈内容"
        return resp
    feedback = FeedbackHandler.deal('init', author_info=member_info, summary=summary,
                                    has_img=int(req.get('has_img', 0)))
    db.session.flush()
    resp['data']['id'] = feedback.id
    db.session.commit()
    resp['code'] = 200
    return jsonify(resp)


@route_api.route("/feedback/add-pics", methods=['GET', 'POST'])
def addFeedbackPics():
    """
    上传反馈图片
    :return:成功
    """
    resp = {'code': -1, 'msg': ''}

    # 检查登陆
    # 检查参数：反馈id, 图片文件image
    req = request.values
    member_info = g.member_info
    if not member_info:
        resp['msg'] = "请先登录"
        return resp
    feedback_id = req.get('id')
    if not feedback_id:
        resp['msg'] = "上传失败"
        return jsonify(resp)
    image = request.files.get('file')
    if image is None:
        return resp
    op_res = FeedbackHandler.deal('addImage', total=int(req.get('total', 0)), feedback_id=feedback_id, image=image)
    db.session.commit()
    resp['code'] = 200 if op_res else -1
    return resp


# 查询所有举报信息
@route_api.route("/feedback/search", methods=['GET', 'POST'])
def feedbackSearch():
    """
    按status获取一页反馈
    :return: 分页的反馈,是否还有更多页
    """

    resp = {'code': -1, 'msg': '', 'data': {}}
    req = request.values

    # 检查登陆
    # 检查参数：反馈status
    member_info = g.member_info
    if not member_info:
        resp['msg'] = "请先登录"
        return resp

    feedbacks, user_id = FeedbackHandler.deal('search',
                                              # 管理员权限
                                              member_id=member_info.id,
                                              # 分页
                                              p=int(req.get('p', 1)), order_rule=Feedback.id.desc())
    feedback_data = []
    if feedbacks:
        for item in feedbacks:
            views = item.views.split(',')
            tmp_data = {
                "id": item.id,
                "member_id": item.member_id,
                "avatar": item.avatar,
                "nickname": item.nickname,
                "created_time": str(item.created_time),
                "pics": [UrlManager.buildImageUrl(i) for i in item.pics.split(',')],
                "status": item.status,
                "summary": item.summary,
                "views": views,
                "viewed": user_id in views
            }
            feedback_data.append(tmp_data)

    # 所有反馈,是否还有更多
    resp['code'] = 200
    resp['data'] = {
        'list': feedback_data,
        'user_id': user_id,
        'has_more': len(feedback_data) >= APP_CONSTANTS['page_size']
    }
    return jsonify(resp)


@route_api.route('/feedback/status/set', methods=['GET', 'POST'])
def feedbackStatusSet():
    """
    已读反馈和删除反馈
    :return:
    """
    resp = {'code': -1, 'msg': '', 'data': {}}
    req = request.values

    # 检查登陆
    # 检查参数：反馈id,反馈发布者auther_info
    member_info = g.member_info
    if not member_info:
        resp['msg'] = "请先登录"
        return resp

    del_ids = param_getter['ids'](req.get('del_ids', None))
    read_ids = param_getter['ids'](req.get('read_ids', None))

    FeedbackHandler.deal('delOrRead', member_id=member_info.id,
                         read_ids=read_ids, del_ids=del_ids)
    db.session.commit()
    resp['code'] = 200
    return resp
