"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/2/16 下午7:39
@file: Report.py
@desc:
"""
from flask import request, jsonify, g

from application import APP_CONSTANTS, db
from common.admin.ReportService import ReportHandlers, ReportRecordMakers
from common.cahce.GoodsCasUtil import GoodsCasUtil
from common.libs.Helper import param_getter
from common.libs.RecordService import RecordHandlers
from common.loggin.time import time_log
from common.models.ciwei.Goods import Good
from common.models.ciwei.Member import Member
from common.models.ciwei.admin.Report import Report
from common.models.ciwei.Thanks import Thank
from web.controllers.api import route_api


@route_api.route("/report/goods", methods=['GET', 'POST'])
@time_log
def reportGoods():
    """
    举报物品/答谢
    :return: 成功
    """
    resp = {'code': -1, 'msg': '举报成功', 'data': {}}
    req = request.values

    # 检查登陆
    # 检查参数：举报id, 举报类型record_type
    member_info = g.member_info
    if not member_info:
        resp['msg'] = '没有用户信息，无法完成举报！请授权登录'
        return jsonify(resp)
    goods_id = int(req.get('id', -1))
    status = int(req.get('status', -1))  # 用户视图中以为的状态
    if goods_id == -1 or status == -1:
        resp['msg'] = "举报失败"
        return jsonify(resp)
    # 物品信息已有了违规标记
    reporting_goods = Good.query.filter_by(id=goods_id).first()
    if reporting_goods.report_status != 0:
        resp['msg'] = "该条信息已被举报过，管理员处理中"
        return resp

    if not GoodsCasUtil.exec_wrap(goods_id, ['nil', status], -status):  # 用户视图中以为的状态正确，进入critical op 区
        resp['msg'] = "操作冲突，请稍后重试"
        return resp

    # 物品举报标记
    ReportHandlers.get('goods').deal(1, reporting_goods=reporting_goods, reporting_member=member_info)
    db.session.commit()
    GoodsCasUtil.exec(goods_id, -status, status)  # 解锁
    resp['code'] = 200
    return jsonify(resp)


@route_api.route("/report/thanks", methods=['GET', 'POST'])
@time_log
def reportThanks():
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

    ReportHandlers.get('thanks').deal(1, reporting_thanks=reporting_thank, reporting_member=member_info)
    db.session.commit()
    resp['code'] = 200
    return jsonify(resp)


@route_api.route('/report/goods/info')
def reportGoodsInfo():
    """
    管理员进入被举报的帖子查看详情
    :return:
    """
    resp = {'code': 200, 'msg': '', 'data': {}}
    if not g.member_info:
        resp['msg'] = "请先登录"
        return resp
    req = request.values  # 取出参数
    goods_id = int(req.get('id', -1))
    if goods_id == -1:
        resp['msg'] = "加载失败"
        return resp
    # 获取举报和物品信息
    reported_goods = Good.query.join(Report, Good.id == Report.record_id).add_entity(Report).filter(
        Good.id == goods_id).first()

    info, reporter = ReportRecordMakers.get('goods_detail')(reported_goods=reported_goods)
    resp['data'] = {
        'info': info,
        'report_auth_info': reporter
    }
    return resp


@route_api.route("/report/goods/search", methods=['GET', 'POST'])
def reportGoodsSearch():
    """
    管理员获取物品举报记录
    :return:
    """
    resp = {'code': -1, 'msg': '获取失败', 'data': {}}
    req = request.values
    p = int(req.get('p', 1))
    status = int(req.get('status', -1))  # 举报的状态
    if status not in (1, 2, 3, 4, 5):
        return resp

    reported_goods = RecordHandlers.get('goods').search().deal(op_status=4,
                                                               report_status=status,
                                                               owner_name=req.get('owner_name'),
                                                               goods_name=req.get('mix_kw'),
                                                               p=p,
                                                               order_rule=Good.id.desc())
    reported_goods_records = []
    if reported_goods:
        for item in reported_goods:
            goods = ReportRecordMakers.get('goods_record')(reported_goods=item)
            reported_goods_records.append(goods)
    resp['code'] = 200
    resp['data']['list'] = reported_goods_records
    resp['data']['has_more'] = len(reported_goods_records) >= APP_CONSTANTS['page_size'] and p < APP_CONSTANTS[
        'max_pages_allowed']  # 由于深度分页的性能问题，限制页数(鼓励使用更好的搜索条件获取较少的数据量)
    return jsonify(resp)


@route_api.route("/report/thanks/search", methods=['GET', 'POST'])
@time_log
def reportThankSearch():
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

    reported_thanks = RecordHandlers.get('thanks').search().deal(2, report_status=report_status,
                                                                 # 搜索,分页,排序
                                                                 owner_name=req.get('owner_name'),
                                                                 goods_name=req.get('mix_kw'),
                                                                 p=int(req.get('p', 1)),
                                                                 order_rule=Report.id.desc())

    reported_thank_records = []
    if reported_thanks:
        for reported_thank in reported_thanks:
            reported_thank_record = ReportRecordMakers.get('thanks')(reported_thank=reported_thank)
            reported_thank_records.append(reported_thank_record)

    resp['code'] = 200
    resp['data']['list'] = reported_thank_records
    resp['data']['has_more'] = len(reported_thank_records) >= APP_CONSTANTS['page_size']
    return jsonify(resp)


@route_api.route('/report/goods/deal')
def reportGoodsDeal():
    """
    拉黑举报者2/发布者3/无违规4
    :return:
    """
    resp = {'code': -1, 'msg': '操作失败', 'data': {}}
    member_info = g.member_info  # 登录检查
    if not member_info:
        resp['msg'] = "请管理员先登录"
        return resp
    req = request.values
    report_status = int(req.get('report_status', -1))
    goods_id = int(req.get('id', -1))
    if goods_id == -1 or report_status not in (2, 3, 4, 5):
        resp['msg'] = "操作失败"
        return resp
    op_res, op_msg = ReportHandlers.get('goods').deal(report_status, goods_id=goods_id, member_id=member_info.id)
    db.session.commit()
    resp['code'] = 200 if op_res else -1
    resp['msg'] = op_msg
    return jsonify(resp)


@route_api.route('/report/thanks/deal')
@time_log
def reportThanksDeal():
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
    thank_id = int(req.get('thank_id', -1))
    if thank_id == -1 or report_status not in (2, 3, 4, 5):
        resp['msg'] = '操作失败'
        return resp
    op_res, op_msg = ReportHandlers.get('thanks').deal(report_status, thank_id=thank_id, member_id=member_info.id)
    db.session.commit()
    resp['code'] = 200 if op_res else -1
    resp['msg'] = op_msg
    return resp


@route_api.route('/report/goods/delete', methods=['GET', 'POST'])
def reportGoodsDelete():
    resp = {'code': -1, 'msg': '', 'data': {}}
    req = request.values
    # 检查登陆
    member_info = g.member_info
    if not member_info:
        resp['msg'] = "请先登陆"
        return resp
    """
    op_status=4, 物品举报
    """
    op_status = int(req.get('op_status', -1))
    if op_status != 4:
        resp['msg'] = "操作失败"
        return resp
    id_list = param_getter['ids'](req.get('id_list', None))
    op_res, op_msg = RecordHandlers.get('goods').delete().deal(op_status,
                                                               goods_ids=id_list,
                                                               # 管理员权限信息
                                                               member_id=member_info.id,
                                                               level=1)
    resp['code'] = 200 if op_res else -1
    resp['msg'] = op_msg
    return resp



@route_api.route("/report/thanks/delete", methods=['GET', 'POST'])
@time_log
def reportThanksDelete():
    """
    删除自己收到和发出的答谢记录
    删除答谢举报
    :return:
    """
    resp = {'code': -1, 'msg': '', 'data': {}}
    member_info = g.member_info
    if not member_info:
        resp['msg'] = "请先登录"
        return resp
    req = request.values
    """
    op_status=4,答谢举报
    """
    op_status = int(req.get('op_status', -1))
    if op_status != 4:
        resp['msg'] = "操作失败"
        return resp

    id_list = param_getter['ids'](req.get('id_list', None))
    op_res, op_msg = RecordHandlers.get('thanks').delete().deal(op_status=op_status,
                                                                thank_ids=id_list,
                                                                # 管理员身份审核信息
                                                                member_id=member_info.id,
                                                                level=1)
    resp['code'] = 200 if op_res else -1
    resp['msg'] = op_msg
    return resp



@route_api.route("/member/blocked/search", methods=['GET', 'POST'])
@time_log
def memberBlockedSearch():
    """
    获取封号的会员
    :return: 状态为status的用户信息列表
    """

    resp = {'code': -1, 'msg': '', 'data': {}}
    req = request.values

    # 检查登陆
    member_info = g.member_info
    if not member_info:
        resp['msg'] = "请先登录"
        return resp

    p = max(int(req.get('p', 1)), 1)
    page_size = APP_CONSTANTS['page_size']
    offset = (p - 1) * page_size
    blocked_members = Member.query.filter(Member.status.in_([0, -1])).order_by(Member.updated_time.desc()).offset(
        offset).limit(page_size).all()

    # models -> objects
    # 用户信息列表
    data_member_list = []
    if blocked_members:
        for member in blocked_members:
            tmp_data = {
                "user_id": member.user_id,
                "created_time": str(member.created_time),
                "updated_time": str(member.updated_time),
                "status": member.status,
                # 用户信息
                "id": member.id,
                "name": member.nickname,
                "avatar": member.avatar
            }
            data_member_list.append(tmp_data)

    resp['code'] = 200
    resp['data']['list'] = data_member_list
    resp['data']['has_more'] = len(data_member_list) >= page_size and p < APP_CONSTANTS[
        'max_pages_allowed']  # 由于深度分页的性能问题，限制页数(鼓励使用更好的搜索条件获取较少的数据量)
    return resp
