# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/2/10 下午1:52
@file: Thanks.py
@desc: 答谢接口
"""

from flask import request, jsonify, g
from sqlalchemy import or_

from application import app, db, APP_CONSTANTS
from common.libs import RecordService, ThanksService
from common.libs.Helper import param_getter, queryToDict
from common.libs.MemberService import MemberService
from common.loggin.decorators import time_log
from common.models.ciwei.Member import Member
from common.models.ciwei.Report import Report
from common.models.ciwei.Thanks import Thank
from common.models.ciwei.User import User
from common.tasks.subscribe import SubscribeTasks
from web.controllers.api import route_api


@route_api.route("/thanks/search", methods=['GET', 'POST'])
@time_log
def thanksSearch():
    resp = {'code': -1, 'msg': 'search thanks successfully(thanks)', 'data': {}}
    # 登录
    member_info = g.member_info
    if not member_info:
        resp['msg'] = "没有相关用户信息"
        return jsonify(resp)
    # 参数检查
    req = request.values
    status = int(req.get('status', -1))
    if status not in (0, 1):
        resp['msg'] = '获取失败'
        return resp

    if status == 0:
        query = RecordService.getMyReceivedThanks(member_id=member_info.id, only_new=req.get('only_new', '') == 'true')
    else:
        query = RecordService.getMySendThanks(member_id=member_info.id, only_new=req.get('only_new', '') == 'true')

    search_rule = RecordService.searchBarFilter(owner_name=req.get('owner_name', ''), goods_name=req.get('mix_kw', ''))
    p = max(int(req.get('p', 1)), 1)
    page_size = 10
    offset = (p - 1) * page_size
    thanks = query.filter(search_rule).order_by(Thank.id.desc()).offset(offset).limit(page_size).all()

    # 将对应的用户信息取出来，组合之后返回
    thanks_records = []
    if thanks:
        for item in thanks:
            # 发出：我感谢的人
            # 收到：感谢我的人
            thank = {
                "id": item.id,  # 返回ID,前端批量删除需要
                "status": item.status,  # 是否已阅
                "goods_name": item.goods_name,  # 答谢的物品名
                "owner_name": item.owner_name,  # 物品的失主
                "updated_time": str(item.updated_time),  # 更新时间
                "business_desc": item.business_desc,  # 答谢物品的类型
                "summary": item.summary,  # 答谢文字
                "reward": str(item.thank_price),  # 答谢金额
                "auther_name": item.nickname,  # 答谢者
                "avatar": item.avatar,  # 答谢者头像
                "selected": False,  # 前端编辑用
            }  # 组装答谢
            thanks_records.append(thank)  #
    resp['data']['list'] = thanks_records
    resp['data']['has_more'] = len(thanks_records) >= page_size
    resp['code'] = 200
    return resp


@route_api.route("/thanks/update-status", methods=['GET', 'POST'])
@time_log
def thankStatusUpdate():
    """
    退出页面时，按用户点击过的状态栏，自动更新答谢为已读
    :return:
    """
    req = request.values
    member_info = g.member_info
    if not member_info:
        return ""
    query = Thank.query.filter(Thank.status.in_([0, 1]))
    is_all = req.get('all', '') == 'true'
    if is_all:
        _rule = or_(Thank.target_member_id == member_info.id, Thank.member_id == member_info.id)
        query = query.filter(_rule)
    else:
        query = query.filter_by(target_member_id=member_info.id)
    query.update({'status': 1}, synchronize_session=False)
    db.session.commit()
    return ""


@route_api.route("/thanks/create", methods=['GET', 'POST'])
@time_log
def thanksCreate():
    """
    新建答谢
    :return:
    """
    # 创建答谢，金额交易。状态更新
    try:
        resp = {'code': -1, 'msg': '', 'data': {}}
        member_info = g.member_info
        if not member_info:
            resp['msg'] = "请先登录"
            return jsonify(resp)
        req = request.values
        thank_model = ThanksService.sendThanksToGoods(send_member=member_info, thanked_goods=req, thank_info=req)
        # 标记goods方便详情帖子获取是否已经答谢过（答谢接口频率低于详情），和记录接口查看已答谢记录
        business_type = req.get('business_type', 0)
        if business_type == 1:
            # 帖子和认领记录一起更新
            ThanksService.updateThankedFoundStatus(found_id=thank_model.goods_id, send_member_id=member_info.id)
        elif business_type == 2:
            # 归还和寻物帖子一起更新
            ThanksService.updateThankedReturnStatus(return_id=thank_model.goods_id)
        db.session.commit()
        resp['code'] = 200
    except Exception as e:
        app.logger.error('{0}: {1}'.format(request.path, str(e)))
        db.session.rollback()
        resp = {'code': -1, 'msg': '服务异常, 涉及交易请立刻联系技术支持', 'data': {}}
        return resp
    try:
        # 即使发生了异常也不会影响已经支付答谢过的
        SubscribeTasks.send_thank_subscribe.delay(thank_info=queryToDict(thank_model))
    except Exception as e:
        app.logger.error('{0}: {1}'.format(request.path, str(e)))
    return resp


# 举报答谢记录
@route_api.route("/thanks/report", methods=['GET', 'POST'])
@time_log
def thanksReport():
    """
    举报物品/答谢
    :return: 成功
    """
    resp = {'code': -1, 'msg': '举报成功', 'data': {}}
    req = request.values

    # 检查登陆
    member_info = g.member_info
    if not member_info:
        resp['msg'] = '没有用户信息，无法完成举报！请授权登录'
        return jsonify(resp)
    thank_id = int(req.get('id', -1))
    if thank_id == -1:
        resp['msg'] = "举报失败"
        return jsonify(resp)
    # 答谢信息违规
    reporting_thank = Thank.query.filter_by(id=thank_id).first()
    if reporting_thank.report_status != 0:
        resp['msg'] = "该条信息已被举报过，管理员处理中"
        return resp

    # 标记举报
    reporting_thank.report_status = 1
    db.session.add(reporting_thank)
    # 新增举报记录
    report = Report()
    report.member_id = reporting_thank.member_id
    # 举报者信息
    report.report_member_id = member_info.id
    report.report_member_nickname = member_info.nickname
    report.report_member_avatar = member_info.avatar
    # 被举报的答谢的链接信息
    report.record_id = thank_id
    report.record_type = 0  # 标识链接的是Thank ID
    db.session.add(report)

    MemberService.updateCredits(member_info=member_info)
    db.session.commit()
    resp['code'] = 200
    return jsonify(resp)


# 查询所有记录
@route_api.route("/thanks/reports/search", methods=['GET', 'POST'])
@time_log
def thanksReportSearch():
    """
    搜出所有被举报的答谢
    :return:
    """
    resp = {'code': -1, 'msg': '', 'data': {}}
    req = request.values

    member_info = g.member_info
    if not member_info:
        resp['msg'] = "请先登录"
        return resp

    # 获取操作值，看用户是查看收到的还是发出的答谢信息
    report_status = int(req.get('report_status', -1))
    if report_status == -1:
        resp['msg'] = "获取失败"
        return resp
    reported_thanks = RecordService.getReportedThanks(report_status=report_status, p=int(req.get('p', 1)))
    # #将对应的用户信息取出来，组合之后返回
    reported_thank_records = []
    if reported_thanks:
        for reported_thank in reported_thanks:
            reported_thank_record = RecordService.makeReportThankRecord(reported_thank=reported_thank)
            reported_thank_records.append(reported_thank_record)

    resp['code'] = 200
    resp['data']['list'] = reported_thank_records
    resp['data']['has_more'] = len(reported_thank_records) >= APP_CONSTANTS['page_size']
    return jsonify(resp)


@route_api.route('/thanks/block')
@time_log
def thanksBlock():
    """
    拉黑答谢的举报者或者发布者
    :return:
    """
    resp = {'code': -1, 'msg': '', 'data': {}}
    req = request.values

    member_info = g.member_info
    if not member_info:
        resp['msg'] = "用户信息异常"
        return jsonify(resp)
    report_status = int(req.get('report_status', -1))
    report_id = int(req.get('report_id', -1))
    if report_id == -1 or report_status not in (2, 3, 4):
        resp['msg'] = '操作失败'
        return resp

    user_info = User.query.filter_by(member_id=member_info.id).first()
    if not user_info:
        resp['msg'] = "您无管理员权限"
        return resp
    # TODO 拉黑这里状态干嘛用的
    report_info = Report.query.filter_by(id=report_id).first()
    thanks_info = Thank.query.filter_by(id=report_info.record_id).first()
    report_info.status = thanks_info.report_status = report_status
    report_info.user_id = thanks_info.user_id = user_info.uid
    db.session.add(report_info)
    db.session.add(thanks_info)
    # TODO:检查 report_status
    if report_status in (2, 3):
        Member.query.filter_by(id=report_info.member_id if report_status == 3 else report_info.report_member_id). \
            update({'status': 0}, synchronize_session=False)
    db.session.commit()
    resp['code'] = 200
    return resp


@route_api.route("/thanks/delete", methods=['GET', 'POST'])
def thanksDelete():
    """
    删除自己收到和发出的答谢记录
    删除答谢举报
    :return:
    """
    resp = {'code': -1, 'msg': '操作失败', 'data': {}}
    member_info = g.member_info
    if not member_info:
        resp['msg'] = "请先登录"
        return resp
    req = request.values
    """
    op_status=4,答谢举报
    op_status=3,答谢记录
    """
    op_status = int(req.get('op_status', -1))
    id_list = param_getter['ids'](req.get('id_list', None))
    op_res = False
    if op_status == 3:
        op_res = RecordService.deleteMyThanks(thank_ids=id_list)
    elif op_status == 4:
        user_info = User.query.filter_by(member_id=member_info.id).first()  # 用户是否是管理员（前端可以传进来）
        if user_info:
            op_res = RecordService.deleteReportedThanks(thank_ids=id_list, user_id=user_info.id)  # 删除
    resp['code'] = 200 if op_res else -1
    return resp
