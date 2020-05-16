# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/3/10 下午11:03
@file: MemberService.py
@desc:
"""
import datetime as dt
from datetime import datetime
from decimal import Decimal

from sqlalchemy import or_, and_, func

from application import app, db
from common.cahce.core import CacheOpService
from common.libs.CryptService import Cipher
from common.libs.mall.PayService import PayService
from common.libs.mall.WechatService import WeChatService, WXBizDataCrypt
from common.models.ciwei.BalanceOder import BalanceOrder
from common.models.ciwei.Goods import Good
from common.models.ciwei.Member import Member
from common.models.ciwei.MemberSmsPkg import MemberSmsPkg
from common.models.ciwei.Recommend import Recommend
from common.models.ciwei.Thanks import Thank
from common.models.ciwei.admin.User import User
from common.models.ciwei.logs.thirdservice.BalanceOrderCallbackData import BalanceOrderCallbackData


class MemberHandler:
    __strategy_map = {
        'is_reg': '_isRegistered',
        'init_register': '_decryptMobile',
        'register': '_createNewMember',
        'login': '_doLogin',
        'basic_info': '_getBasicInfo',
        'detailed_info': '_getDetailedInfo',
        'new_hints': '_getNewHints',
        'renew_session': '_renewWechatSession',
        'change_name': '_changeName',
        'change_credits': '_changeCredits',
        'balance_warn': '_balanceUseWarn',
        'init_recharge': '_initRechargeAccount',
        'finish_recharge': '_finishRechargeAccount',
        'change_balance': '_changeBalance',
        'add_sms_pkg': '_addSmsPkg',
        'add_sms': '_addSmsTimes'
    }

    wechat = WeChatService(merchant_key=app.config['OPENCS_APP']['mch_key'])

    @classmethod
    def deal(cls, op, **kwargs):
        strategy = cls.__strategy_map.get(op)
        handler = getattr(cls, strategy, None)
        if handler:
            return handler(**kwargs)

    @classmethod
    def _isRegistered(cls, openid=''):
        if openid:
            member_info = Member.getByOpenId(openid)
        else:
            member_info = 1
        return member_info is not None

    @classmethod
    def _decryptMobile(cls, encrypt_mobile='', iv='', decrypt_key=''):
        # 解密手机号
        pc = WXBizDataCrypt(app.config['OPENCS_APP']['appid'], decrypt_key)  # session_key是秘钥, appID则是解密后的数据一致性核对
        try:
            mobile_obj = pc.decrypt(encrypt_mobile, iv)
        except Exception as e:
            app.logger.warn(e)
            return -1, "手机号获取失败，请确保从后台完全关闭小程序后重试"
        return 200, Cipher.encrypt(text=mobile_obj.get('phoneNumber'))

    @classmethod
    def _createNewMember(cls, reg_info=None):
        openid = cls.wechat.getWeChatOpenId(reg_info.get('code'))
        if not openid:
            return -1, '注册失败'
        new_member = Member(nickname=reg_info.get('nickName', ''), sex=reg_info.get('gender', ''),
                            avatar=reg_info.get('avatarUrl', ''), openid=openid, mobile=reg_info.get('mobile', ''))
        db.session.flush()
        member_id = new_member.id
        db.session.commit()
        return 200, {
            'token': Cipher.encrypt("{0}#{1}".format(member_id, openid)),
            'is_adm': False,
            'is_user': False,
            'has_qrcode': False,
            'member_status': 1,
            'id': member_id
        }

    @classmethod
    def _doLogin(cls, code=''):

        """
        登录
        :param code:
        :return: 会员和管理员信息
        """
        openid, session_key = cls.wechat.getWeChatOpenId(code=code, get_session_key=True)
        if not openid or not session_key:
            return -1, '服务繁忙，稍后重试'


        member_info = Member.getByOpenId(openid=openid)
        if not member_info:
            return -2, {'openid': openid, 'session_key': session_key}

        CacheOpService.setMemberCache(member_info=member_info)
        user_info = User.getByMemberId(member_info.id)
        CacheOpService.setUsersCache(users=[user_info])
        hard_code_adm = member_info.openid in ['opLxO5fmwgdzntX4gfdKEk5NqLQA']
        is_user = (user_info is not None and user_info.status == 1) or hard_code_adm
        is_adm = hard_code_adm or (is_user and user_info.level == 1)
        return 200, {'token': Cipher.encrypt("{0}#{1}".format(member_info.id, member_info.openid)),
                     'is_adm': is_adm,
                     'is_user': is_user,
                     'has_qrcode': member_info.has_qr_code,
                     'member_status': member_info.status,
                     'id': member_info.id,
                     'openid': member_info.openid
                     }

    @classmethod
    def _getBasicInfo(cls, member=None):
        if member:
            return 200, {
                "has_qr_code": member.has_qr_code,
                "avatar": member.avatar,
                "nickname": member.nickname,
                "level": member.credits / 100 / 20
            }
        else:
            return -1, {
                "has_qr_code": False,
                "avatar": "/images/more/un_reg_user.png",
                "nickname": "未登录",
                "level": 0
            }

    @classmethod
    def _getDetailedInfo(cls, member=None):
        def __getSmsDetailedInfo():
            # pkgs = MemberSmsPkg.getAllValidPkg(member_id=member.id)
            p_times = 0  # 计算套餐包有效期内总数量
            pkg_data_list = []
            # for item in pkgs:
            #     p_time = item.left_notify_times
            #     tmp_data = {
            #         'num': p_time,
            #         'expire': item.expired_time.strftime(format="%Y-%m-%d")
            #     }
            #     p_times += p_time
            #     pkg_data_list.append(tmp_data)
            m_times = member.left_notify_times  # 计算按量购买的数量
            total = p_times + m_times
            return total, m_times, pkg_data_list

        total_sms, unlimited_times, pkg_detail = __getSmsDetailedInfo()
        return {
            'member_id': member.id,
            "name": member.name,
            "mobile": member.decrypt_mobile,
            'nickname': member.nickname,
            'avatar': member.avatar,
            # 二维码
            "has_qrcode": member.has_qr_code,
            'qr_code': member.qr_code_url,
            # 余额积分
            "credits": member.credits,
            "balance": str(member.balance),
            # 短信
            "m_times": unlimited_times,  # 无限期
            "total_times": total_sms,  # 套餐包加单条
            "pkgs": pkg_detail
        }

    @classmethod
    def _getNewHints(cls, member=None):
        # 推荐规则
        recommends = Recommend.query.filter_by(status=0, target_member_id=member.id).all()
        recommend_rule = and_(Good.id.in_([r.found_goods_id for r in recommends]), Good.status.in_([1, 2, 3]))
        # 归还规则
        return_rule = and_(Good.business_type == 2, Good.status == 1,
                           or_(Good.return_goods_openid == member.openid,
                               Good.qr_code_openid == member.openid))
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
        # normal_return_new = len(list(filter(lambda item: item.return_goods_id != 0, return_goods)))
        # scan_return_new = min(return_new - normal_return_new, 99)
        # normal_return_new = min(normal_return_new, 99)
        return_new = min(return_new, 99)
        # 获取会员未读的答谢记录
        thanks_new = db.session.query(func.count(Thank.id)).filter_by(target_member_id=member.id,
                                                                      status=0).scalar()
        thanks_new = min(thanks_new, 99)

        # 总数量,最多显示99+
        total_new = min(recommend_new + thanks_new + return_new, 99)
        # 前端新消息计数
        return {
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
                'wait': return_new
            }
        }  # 首页

    @classmethod
    def _renewWechatSession(cls, code=''):
        openid, session_key = cls.wechat.getWeChatOpenId(code, get_session_key=True)
        if openid is None or session_key is None:
            return -1, "手机号获取失败"
        return 200, {'session_key': session_key}

    @classmethod
    def _changeName(cls, member=None, name=''):
        member.changeName(name)
        db.session.commit()
        return name

    @classmethod
    def _changeCredits(cls, member=None, quantity=0):
        member.changeCredits(quantity)
        db.session.commit()

    @classmethod
    def _balanceUseWarn(cls, consumer=None):
        """
        余额垫付警告预留短信费
        :param consumer:
        :return:
        """
        if consumer.has_qr_code:
            if consumer.left_notify_times <= 0:
                pkg = MemberSmsPkg.getOldestValidPkg(openid=consumer.openid)
                if not pkg:
                    return True
        return False

    @classmethod
    def _initRechargeAccount(cls, consumer=None, recharge_amount=''):
        model_order = BalanceOrder(consumer=consumer, price=recharge_amount)
        # 微信下单
        pay_data = {
            'appid': app.config['OPENCS_APP']['appid'],
            'mch_id': app.config['OPENCS_APP']['mch_id'],
            'nonce_str': cls.wechat.get_nonce_str(),
            'body': '鲟回-充值',
            'out_trade_no': model_order.order_sn,
            'total_fee': int(model_order.price * 100),
            'notify_url': app.config['APP']['domain'] + "/api/member/balance/order/notify",
            'time_expire': (datetime.now() + dt.timedelta(minutes=5)).strftime("%Y%m%d%H%M%S"),
            'trade_type': 'JSAPI',
            'openid': consumer.openid
        }

        pay_sign_data = cls.wechat.get_pay_info(pay_data=pay_data)
        if not pay_sign_data:
            return None
        model_order.status = 0
        db.session.commit()
        return pay_sign_data

    @classmethod
    def _finishRechargeAccount(cls, callback_body=None):

        def __accountRechargeSuccess(order_info=None, params=None):
            """
            支付成功后,更新订单状态
            :param order_info:
            :param params:
            :return: 数据库操作成功
            """
            # 更新BalanceOrder支付状态
            PayService.orderPaid(order_info=order_info, params=params)

        def __addRechargePayCallbackData(order_id=0, callback_type='pay', data=''):
            """
            微信支付回调记录
            :param order_id:
            :param callback_type:
            :param data:
            :return:
            """
            PayService.addCallbackData(BalanceOrderCallbackData, 'balance_order_id', order_id, data=data,
                                       callback_type=callback_type)

        callback_data = cls.wechat.xml_to_dict(callback_body)
        app.logger.info(callback_data)

        # 检查签名和订单金额
        sign = callback_data['sign']
        callback_data.pop('sign')
        gene_sign = cls.wechat.create_sign(callback_data)
        app.logger.info(gene_sign)
        if sign != gene_sign or callback_data['result_code'] != 'SUCCESS':
            return PayService.callBackReturn(wechat=cls.wechat)

        pay_order_info = BalanceOrder.getByOrderSn(callback_data['out_trade_no'])
        if not pay_order_info or int(pay_order_info.price * 100) != int(callback_data['total_fee']):
            return PayService.callBackReturn(wechat=cls.wechat)
        # 订单状态已回调更新过直接返回
        if pay_order_info.status == 1:
            return PayService.callBackReturn(success=True, wechat=cls.wechat)
        # 订单状态未回调更新过
        __accountRechargeSuccess(order_info=pay_order_info, params={"pay_sn": callback_data['transaction_id'],
                                                                    "paid_time": callback_data['time_end']})
        __addRechargePayCallbackData(order_id=pay_order_info.id, data=callback_body)
        return PayService.callBackReturn(success=True, wechat=cls.wechat)

    @classmethod
    def _changeBalance(cls, consumer=None, quantity='0'):
        consumer.changeBalance(quantity=Decimal(quantity).quantize(Decimal('.00')))
        db.session.commit()

    @classmethod
    def _addSmsPkg(cls, consumer=None):
        MemberSmsPkg(openid=consumer.openid, member_id=consumer.id)
        db.session.commit()

    @classmethod
    def _addSmsTimes(cls, consumer=None, quantity=0):
        consumer.changeSms(quantity=quantity)
        db.session.commit()

















class MemberService:
    @staticmethod
    def updateCredits(member_id=0, quantity=5):
        """
        更新会员积分
        :param member_id:
        :param quantity: 变更积分数，默认 5
        :return:
        """
        if not member_id or not quantity:
            return
        # 发布成功，用户积分涨5
        member_info = Member.getById(member_id)
        if member_info:
            member_info.credits += quantity
            db.session.add(member_info)


