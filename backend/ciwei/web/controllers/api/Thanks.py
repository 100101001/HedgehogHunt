# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/2/10 下午1:52
@file: Thanks.py
@desc: 答谢接口
"""
import datetime
from _pydecimal import Decimal

from flask import request, jsonify, g

from application import app, db, APP_CONSTANTS
from common.libs import ThanksService
from common.libs.Helper import param_getter, queryToDict
from common.libs.RecordService import RecordHandlers
from common.libs.mall.PayService import PayService
from common.libs.mall.WechatService import WeChatService
from common.loggin.time import time_log
from common.models.ciwei.ThankOrder import ThankOrder
from common.models.ciwei.Thanks import Thank
from common.tasks.subscribe import SubscribeTasks
from web.controllers.api import route_api


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
        business_type = int(req.get('business_type', 0))
        if business_type == 1:
            # 帖子和认领记录一起更新
            ThanksService.updateThankedFoundStatus(found_id=thank_model.goods_id, send_member_id=member_info.id)
        elif business_type == 2:
            # 归还和寻物帖子一起更新
            ThanksService.updateThankedReturnStatus(return_id=thank_model.goods_id)
        thanks_info = queryToDict(thank_model)
        db.session.commit()
        resp['code'] = 200
    except Exception as e:
        app.logger.error('{0}: {1}'.format(request.path, str(e)))
        db.session.rollback()
        resp = {'code': -1, 'msg': '服务异常, 涉及交易请立刻联系技术支持', 'data': {}}
        return resp
    try:
        # 即使发生了异常也不会影响已经支付答谢过的
        SubscribeTasks.send_thank_subscribe.delay(thank_info=thanks_info)
    except Exception as e:
        app.logger.error('{0}: {1}'.format(request.path, str(e)))
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
                                                        only_new=req.get(
                                                            'only_new') == 'true',
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


@route_api.route("/thanks/read", methods=['GET', 'POST'])
@time_log
def thankStatusUpdate():
    """
    退出页面时，自动更新答谢为已读
    :return:
    """
    member_info = g.member_info
    if not member_info:
        return ""
    Thank.query.filter_by(target_member_id=member_info.id, status=0).update({'status': 1}, synchronize_session=False)
    db.session.commit()
    return ""


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


@route_api.route("/thank/order", methods=['POST', 'GET'])
def createThankOrder():
    resp = {'code': -1, 'msg': 'success', 'data': {}}
    req = request.values
    member_info = g.member_info
    if not member_info:
        resp['msg'] = "请先登录"
        return jsonify(resp)
    price = Decimal(req.get('price', '0')).quantize(Decimal('0.00'))
    if not price:
        resp['msg'] = "支付失败"
        return jsonify(resp)

    # 数据库下单
    wechat_service = WeChatService(merchant_key=app.config['OPENCS_APP']['mch_key'])
    pay_service = PayService()
    model_order = ThankOrder()
    model_order.order_sn = pay_service.geneThankOrderSn()
    model_order.openid = member_info.openid
    model_order.member_id = member_info.id
    model_order.price = price
    model_order.balance_discount = Decimal(req.get('discount', '0')).quantize(Decimal('0.00'))
    order_sn = model_order.order_sn
    # 微信下单
    pay_data = {
        'appid': app.config['OPENCS_APP']['appid'],
        'mch_id': app.config['OPENCS_APP']['mch_id'],
        'nonce_str': wechat_service.get_nonce_str(),
        'body': '闪寻-答谢',
        'out_trade_no': order_sn,
        'total_fee': int(model_order.price * 100),
        'notify_url': app.config['APP']['domain'] + "/api/thank/order/notify",
        'time_expire': (datetime.datetime.now() + datetime.timedelta(minutes=5)).strftime("%Y%m%d%H%M%S"),
        'trade_type': 'JSAPI',
        'openid': member_info.openid
    }
    pay_sign_data = wechat_service.get_pay_info(pay_data=pay_data)
    if not pay_sign_data:
        resp['msg'] = "微信服务器繁忙，请稍后重试"
        return jsonify(resp)
    model_order.status = 0
    db.session.add(model_order)
    db.session.commit()
    resp['code'] = 200
    resp['data'] = pay_sign_data
    resp['data']['thank_order_sn'] = order_sn
    return jsonify(resp)


@route_api.route('/thank/order/notify', methods=['GET', 'POST'])
def thankOrderCallback():
    """
    支付回调
    :return:
    """

    result_data = {
        'return_code': 'SUCCESS',
        'return_msg': 'OK'
    }
    header = {'Content-Type': 'application/xml'}
    app_config = app.config['OPENCS_APP']
    target_wechat = WeChatService(merchant_key=app_config['mch_key'])
    callback_data = target_wechat.xml_to_dict(request.data)
    app.logger.info(callback_data)

    # 检查签名和订单金额
    sign = callback_data['sign']
    callback_data.pop('sign')
    gene_sign = target_wechat.create_sign(callback_data)
    app.logger.info(gene_sign)
    if sign != gene_sign:
        result_data['return_code'] = result_data['return_msg'] = 'FAIL'
        return target_wechat.dict_to_xml(result_data), header
    if callback_data['result_code'] != 'SUCCESS':
        result_data['return_code'] = result_data['return_msg'] = 'FAIL'
        return target_wechat.dict_to_xml(result_data), header

    order_sn = callback_data['out_trade_no']
    thank_order_info = ThankOrder.query.filter_by(order_sn=order_sn).first()
    if not thank_order_info:
        result_data['return_code'] = result_data['return_msg'] = 'FAIL'
        return target_wechat.dict_to_xml(result_data), header

    if int(thank_order_info.price * 100) != int(callback_data['total_fee']):
        result_data['return_code'] = result_data['return_msg'] = 'FAIL'
        return target_wechat.dict_to_xml(result_data), header

    # 更新订单的支付状态, 记录日志

    # 订单状态已回调更新过直接返回
    if thank_order_info.status == 1:
        return target_wechat.dict_to_xml(result_data), header
    # 订单状态未回调更新过
    target_pay = PayService()
    target_pay.thankOrderSuccess(thank_order_id=thank_order_info.id, params={"pay_sn": callback_data['transaction_id'],
                                                                             "paid_time": callback_data['time_end']})
    target_pay.addThankPayCallbackData(thank_order_id=thank_order_info.id, data=request.data)
    return target_wechat.dict_to_xml(result_data), header
