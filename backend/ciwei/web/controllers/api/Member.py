# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/1/9 上午12:36
@file: Member.py
@desc:
"""

from flask import request, jsonify, g

from common.libs.MemberService import MemberHandler
from common.loggin.time import time_log
from web.controllers.api import route_api



@route_api.route("/member/is-reg", methods=['GET', 'POST'])
@time_log
def memberIsReg():
    resp = {'code': 200, 'msg': '', 'data': {}}
    req = request.values
    resp['data']['is_reg'] = MemberHandler.deal('is_reg', openid=req.get('openid'))
    return resp


@route_api.route("/member/phone/decrypt", methods=['POST', 'GET'])
@time_log
def memberPhoneDecrypt():
    """
    前端获取手机号后，如果能成功解密获取，才能继续注册
    返回前端的数据经过HTTPS加密处理
    :return:
    """
    resp = {'code': -1, 'msg': '已获取手机号', 'data': {}}
    req = request.get_json()
    # 获取加密手机号 # 获取加密向量# 获取秘钥session_key
    encrypted_data, iv, session_key = req.get('encrypted_data'), req.get('iv'), req.get('session_key')
    if not session_key or not iv or not encrypted_data:
        resp['msg'] = "手机号获取失败"
        return resp
    code, data = MemberHandler.deal('init_register', encrypt_mobile=encrypted_data, iv=iv, decrypt_key=session_key)
    if code == -1:
        resp['msg'] = data
        return resp
    resp['code'] = code
    resp['data'] = data
    return resp


@route_api.route("/member/register", methods=['GET', 'POST'])
@time_log
def memberReg():
    """
    会员登陆或注册
    :return: openid#会员id
    """
    resp = {'code': -1, 'msg': '', 'data': {}}
    req = request.values
    res_code, res_data = MemberHandler.deal('register', reg_info=req)
    if res_code == -1:
        resp['msg'] = res_data
        return resp
    resp['data'] = res_data
    resp['code'] = res_code
    return resp


@route_api.route("/member/login", methods=['GET', 'POST'])
@time_log
def memberLogin():
    """
    角色信息
    :return:用户角色,二维码,token,用户状态
    """
    resp = {'code': -1, 'msg': '', 'data': {}}
    req = request.values
    # 检查参数：code
    code, data = MemberHandler.deal('login', code=req.get('code'))
    if code == -1:
        resp['msg'] = data
        return resp
    resp = {'code': code, 'data': data}
    return resp


@route_api.route("/member/simple/info")
@time_log
def memberSimpleInfo():
    """
    用户信息
    :return: 昵称,头像,积分,二维码
    """
    code, data = MemberHandler.deal('basic_info', member=g.member_info)
    resp = {
        'code': code,
        'data': data
    }
    return resp


@route_api.route("/member/info")
@time_log
def memberInfo():
    """
    用户信息
    :return: id,昵称,头像,积分,二维码
    """
    resp = {'code': -1, 'msg': '', 'data': {}}
    member_info = g.member_info
    if not member_info:
        resp['msg'] = "请先登录"
        return resp
    resp['code'] = 200
    resp['data']['info'] = MemberHandler.deal('detailed_info', member=member_info)
    return resp


@route_api.route("/member/has/qrcode")
@time_log
def memberHasQrcode():
    """
    用户信息
    :return:
    """
    resp = {'code': -1, 'msg': '', 'data': {}}

    member_info = g.member_info
    if not member_info:
        resp['msg'] = "请先登录"
        return resp

    resp['data'] = {"has_qr_code": member_info.has_qr_code}
    resp['code'] = 200
    return resp



@route_api.route("/member/new/hint")
@time_log
def memberNewHint():
    """
    未读答谢和所有的匹配推荐
    :return: 总数, 3类推荐的物品列表
    """
    resp = {'code': -1, 'msg': '', 'data': {}}
    # 检查登陆
    member_info = g.member_info
    if not member_info:
        resp['msg'] = "请先登录"
        return resp
    resp['data'] = MemberHandler.deal('new_hints', member=member_info)
    resp['code'] = 200
    return resp


@route_api.route('/member/renew/session', methods=['GET', 'POST'])
@time_log
def memberSessionUpdate():
    """
    前端检测登录状态已过期，获取新的session_key
    :return:
    """
    resp = {'code': -1, 'msg': '', 'data': {}}
    req = request.get_json()
    code, data = MemberHandler.deal('renew_session', code=req.get('code'))
    if code == -1:
        resp['msg'] = data
        return resp
    resp = {'code': code, 'data': data}
    return resp



@route_api.route('/member/set/name', methods=['GET', 'POST'])
@time_log
def memberNameSet():
    resp = {'code': -1, 'msg': '修改成功', 'data': {}}
    req = request.values
    member_info = g.member_info
    if not member_info:
        resp['msg'] = "请先登录"
        return resp
    name = MemberHandler.deal('change_name', member=member_info, name=req.get('name'))
    resp['code'] = 200
    resp['data'] = {'name': name}
    return resp


@route_api.route('/member/share')
@time_log
def memberShare():
    """
    分享
    :return: 成功
    """
    resp = {'code': -1, 'msg': '', 'data': {}}
    # 检查登陆
    member_info = g.member_info
    if not member_info:
        resp['msg'] = '请先登录'
        return resp
    MemberHandler.deal('change_credits', member=member_info, quantity=5)
    resp['code'] = 200
    return resp


@route_api.route("/member/balance")
@time_log
def memberBalanceGet():
    """
    余额垫付获取剩余余额
    :return:
    """
    resp = {'code': -1, 'msg': '', 'data': {}}

    member_info = g.member_info
    if not member_info:
        resp['msg'] = "请先登录"
        return resp

    resp['data'] = {"balance": str(member_info.balance)}
    resp['code'] = 200
    return jsonify(resp)


@route_api.route("/member/balance/use/warn", methods=['GET', 'POST'])
@time_log
def memberUseBalanceWarn():
    """
    对使用余额，有二维码，但没有任何短信次数的会员进行余额预警
    :return:
    """
    resp = {'code': -1, 'msg': '请先登录', 'data': False}
    member_info = g.member_info
    if not member_info:
        return resp

    resp['data'] = MemberHandler.deal('balance_warn', consumer=member_info)
    resp['code'] = 200
    return resp


@route_api.route("/member/balance/order", methods=['POST', 'GET'])
@time_log
def memberBalanceOrderCreate():
    """
    🥌余额充值下单
    :return:
    """
    resp = {'code': -1, 'msg': '', 'data': {}}
    req = request.values
    member_info = g.member_info
    if not member_info:
        resp['msg'] = "请先登录"
        return resp
    price = req.get('price')
    if not price:
        resp['msg'] = "支付失败"
        return resp

    # 数据库下单
    pay_sign_data = MemberHandler.deal('init_recharge',  consumer=member_info, recharge_amount=price)
    if not pay_sign_data:
        resp['msg'] = '服务繁忙，稍后重试'
        return resp

    resp['data'] = pay_sign_data
    resp['code'] = 200
    return resp


@route_api.route('/member/balance/order/notify', methods=['GET', 'POST'])
@time_log
def memberBalanceOrderCallback():
    """
    余额单子支付回调
    :return:
    """

    xml_data, header = MemberHandler.deal('finish_recharge', callback_body=request.data)
    return xml_data, header


@route_api.route("/member/balance/change", methods=['GET', 'POST'])
@time_log
def memberBalanceChange():
    resp = {'code': -1, 'msg': '', 'data': {}}
    req = request.values
    # note = req.get('note', '')
    member_info = g.member_info
    if not member_info:
        resp['msg'] = "请先登录"
        return resp
    MemberHandler.deal('change_balance', consumer=member_info, quantity=req.get('unit'))
    resp['code'] = 200
    return resp


@route_api.route('/member/sms/pkg/add', methods=['GET', 'POST'])
@time_log
def memberSmsPkgAdd():
    """
    增加短信包
    :return:
    """
    resp = {'code': -1, 'msg': '', 'data': {}}
    member_info = g.member_info
    if not member_info:
        resp['msg'] = "请先登录"
        return resp
    MemberHandler.deal('add_sms_pkg',  consumer=member_info)
    resp['code'] = 200
    return jsonify(resp)


@route_api.route('/member/sms/change', methods=['GET', 'POST'])
@time_log
def memberSmsChange():
    """
    用户通知次数变更
    :return:
    """
    resp = {'code': -1, 'msg': '', 'data': {}}
    req = request.values
    member_info = g.member_info
    if not member_info:
        resp['msg'] = "请先登录"
        return resp
    MemberHandler.deal('add_sms', consumer=member_info, quantity=int(req.get('times', 0)))
    resp['code'] = 200
    return resp


