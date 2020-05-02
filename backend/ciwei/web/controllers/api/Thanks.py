# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/2/10 下午1:52
@file: Thanks.py
@desc: 答谢接口
"""

from flask import request, jsonify, g

from application import APP_CONSTANTS
from common.libs.Helper import param_getter
from common.libs.RecordService import RecordHandlers
from common.libs.ThanksService import ThankHandler
from common.loggin.time import time_log
from common.models.ciwei.Thanks import Thank
from web.controllers.api import route_api


@route_api.route("/thank/order", methods=['POST', 'GET'])
@time_log
def thankOrderInit():
    resp = {'code': -1, 'msg': '服务繁忙，稍后重试', 'data': {}}
    req = request.values
    member_info = g.member_info
    if not member_info:
        resp['msg'] = "请先登录"
        return resp
    price = req.get('price')
    if not price:
        resp['msg'] = "支付失败"
        return resp

    pay_sign_data = ThankHandler.deal('init_pay', consumer=member_info, price=price, discount=req.get('discount', '0'))
    if not pay_sign_data:
        return resp
    # 数据库下单
    resp['data'] = pay_sign_data
    return resp


@route_api.route('/thank/order/notify', methods=['GET', 'POST'])
def thankOrderCallback():
    """
    支付回调
    :return:
    """
    xml_data, header = ThankHandler.deal('finish_pay', callback_body=request.data)
    return xml_data, header


@route_api.route("/thanks/create", methods=['GET', 'POST'])
@time_log
def thanksCreate():
    """
    新建答谢
    :return:
    """
    # 创建答谢，金额交易。状态更新
    resp = {'code': -1, 'msg': '', 'data': {}}
    member_info = g.member_info
    if not member_info:
        resp['msg'] = "请先登录"
        return resp
    req = request.values
    ThankHandler.deal('create', sender=member_info, gotback_goods=req, thank_info=req)
    resp['code'] = 200
    return resp


@route_api.route("/thanks/search", methods=['GET', 'POST'])
@time_log
def thanksSearch():
    resp = {'code': -1, 'msg': '', 'data': {}}
    # 登录
    member_info = g.member_info
    if not member_info:
        resp['msg'] = "请先登录"
        return jsonify(resp)
    # 参数检查
    req = request.values
    status = int(req.get('status', -1))
    if status not in (0, 1):
        resp['msg'] = '获取失败'
        return resp

    """
    status = 0 我收到的
    status = 1 我发出的
    """
    report_rule = Thank.report_status.in_([0, 1]) if status else Thank.report_status == 0

    thanks = RecordHandlers.get('thanks').search().deal(status,
                                                        member_id=member_info.id,
                                                        only_new=req.get('only_new') == 'true',
                                                        # 搜索，分页，排序
                                                        owner_name=req.get('owner_name'),
                                                        goods_name=req.get('mix_kw'),
                                                        p=int(req.get('p', 1)),
                                                        order_rule=Thank.id.desc(),
                                                        report_rule=report_rule)

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
                "unselectable": item.report_status != 0
            }  # 组装答谢
            thanks_records.append(thank)  #
    resp['data']['list'] = thanks_records
    resp['data']['has_more'] = len(thanks_records) >= APP_CONSTANTS['page_size']
    resp['code'] = 200
    return resp


@route_api.route("/thanks/delete", methods=['GET', 'POST'])
@time_log
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
    op_status=3,答谢记录 -- status = 0 收到的答谢 status=1 发出的答谢
    """
    op_status = int(req.get('op_status', -1))
    id_list = param_getter['ids'](req.get('id_list', None))

    status = int(req.get('status', 0))

    op_res = RecordHandlers.get('thanks').delete().deal(op_status=op_status - status,
                                                        thank_ids=id_list,
                                                        member_id=member_info.id)
    resp['code'] = 200 if op_res else -1
    return resp


@route_api.route("/thanks/read", methods=['GET', 'POST'])
@time_log
def thankRead():
    """
    退出页面时，自动更新答谢为已读
    :return:
    """
    ThankHandler.deal('read', member_info=g.member_info)
    return ""

