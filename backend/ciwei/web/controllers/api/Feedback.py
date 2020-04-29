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
from common.libs import UserService
from common.libs.Helper import param_getter
from common.libs.MemberService import MemberService
from common.libs.UploadService import UploadService
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

    # 新增uuid不重复的反馈, 控制提交频率
    feedback = Feedback()
    feedback.member_id = member_info.id
    feedback.nickname = member_info.nickname
    feedback.avatar = member_info.avatar
    feedback.summary = summary
    feedback.status = 7 if req.get('has_img', 0) else 1  # 如果有图片暂时为创建结束
    db.session.add(feedback)

    # 反馈成功，用户积分涨5
    MemberService.updateCredits(member_info=member_info)
    db.session.commit()
    resp['code'] = 200
    resp['data']['id'] = feedback.id
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
        return jsonify(resp)
    feedback_id = req.get('id')
    if not feedback_id:
        resp['msg'] = "上传失败"
        return jsonify(resp)
    image = request.files.get('file')
    if image is None:
        return resp
    feedback_info = Feedback.query.filter_by(id=feedback_id).with_for_update().first()
    if not feedback_info:
        return resp

    # 保存图片到数据库和文件系统
    # 在反馈的pics中加入图片路径: 日期/文件名
    ret = UploadService.uploadByFile(image)
    if ret['code'] != 200:
        resp['msg'] = '图片上传失败！'
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
    resp = {'code': -1, 'msg': '', 'data': {}}

    # 检查登陆
    # 检查参数：反馈id
    req = request.values
    member_info = g.member_info
    if not member_info:
        resp['msg'] = "请先登录"
        return resp
    feedback_id = req.get('id')
    if not feedback_id:
        resp['msg'] = "提交失败"
        return resp
    feedback_info = Feedback.query.filter_by(id=int(feedback_id)).with_for_update().first()
    if not feedback_info:
        resp['msg'] = '提交失败'
        return resp

    # id号反馈状态更新1
    feedback_info.status = 1
    db.session.commit()

    resp['code'] = 200
    return jsonify(resp)


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

    p = max(int(req.get('p', 1)), 1)
    page_size = APP_CONSTANTS['page_size']
    offset = (p - 1) * page_size
    feedbacks = Feedback.query.filter_by(status=1).order_by(Feedback.id.desc()). \
        offset(offset).limit(page_size).all()

    user = UserService.getUserByMid(member_info.id)
    if not user:
        resp['msg'] = '您不是管理员，无权查看反馈'
        return resp
    user_id = str(user.uid)
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
    resp['data']['list'] = feedback_data
    resp['data']['user_id'] = user_id
    resp['data']['has_more'] = len(feedback_data) >= page_size
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

    user = UserService.getUserByMid(member_info.id)
    if not user:
        return resp
    user_id = user.uid
    Feedback.query.filter(Feedback.id.in_(read_ids)).update({'views': str(user_id) if not Feedback.views else
    Feedback.views + (',{}'.format(user_id))}, synchronize_session=False)
    if user.level == 1 and del_ids:
        Feedback.query.filter(Feedback.id.in_(del_ids), Feedback.status == 0).update({'status': 7}, synchronize_session=False)
    db.session.commit()
    resp['code'] = 200
    return resp
