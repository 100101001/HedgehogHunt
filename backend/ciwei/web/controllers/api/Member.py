#!/usr/bin/python3.6.8
# -*- coding:utf-8 -*-
import datetime
from decimal import Decimal

from flask import request, jsonify, g

from application import db, app
from common.libs.Helper import getCurrentDate
from common.libs.MemberService import MemberService
from common.libs.UrlManager import UrlManager
from common.libs.mall.PayService import PayService
from common.libs.mall.WechatService import WeChatService
from common.models.ciwei.BalanceOder import BalanceOrder
from common.models.ciwei.Goods import Good
from common.models.ciwei.Member import Member
from common.models.ciwei.MemberSmsPkg import MemberSmsPkg
from common.models.ciwei.Thanks import Thank
from common.models.ciwei.User import User

from web.controllers.api import route_api


@route_api.route("/balance/use/warn", methods=['GET', 'POST'])
def warnUseBalance():
    """
    对使用余额，有二维码，但没有任何短信次数的会员进行余额预警
    :return:
    """
    resp = {'code': 200, 'msg': 'success', 'data': False}
    member_info = g.member_info
    if not member_info:
        resp['code'] = -1
        resp['msg'] = "请先登录"
        return jsonify(resp)

    if member_info.has_qr_code:
        if member_info.left_notify_times <= 0:
            pkg = MemberSmsPkg.query.filter(MemberSmsPkg.open_id == member_info.openid,
                                            MemberSmsPkg.expired_time < datetime.datetime.now() + datetime.timedelta(
                                                weeks=1),
                                            MemberSmsPkg.left_notify_times > 0).first()
            if not pkg:
                resp['data'] = True
    return jsonify(resp)


@route_api.route("/balance/order", methods=['POST', 'GET'])
def createBalanceOrder():
    """
    🥌余额充值下单
    :return:
    """
    resp = {'code': 200, 'msg': 'success', 'data': {}}
    req = request.values
    member_info = g.member_info
    if not member_info:
        resp['code'] = -1
        resp['msg'] = "请先登录"
        return jsonify(resp)
    price = req['price'] if 'price' in req else 0
    if not price:
        resp['code'] = -1
        resp['msg'] = "支付失败"
        return jsonify(resp)

    # 数据库下单
    wechat_service = WeChatService(merchant_key=app.config['OPENCS_APP']['mch_key'])
    pay_service = PayService()
    model_order = BalanceOrder()
    model_order.order_sn = pay_service.geneBalanceOrderSn()
    model_order.openid = member_info.openid
    model_order.member_id = member_info.id
    model_order.price = Decimal(price).quantize(Decimal('0.00'))

    # 微信下单
    pay_data = {
        'appid': app.config['OPENCS_APP']['appid'],
        'mch_id': app.config['OPENCS_APP']['mch_id'],
        'nonce_str': wechat_service.get_nonce_str(),
        'body': '闪寻-充值',
        'out_trade_no': model_order.order_sn,
        'total_fee': int(model_order.price * 100),
        'notify_url': app.config['APP']['domain'] + "/api/balance/order/notify",
        'time_expire': (datetime.datetime.now() + datetime.timedelta(minutes=5)).strftime("%Y%m%d%H%M%S"),
        'trade_type': 'JSAPI',
        'openid': member_info.openid
    }
    pay_sign_data = wechat_service.get_pay_info(pay_data=pay_data)
    if not pay_sign_data:
        resp['code'] = -1
        resp['msg'] = "微信服务器繁忙，请稍后重试"
        return jsonify(resp)
    model_order.status = 0
    db.session.add(model_order)
    db.session.commit()
    resp['data'] = pay_sign_data
    return jsonify(resp)


@route_api.route('/balance/order/notify', methods=['GET', 'POST'])
def balanceOrderCallback():
    """
    余额单子支付回调
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
    pay_order_info = BalanceOrder.query.filter_by(order_sn=order_sn).first()
    if not pay_order_info:
        result_data['return_code'] = result_data['return_msg'] = 'FAIL'
        return target_wechat.dict_to_xml(result_data), header

    if int(pay_order_info.price * 100) != int(callback_data['total_fee']):
        result_data['return_code'] = result_data['return_msg'] = 'FAIL'
        return target_wechat.dict_to_xml(result_data), header

    # 更新订单的支付状态, 记录日志

    # 订单状态已回调更新过直接返回
    if pay_order_info.status == 1:
        return target_wechat.dict_to_xml(result_data), header
    # 订单状态未回调更新过
    target_pay = PayService()
    target_pay.balanceOrderSuccess(pay_order_id=pay_order_info.id, params={"pay_sn": callback_data['transaction_id'],
                                                                           "paid_time": callback_data['time_end']})
    target_pay.addBalancePayCallbackData(pay_order_id=pay_order_info.id, data=request.data)

    return target_wechat.dict_to_xml(result_data), header


@route_api.route('/member/sms/pkg/add', methods=['GET', 'POST'])
def addSmsPkg():
    """

    :return:
    """
    resp = {'code': 200, 'msg': '', 'data': {}}
    req = request.values
    member_info = g.member_info
    if not member_info:
        resp['code'] = -1
        resp['msg'] = "请先登录"
        return jsonify(resp)

    pkg = MemberSmsPkg()
    pkg.open_id = member_info.openid
    pkg.left_notify_times = 50
    pkg.expired_time = datetime.datetime.now() + datetime.timedelta(weeks=156)
    db.session.add(pkg)
    db.session.commit()
    return jsonify(resp)


@route_api.route('/member/sms/change', methods=['GET', 'POST'])
def changeSmsTimes():
    """
    用户通知次数
    :return:
    """
    resp = {'code': 200, 'msg': '', 'data': {}}
    req = request.values
    member_info = g.member_info
    if not member_info:
        resp['code'] = -1
        resp['msg'] = "请先登录"
        return jsonify(resp)

    times = int(req['times']) if 'times' in req else 0
    member_info.left_notify_times += times
    db.session.add(member_info)
    db.session.commit()
    return jsonify(resp)


@route_api.route("/member/balance/change", methods=['GET', 'POST'])
def balanceChange():
    resp = {'code': 200, 'msg': '', 'data': {}}
    req = request.values
    unit = req['unit'] if 'unit' in req else 0
    unit = Decimal(unit).quantize(Decimal("0.00"))

    member_info = g.member_info
    if not member_info:
        resp['code'] = -1
        resp['msg'] = "请先登录"
        return jsonify(resp)

    member_info.balance += unit
    MemberService.setMemberBalanceChange(member_info=member_info, unit=unit, note=req['note'] if 'note' in req else '')
    db.session.add(member_info)
    db.session.commit()
    return jsonify(resp)


# TODO：如果可以锁号，那么登陆需要判断用户的status
@route_api.route("/member/login", methods=['GET', 'POST'])
def login():
    """
    会员登陆或注册
    :return: openid#会员id
    """
    resp = {'code': 200, 'msg': 'login successfully(login)', 'data': {}}
    req = request.values

    # 检查参数：code
    code = req['code'] if 'code' in req else ''

    if not code or len(code) < 1:
        resp['code'] = -1
        resp['msg'] = "need code"
        return jsonify(resp)

    # 微信端登陆
    # 没注册：新增openid绑定的会员/查找openid绑定的会员
    # 返回openid#会员id
    openid = MemberService.getWeChatOpenId(code)
    if openid is None:
        resp['code'] = -1
        resp['msg'] = "call wechat error"
        return jsonify(resp)

    nickname = req['nickName'] if 'nickName' in req else ''
    sex = req['gender'] if 'gender' in req else 0
    avatar = req['avatarUrl'] if 'avatarUrl' in req else ''
    mobile = req['mobile'] if 'mobile' in req and req['mobile'] else ''
    '''
    判断是否已经注册过，注册了直接返回一些信息即可
    '''
    member_info = Member.query.filter_by(openid=openid, status=1).first()
    if not member_info:
        model_member = Member()
        model_member.nickname = nickname
        model_member.sex = sex
        model_member.avatar = avatar
        model_member.updated_time = model_member.created_time = getCurrentDate()
        model_member.openid = openid
        model_member.mobile = mobile
        db.session.add(model_member)
        db.session.commit()
        member_info = model_member
    else:
        if not nickname:
            member_info.nickname = nickname
            db.session.add(member_info)
        if not sex:
            member_info.sex = sex
            db.session.add(member_info)
        if not avatar:
            member_info.avatar = avatar
            db.session.add(member_info)
        if not mobile:
            member_info.mobile = mobile
            db.session.add(member_info)
        db.session.commit()

    # 登陆后，前端在 app.globalData 中存有全局变量
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

    # 济人济市的openid if openid=="opLxO5fmwgdzntX4gfdKEk5NqLQA":
    # uni-济旦财的openid if openid=="o1w1e5egBOLj5SjvPkNIsA3jpZFI":
    if openid == "opLxO5fmwgdzntX4gfdKEk5NqLQA":
        is_adm = True
        is_user = True

    if member_info.qr_code:
        has_qrcode = True

    token = "%s#%s" % (openid, member_info.id)
    resp['data'] = {
        'token': token,
        'is_adm': is_adm,
        'is_user': is_user,
        'has_qrcode': has_qrcode,
        'member_status': member_info.status,
        'id': member_info.id
    }
    return jsonify(resp)


@route_api.route("/member/check-reg", methods=['GET', 'POST'])
def checkReg():
    """
    角色信息
    :return:用户角色,二维码,token,用户状态
    """
    resp = {'code': 200, 'msg': 'login successfully(check-reg)', 'data': {}}
    req = request.values

    # 检查参数：code

    code = req['code'] if 'code' in req else ''
    if not code:
        resp['code'] = -1
        resp['msg'] = "微信繁忙"
        return jsonify(resp)

    openid, session_key = MemberService.getWeChatOpenId(code, get_session_key=True)
    if not openid:
        resp['code'] = -1
        resp['msg'] = "微信繁忙"
        return jsonify(resp)
    member_info = Member.query.filter_by(openid=openid).first()
    if not member_info:
        resp['code'] = -2
        resp['member_status'] = -2
        resp['data'] = {
            'openid': openid,
            'session_key': session_key
        }
        resp['msg'] = "用户未注册"
        return jsonify(resp)
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

    # 济人济市的openid if openid=="opLxO5fmwgdzntX4gfdKEk5NqLQA":
    # uni-济旦财的openid if openid=="o1w1e5egBOLj5SjvPkNIsA3jpZFI":
    if openid == "opLxO5fmwgdzntX4gfdKEk5NqLQA":
        is_adm = True
        is_user = True

    if member_info.qr_code:
        has_qrcode = True

    token = "%s#%s" % (openid, member_info.id)
    resp['data'] = {
        'token': token,
        'is_adm': is_adm,
        'is_user': is_user,
        'has_qrcode': has_qrcode,
        'member_status': member_info.status,
        'id': member_info.id
    }
    return jsonify(resp)


@route_api.route("/member/is-reg", methods=['GET', 'POST'])
def isReg():
    resp = {'code': 200, 'msg': '', 'data': {}}
    req = request.values
    openid = req['openid'] if 'openid' in req else ''
    member_info = Member.query.filter_by(openid=openid).first()
    if not member_info:
        resp['data']['is_reg'] = False
    else:
        resp['data']['is_reg'] = True
    return jsonify(resp)


@route_api.route("/member/info")
def memberInfo():
    """
    用户信息
    :return: id,昵称,头像,积分,二维码
    """
    resp = {'code': 200, 'msg': '', 'data': {}}

    member_info = g.member_info
    if not member_info:
        resp['code'] = -1
        resp['msg'] = "没有相关用户信息"
        return jsonify(resp)

    has_qrcode = False
    if member_info.qr_code:
        qr_code_url = UrlManager.buildImageUrl(member_info.qr_code)
        has_qrcode = True
    else:
        qr_code_url = ""

    pkg = MemberSmsPkg.query.filter(MemberSmsPkg.open_id == member_info.openid,
                                    MemberSmsPkg.expired_time >= datetime.datetime.now()) \
        .order_by(MemberSmsPkg.id.desc()).first()
    resp['data']['info'] = {
        'nickname': member_info.nickname,
        'avatar': member_info.avatar,
        'qr_code': qr_code_url,
        'member_id': member_info.id,
        "credits": member_info.credits,
        "balance": str(member_info.balance),
        "has_qrcode": has_qrcode,
        "name": member_info.name,
        "mobile": member_info.mobile,
        "m_times": member_info.left_notify_times,
        "p_times": pkg.left_notify_times if pkg else 0,
        "p_expire": pkg.expired_time.strftime(format="%Y-%m-%d") if pkg else ''
    }
    return jsonify(resp)


@route_api.route("/member/balance")
def memberBalance():
    """
    用户信息
    :return: id,昵称,头像,积分,二维码
    """
    resp = {'code': 200, 'msg': '', 'data': {}}

    member_info = g.member_info
    if not member_info:
        resp['code'] = -1
        resp['msg'] = "没有相关用户信息"
        return jsonify(resp)

    resp['data'] = {
        "balance": str(member_info.balance)
    }
    return jsonify(resp)


@route_api.route("/member/has-qrcode")
def memberHasQrcode():
    """
    用户信息
    :return: id,昵称,头像,积分,二维码
    """
    resp = {'code': 200, 'msg': '', 'data': {}}

    member_info = g.member_info
    if not member_info:
        resp['code'] = -1
        resp['msg'] = "没有相关用户信息"
        return jsonify(resp)

    resp['data'] = {
        "has_qr_code": member_info.has_qr_code
    }
    return jsonify(resp)


# TODO：不需要分页么？
@route_api.route("/member/get-new-recommend")
def getNewRecommend():
    """
    未读答谢和所有的匹配推荐
    :return: 总数, 3类推荐的物品列表
    """
    resp = {'code': 200, 'msg': '', 'data': {}}
    # 检查登陆
    member_info = g.member_info
    if not member_info:
        resp['code'] = -1
        resp['msg'] = "没有相关用户信息"
        return jsonify(resp)

    # 获取所有会员的recommend_id列表中的物品,按状态：待,预,已分类
    recommend_status_2 = recommend_status_3 = recommend_status_1 = 0
    recommend_new = thanks_new = 0
    if member_info.recommend_id:
        recommend_dict = MemberService.getRecommendDict(member_info.recommend_id, True)
        query = Good.query.filter(Good.id.in_(recommend_dict.keys()))
        recommend_status_1 = len(query.filter_by(status=1).all())
        recommend_status_2 = len(query.filter_by(status=2).all())
        recommend_status_3 = len(query.filter_by(status=3).all())
        recommend_new = len(recommend_dict) if len(recommend_dict) <= 99 else 99

    # 获取会员未读的答谢记录
    thanks_query = Thank.query.filter_by(target_member_id=member_info.id)
    thanks_list = thanks_query.filter_by(status=0).all()
    if thanks_list:
        thanks_new = len(thanks_list) if len(thanks_list) <= 99 else 99

    # 总数量,最多显示99+
    total_new = recommend_new + thanks_new
    total_new = total_new if total_new <= 99 else 99

    resp['data'] = {
        'total_new': total_new,
        'recommend_new': recommend_new,
        'thanks_new': thanks_new,
        'recommend': {
            'wait': recommend_status_1 if recommend_status_1 <= 99 else 99,
            'doing': recommend_status_2 if recommend_status_2 <= 99 else 99,
            'done': recommend_status_3 if recommend_status_3 <= 99 else 99,
        }
    }
    return jsonify(resp)


@route_api.route("/member/block-search", methods=['GET', 'POST'])
def blockMemberSearch():
    """
    :return: 状态为status的用户信息列表
    """

    resp = {'code': 200, 'msg': 'search record successfully(search)', 'data': {}}
    req = request.values

    # 检查登陆
    member_info = g.member_info
    if not member_info:
        resp['code'] = -1
        resp['msg'] = "用户信息异常"
        return jsonify(resp)

    # 按status筛选用户
    status = int(req['status']) if 'status' in req else "nonono"
    query = Member.query.filter_by(status=status)

    # 分页, 排序
    p = int(req['p']) if ('p' in req and req['p']) else 1
    if p < 1:
        p = 1
    page_size = 10
    offset = (p - 1) * page_size
    member_list = query.order_by(Member.updated_time.desc()).offset(offset).limit(10).all()

    # models -> objects
    # 用户信息列表
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
    """
    恢复用户
    :return: 成功
    """
    resp = {'code': 200, 'msg': 'operate successfully(get info)', 'data': {}}
    req = request.values

    # 将用户的status改为1
    select_member_id = int(req['id']) if ('id' in req and req['id']) else 0
    select_member_info = Member.query.filter_by(id=select_member_id).first()
    select_member_info.status = 1
    select_member_info.updated_time = getCurrentDate()
    db.session.add(select_member_info)

    # 将用户发布的物品status从8改为1
    goods_list = Good.query.filter(Good.member_id == select_member_id, Good.status == 8).all()
    for item in goods_list:
        item.status = 1
        item.updated_time = getCurrentDate()
        db.session.add(item)

    db.session.commit()
    return jsonify(resp)


@route_api.route('/member/share')
def memberShare():
    """
    分享
    :return: 成功
    """
    resp = {'code': 200, 'msg': 'operate successfully(get info)', 'data': {}}
    # 检查登陆
    member_info = g.member_info
    if not member_info:
        resp['code'] = -1
        resp['msg'] = "用户信息异常"
        return jsonify(resp)

    # 会员credits加5
    member_info.credits = member_info.credits + 5
    member_info.updated_time = getCurrentDate()
    db.session.add(member_info)
    db.session.commit()

    return jsonify(resp)


@route_api.route("/member/phone/decrypt", methods=['POST', 'GET'])
def decryptPhone():
    resp = {'code': 200, 'msg': '已获取手机号', 'data': {}}
    from common.libs.mall.WechatService import WXBizDataCrypt
    req = request.get_json()
    app.logger.info(req)
    # 获取加密手机号
    encrypted_data = req['encrypted_data'] if 'encrypted_data' in req and req['encrypted_data'] else ''
    if not encrypted_data:
        resp['code'] = -1
        resp['msg'] = "手机号获取失败"
        return jsonify(resp)
    # 获取加密向量
    iv = req['iv'] if 'iv' in req and req['iv'] else ''
    if not iv:
        resp['code'] = -1
        resp['msg'] = "手机号获取失败"
        return jsonify(resp)
    # 获取session_key
    session_key = req['session_key'] if 'session_key' in req and req['session_key'] else ''
    if not session_key:
        resp['code'] = -1
        resp['msg'] = "手机号获取失败"
        return jsonify(resp)
    appId = app.config['OPENCS_APP']['appid']
    # 解密手机号
    pc = WXBizDataCrypt(appId, session_key)
    try:
        mobile_obj = pc.decrypt(encrypted_data, iv)
    except Exception as e:
        app.logger.warn(e)
        resp['code'] = -1
        resp['msg'] = "手机号获取失败，请确保从后台完全关闭小程序后重试"
        return jsonify(resp)
    mobile = mobile_obj['phoneNumber']
    app.logger.info("手机号是：{}".format(mobile))
    resp['data'] = {
        'mobile': mobile
    }
    return jsonify(resp)


@route_api.route('/member/login/wx', methods=['GET', 'POST'])
def getUserInfo():
    resp = {'code': 200, 'msg': '已获取手机号', 'data': {}}
    req = request.get_json()
    code = req['code'] if 'code' in req and req['code'] else ''
    if not code:
        resp['code'] = -1
        resp['msg'] = "手机号获取失败"
        return jsonify(resp)
    openid, session_key = MemberService.getWeChatOpenId(code, get_session_key=True)
    if openid is None:
        resp['code'] = -1
        resp['msg'] = "手机号获取失败"
        return jsonify(resp)
    resp['data'] = {
        'openid': openid,
        'session_key': session_key
    }
    return jsonify(resp)


@route_api.route('/member/set/name', methods=['GET', 'POST'])
def setName():
    resp = {'code': 200, 'msg': '修改成功', 'data': {}}
    req = request.values
    name = req['name'] if 'name' in req and req['name'] else ''
    member_info = g.member_info
    if not member_info:
        resp['code'] = -1
        resp['msg'] = "请先登录"
        return jsonify(resp)

    member_info.name = name
    member_info.updated_time = getCurrentDate()
    db.session.add(member_info)
    db.session.commit()
    resp['data'] = {'name': member_info.name}
    return jsonify(resp)


@route_api.route('/member/exists', methods=['GET', 'POST'])
def member_exists():
    resp = {'code': 200, 'msg': '用户已注册', 'data': {'exists': True}}
    req = request.values
    openid = req['openid'] if 'openid' in req and req['openid'] else ''
    if not openid:
        resp['code'] = -1
        resp['msg'] = "登陆信息缺失"
        return jsonify(resp)
    member_info = Member.query.filter_by(openid=openid).first()
    if not member_info:
        resp['data'] = {'exists': False}
    return jsonify(resp)
