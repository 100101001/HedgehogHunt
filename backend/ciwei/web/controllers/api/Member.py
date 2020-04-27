# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/1/9 上午12:36
@file: Member.py
@desc:
"""
import datetime
from decimal import Decimal

from flask import request, jsonify, g
from sqlalchemy import and_, or_, func

from application import db, app, APP_CONSTANTS
from common.libs import UserService, LogService
from common.libs.CryptService import Cipher
from common.libs.Helper import queryToDict
from common.libs.MemberService import MemberService
from common.libs.ReportService import REPORT_CONSTANTS
from common.libs.UrlManager import UrlManager
from common.libs.mall.PayService import PayService
from common.libs.mall.WechatService import WeChatService
from common.loggin.decorators import time_log
from common.models.ciwei.BalanceOder import BalanceOrder
from common.models.ciwei.Goods import Good
from common.models.ciwei.Member import Member
from common.models.ciwei.MemberSmsPkg import MemberSmsPkg
from common.models.ciwei.Recommend import Recommend
from common.models.ciwei.Thanks import Thank
from web.controllers.api import route_api


@route_api.route("/member/balance/use/warn", methods=['GET', 'POST'])
@time_log
def memberUseBalanceWarn():
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


@route_api.route("/member/balance/order", methods=['POST', 'GET'])
@time_log
def memberBalanceOrderCreate():
    """
    🥌余额充值下单
    :return:
    """
    resp = {'code': -1, 'msg': 'success', 'data': {}}
    req = request.values
    member_info = g.member_info
    if not member_info:
        resp['msg'] = "请先登录"
        return jsonify(resp)
    price = req['price'] if 'price' in req else 0
    if not price:
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
        'body': '鲟回-充值',
        'out_trade_no': model_order.order_sn,
        'total_fee': int(model_order.price * 100),
        'notify_url': app.config['APP']['domain'] + "/api/member/balance/order/notify",
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
    resp['code'] = 200
    return jsonify(resp)


@route_api.route('/member/balance/order/notify', methods=['GET', 'POST'])
@time_log
def memberBalanceOrderCallback():
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
        return jsonify(resp)

    MemberService.addSmsPkg(openid=member_info.openid)
    db.session.commit()
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
        return jsonify(resp)
    MemberService.updateSmsNotify(member_info=member_info, sms_times=int(req.get('times', 0)))
    db.session.commit()
    resp['code'] = 200
    return jsonify(resp)


@route_api.route("/member/balance/change", methods=['GET', 'POST'])
@time_log
def memberBalanceChange():
    resp = {'code': -1, 'msg': '', 'data': {}}
    req = request.values
    unit = Decimal(req.get('unit', '0')).quantize(Decimal("0.00"))
    note = req.get('note', '')
    member_info = g.member_info
    if not member_info:
        resp['msg'] = "请先登录"
        return jsonify(resp)

    MemberService.updateBalance(member_info=member_info, unit=unit, note=note)
    db.session.commit()
    resp['code'] = 200
    return jsonify(resp)


@time_log
@route_api.route("/member/register", methods=['GET', 'POST'])
def memberReg():
    """
    会员登陆或注册
    :return: openid#会员id
    """
    resp = {'code': -1, 'msg': '', 'data': {}}
    req = request.values

    openid = MemberService.getWeChatOpenId(req.get('code', ''))
    if openid is None:
        resp['msg'] = "注册失败"
        return jsonify(resp)

    model_member = Member()
    model_member.nickname = req.get('nickName', '')
    model_member.sex = req.get('gender', '')
    model_member.avatar = req.get('avatarUrl', '')
    model_member.openid = openid
    model_member.mobile = req.get('mobile', '')  # 加密过了的手机
    db.session.add(model_member)
    db.session.flush()  # 防止获取id，会再次执行查询

    token = "%s#%s" % (openid, model_member.id)
    resp['data'] = {
        'token': token,
        'is_adm': False,
        'is_user': False,
        'has_qrcode': False,
        'member_status': 1,
        'id': model_member.id
    }
    db.session.commit()  # 最后提交
    resp['code'] = 200
    return jsonify(resp)


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
    openid, session_key = MemberService.getWeChatOpenId(req.get('code', ''), get_session_key=True)
    if openid is None or session_key is None:
        resp['msg'] = "登录失败"
        return jsonify(resp)
    member_info, user_info = MemberService.doLogin(openid=openid)
    if not member_info:
        resp['code'] = -2
        resp['data'] = {'openid': openid, 'session_key': session_key}
        return jsonify(resp)

    hard_code_adm = member_info.openid in ['opLxO5fmwgdzntX4gfdKEk5NqLQA']
    is_user = (user_info is not None and user_info.status == 1) or hard_code_adm
    is_adm = hard_code_adm or (is_user and user_info.level == 1)

    token = "%s#%s" % (openid, member_info.id)
    resp['data'] = {
        'token': token,
        'is_adm': is_adm,
        'is_user': is_user,
        'has_qrcode': member_info.has_qr_code,
        'member_status': member_info.status,
        'id': member_info.id
    }
    resp['code'] = 200
    return jsonify(resp)


@route_api.route("/member/is-reg", methods=['GET', 'POST'])
@time_log
def memberIsReg():
    resp = {'code': 200, 'msg': '', 'data': {}}
    req = request.values
    openid = req.get('openid', '')
    resp['data']['is_reg'] = MemberService.isReg(openid=openid)
    return jsonify(resp)


@route_api.route("/member/info")
@time_log
def memberInfo():
    """
    用户信息
    :return: id,昵称,头像,积分,二维码
    """
    resp = {'code': 200, 'msg': '', 'data': {}}

    member_info = g.member_info
    if not member_info:
        resp['code'] = -1
        resp['msg'] = "请先登录"
        return jsonify(resp)

    has_qrcode = member_info.has_qr_code
    qr_code_url = "" if not has_qrcode else UrlManager.buildImageUrl(member_info.qr_code, image_type='QR_CODE')

    pkgs = MemberSmsPkg.query.filter(MemberSmsPkg.open_id == member_info.openid,
                                     MemberSmsPkg.expired_time >= datetime.datetime.now()).all()

    p_times = 0  # 计算套餐包有效期内总数量
    pkg_data_list = []
    for item in pkgs:
        p_time = item.left_notify_times
        tmp_data = {
            'num': p_time,
            'expire': item.expired_time.strftime(format="%Y-%m-%d")
        }
        p_times += p_time
        pkg_data_list.append(tmp_data)

    m_times = member_info.left_notify_times  # 计算按量购买的数量
    resp['data']['info'] = {
        'nickname': member_info.nickname,
        'avatar': member_info.avatar,
        'qr_code': qr_code_url,
        'member_id': member_info.id,
        "credits": member_info.credits,
        "balance": str(member_info.balance),
        "has_qrcode": has_qrcode,
        "name": member_info.name,
        "mobile": Cipher.decrypt(text=member_info.mobile),
        "m_times": m_times,  # 无限期
        "total_times": p_times + m_times,  # 套餐包加单条
        "pkgs": pkg_data_list
    }
    return jsonify(resp)


@route_api.route("/member/simple/info")
@time_log
def memberSimpleInfo():
    """
    用户信息
    :return: 昵称,头像,积分,二维码
    """
    resp = {'code': -1, 'msg': '', 'data': {
        "has_qr_code": False,
        "avatar": "",
        "nickname": "未登录",
        "level": 0
    }}

    member_info = g.member_info
    if member_info:
        resp['data'] = {
            "has_qr_code": member_info.has_qr_code,
            "avatar": member_info.avatar,
            "nickname": member_info.nickname,
            "level": member_info.credits / 100 / 20
        }
    resp['code'] = 200
    return jsonify(resp)


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
        return jsonify(resp)

    resp['data'] = {"has_qr_code": member_info.has_qr_code}
    resp['code'] = 200
    return jsonify(resp)


@route_api.route("/member/balance")
@time_log
def memberBalanceGet():
    """
    用户信息
    :return: id,昵称,头像,积分,二维码
    """
    resp = {'code': 200, 'msg': '', 'data': {}}

    member_info = g.member_info
    if not member_info:
        resp['code'] = -1
        resp['msg'] = "请先登录"
        return jsonify(resp)

    resp['data'] = {"balance": str(member_info.balance)}
    return jsonify(resp)


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
        return jsonify(resp)

    # 推荐规则
    recommends = Recommend.query.filter_by(status=0, target_member_id=member_info.id).all()
    recommend_rule = and_(Good.id.in_([r.found_goods_id for r in recommends]), Good.status.in_([1, 2, 3]))
    # 归还规则
    return_rule = and_(Good.business_type == 2, Good.status == 1)
    # 一次性获取推荐失物和归还物品
    goods_list = Good.query.filter(or_(recommend_rule, return_rule)).with_entities(Good.business_type,
                                                                                   Good.status,
                                                                                   Good.return_goods_id).all()
    # 分割推荐与归还
    recommend_goods = list(filter(lambda item: item.business_type == 1, goods_list))
    return_goods = list(filter(lambda item: item.business_type == 2, goods_list))
    # 推荐状态细分
    recommend_new = min(len(recommend_goods), 99)
    recommend_status_1 = min(len(list(filter(lambda item: item.status == 1, recommend_goods))), 99)
    recommend_status_2 = min(len(list(filter(lambda item: item.status == 2, recommend_goods))), 99)
    recommend_status_3 = min(len(list(filter(lambda item: item.status == 3, recommend_goods))), 99)
    # 归还状态细分
    return_new = len(return_goods)
    # 会员待取回的归还记录(待确认的寻物归还和待取回的二维码归还)
    normal_return_new = len(list(filter(lambda item: item.return_goods_id != 0, return_goods)))
    scan_return_new = min(return_new - normal_return_new, 99)
    normal_return_new = min(normal_return_new, 99)
    return_new = min(return_new, 99)
    # 获取会员未读的答谢记录
    thanks_new = db.session.query(func.count(Thank.id)).filter_by(target_member_id=member_info.id, status=0).scalar()
    thanks_new = min(thanks_new, 99)

    # 总数量,最多显示99+
    total_new = min(recommend_new + thanks_new + return_new, 99)
    # 前端新消息计数
    resp['data'] = {
        'total_new': total_new,  # 总计（导航栏）
        'recommend_new': recommend_new,  # 推荐（记录索引）
        'thanks_new': thanks_new,  # 推荐（记录索引）
        'recommend': {
            'wait': recommend_status_1,  # 推荐的失物招领帖子，待领
            'doing': recommend_status_2,  # 推荐的失物招领帖子，预领
            'done': recommend_status_3,  # 推荐的失物招领帖子，已领
        },
        'return_new': return_new,  # 推荐（记录索引）
        'return': {
            'wait': normal_return_new,
            'doing': scan_return_new
        }
    }  # 首页
    resp['code'] = 200
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
    from common.libs.mall.WechatService import WXBizDataCrypt
    req = request.get_json()
    encrypted_data = req.get('encrypted_data', '')  # 获取加密手机号
    iv = req.get('iv', '')  # 获取加密向量
    session_key = req.get('session_key', '')  # 获取秘钥session_key
    if not session_key or not iv or not encrypted_data:
        resp['msg'] = "手机号获取失败"
        return jsonify(resp)
    # 解密手机号
    pc = WXBizDataCrypt(app.config['OPENCS_APP']['appid'], session_key)  # session_key是秘钥, appID则是解密后的数据一致性核对
    try:
        mobile_obj = pc.decrypt(encrypted_data, iv)
    except Exception as e:
        app.logger.warn(e)
        resp['msg'] = "手机号获取失败，请确保从后台完全关闭小程序后重试"
        return jsonify(resp)
    resp['data'] = {'mobile': Cipher.encrypt(text=mobile_obj.get('phoneNumber'))}
    resp['code'] = 200
    return jsonify(resp)


@time_log
@route_api.route('/member/login/wx', methods=['GET', 'POST'])
def memberSessionUpdate():
    """
    前端检测登录状态已过期，获取新的session_key
    :return:
    """
    resp = {'code': -1, 'msg': '', 'data': {}}
    req = request.get_json()
    openid, session_key = MemberService.getWeChatOpenId(req.get('code', ''), get_session_key=True)
    if openid is None or session_key is None:
        resp['msg'] = "手机号获取失败"
        return jsonify(resp)
    resp['data'] = {
        'openid': openid,
        'session_key': session_key
    }
    resp['code'] = 200
    return jsonify(resp)


@time_log
@route_api.route('/member/set/name', methods=['GET', 'POST'])
def memberNameSet():
    resp = {'code': -1, 'msg': '修改成功', 'data': {}}
    req = request.values
    name = req.get('name', '')
    member_info = g.member_info
    if not member_info:
        resp['msg'] = "请先登录"
        return jsonify(resp)

    MemberService.updateName(member_info=member_info, name=name)
    db.session.commit()
    resp['code'] = 200
    resp['data'] = {'name': name}
    return jsonify(resp)


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

    # 按status筛选用户
    status = int(req.get('status', -1))
    if status not in (0, 2):
        resp['msg'] = '获取失败'
        return resp

    p = max(int(req.get('p', 1)), 1)
    page_size = APP_CONSTANTS['page_size']
    offset = (p - 1) * page_size
    blocked_members = Member.query.filter(Member.status.in_([0, -1])).order_by(Member.updated_time.desc()).offset(
        offset).limit(
        page_size).all()

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
    return jsonify(resp)


# 恢复会员
@route_api.route('/member/restore')
@time_log
def memberRestore():
    """
    恢复用户
    :return: 成功
    """
    resp = {'code': -1, 'msg': '', 'data': {}}
    req = request.values

    member_info = g.member_info
    if not member_info:
        resp['msg'] = '请先登录'
        return resp
    # 将用户的status改为1
    restore_id = int(req.get('id', 0))
    if not restore_id:
        resp['msg'] = '操作失败'
        return resp

    user = UserService.getUserByMid(member_id=member_info.id)
    if not user:
        resp['msg'] = "您不是管理员，操作失败"
        return resp

    MemberService.restoreMember(member_id=restore_id, user_id=user.uid)
    resp['code'] = 200
    return resp


@route_api.route('/member/blocked/record')
@time_log
def memberBlockedRecords():
    """
    用户获取管理员操作自己用户状态的记录，以便进行申诉
    管理员查看封锁记录以便进行驳回，接受
    :return:
    """
    resp = {'code': -1, 'msg': '', 'data': {'list': []}}
    req = request.values
    member_id = int(req.get('id', 0))
    if not member_id:
        resp['msg'] = '获取失败'
        return resp
    stuff_type = int(req.get('status', 0))
    if stuff_type not in REPORT_CONSTANTS['stuff_type']:
        resp['msg'] = '获取失败'
        return resp

    logs = LogService.getStatusChangeLogsWithStuffDetail(member_id=member_id, stuff_type=stuff_type)

    def detailTransformer(stuff_typo=0):
        if stuff_typo == REPORT_CONSTANTS['stuff_type']['goods']:
            def transform(good):
                return {
                    'summary': good.summary,
                    'pics': [UrlManager.buildImageUrl(pic) for pic in good.pics.split(',')],
                    'name': good.name,
                    'loc': good.location.split('###')[1],
                    'owner_name': good.owner_name,
                    'mobile': good.mobile
                }
            return transform
        else:
            def transform(thank):
                return {
                    'thanked_mid': thank.target_member_id,
                    'summary': thank.summary,
                    'reward': str(thank.thank_price)
                }
            return transform

    transformer = detailTransformer(stuff_type)
    data_list = []
    for item in logs:
        tmp = queryToDict(item.MemberStatusChangeLog)
        tmp['stuff'] = transformer(item[1])  # 可以用 item.Good, item.Thank。为了统一用下标
        data_list.append(tmp)
    resp['data']['list'] = data_list
    resp['code'] = 200
    return resp


@route_api.route('/member/blocked/appeal', methods=['POST', 'GET'])
@time_log
def memberBlockedAppeal():
    """
    用户针对某条管理员拉黑自己的记录进行申诉
    :return:
    """
    resp = {'code': -1, 'msg': '', 'data': {}}
    req = request.values
    log_id = req.get('id', 0)
    reason = req.get('reason', '')
    if not log_id or not reason:
        resp['msg'] = '申诉失败'
        return resp
    MemberService.appealStatusChangeRecord(log_id=log_id, reason=reason)
    db.session.commit()
    resp['code'] = 200
    return resp


@route_api.route('/member/block/appeal/reject', methods=['POST', 'GET'])
@time_log
def memberBlockTurnDown():
    """
    管理员驳回用户的封号申诉
    :return:
    """
    resp = {'code': -1, 'msg': '', 'data': {}}
    req = request.values

    member_info = g.member_info
    if not member_info:
        resp['msg'] = '请先登录'
        return resp
        # 将用户的status改为1
    log_id = int(req.get('id', 0))
    if not log_id:
        resp['msg'] = '操作失败'
        return resp

    user = UserService.getUserByMid(member_id=member_info.id)
    if not user:
        resp['msg'] = "您不是管理员，操作失败"
        return resp

    LogService.turnDownBlockAppeal(log_id=log_id)
    db.session.commit()
    resp['code'] = 200
    return resp


@route_api.route('/member/block/appeal/accept', methods=['POST', 'GET'])
@time_log
def memberBlockAccept():
    """
    管理员同意用户的封号申诉
    :return:
    """
    resp = {'code': -1, 'msg': '', 'data': {}}
    req = request.values

    member_info = g.member_info
    if not member_info:
        resp['msg'] = '请先登录'
        return resp
        # 将用户的status改为1
    log_id = int(req.get('id', 0))
    if not log_id:
        resp['msg'] = '操作失败'
        return resp

    user = UserService.getUserByMid(member_id=member_info.id)
    if not user:
        resp['msg'] = "您不是管理员，操作失败"
        return resp
    op_res, op_msg = LogService.acceptBlockAppeal(log_id=log_id, user=user)
    db.session.commit()
    resp['code'] = 200 if op_res else -1
    resp['msg'] = op_msg
    return resp


@route_api.route('/member/share')
@time_log
def memberShare():
    """
    分享
    :return: 成功
    """
    resp = {'code': 200, 'msg': '', 'data': {}}
    # 检查登陆
    member_info = g.member_info
    if not member_info:
        resp['msg'] = '请先登录'
        return jsonify(resp)

    # 会员credits加5
    MemberService.updateCredits(member_info=member_info)
    db.session.commit()
    return jsonify(resp)
