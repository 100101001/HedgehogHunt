# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/4/19 下午4:45
@file: ThanksService.py
@desc: 
"""
import datetime as dt
from datetime import datetime

from sqlalchemy import or_

from application import db, app
from common.cahce.GoodsCasUtil import GoodsCasUtil
from common.libs.Helper import queryToDict
from common.libs.mall.PayService import PayService
from common.libs.mall.WechatService import WeChatService
from common.models.ciwei.Goods import Good
from common.models.ciwei.Mark import Mark
from common.models.ciwei.Member import Member
from common.models.ciwei.ThankOrder import ThankOrder
from common.models.ciwei.Thanks import Thank
from common.models.ciwei.logs.thirdservice.ThankOrderCallbackData import ThankOrderCallbackData
from common.tasks.subscribe import SubscribeTasks


class ThankHandler:

    __strategy_map = {
        'init_pay': '_initThankPay',
        'finish_pay': '_finishThankPay',
        'create': '_createThanks',
        'insert_trig': '_insertThanksTrigger',
        'read': '_readReceivedThanks',
    }

    wechat = WeChatService(merchant_key=app.config['OPENCS_APP']['mch_key'])


    @classmethod
    def deal(cls, op, **kwargs):
        strategy = cls.__strategy_map.get(op)
        handler = getattr(cls, strategy, None)
        if handler:
            return handler(**kwargs)


    @classmethod
    def _initThankPay(cls, consumer=None, price='', discount='', **kwargs):
        # 数据库下单
        model_order = ThankOrder(consumer=consumer, price=price, discount=discount)
        order_sn = model_order.order_sn
        # 微信下单
        pay_data = {
            'appid': app.config['OPENCS_APP']['appid'],
            'mch_id': app.config['OPENCS_APP']['mch_id'],
            'nonce_str': cls.wechat.get_nonce_str(),
            'body': '鲟回-答谢',
            'out_trade_no': order_sn,
            'total_fee': int(model_order.price * 100),
            'notify_url': app.config['APP']['domain'] + "/api/thank/order/notify",
            'time_expire': (datetime.now() + dt.timedelta(minutes=5)).strftime("%Y%m%d%H%M%S"),
            'trade_type': 'JSAPI',
            'openid': model_order.openid
        }
        pay_sign_data = cls.wechat.get_pay_info(pay_data=pay_data)
        if not pay_sign_data:
            return None
        model_order.status = 0
        db.session.commit()
        pay_sign_data['thank_order_sn'] = order_sn
        return pay_sign_data


    @classmethod
    def _finishThankPay(cls, callback_body=None, **kwargs):
        callback_data = cls.wechat.xml_to_dict(callback_body)
        app.logger.info(callback_data)

        # 检查签名和订单金额
        sign = callback_data['sign']
        callback_data.pop('sign')
        gene_sign = cls.wechat.create_sign(callback_data)
        app.logger.info(gene_sign)
        if sign != gene_sign or callback_data['result_code'] != 'SUCCESS':
            return PayService.callBackReturn(wechat=cls.wechat)

        thank_order_info = ThankOrder.getByOrderSn(callback_data['out_trade_no'])
        if not thank_order_info or int(thank_order_info.price * 100) != int(callback_data['total_fee']):
            return PayService.callBackReturn(wechat=cls.wechat)

        # 更新订单的支付状态, 记录日志
        # 订单状态已回调更新过直接返回
        if thank_order_info.status == 1:
            return PayService.callBackReturn(success=True,wechat=cls.wechat)

        def __thankOrderSuccess():
            PayService.orderPaid(order_info=thank_order_info, params={"pay_sn": callback_data['transaction_id'],
                                                                      "paid_time": callback_data['time_end']})

        def __addCallbackData():
            PayService.addCallbackData(ThankOrderCallbackData, 'thank_order_id', thank_order_info.id,
                                       data=callback_body)

        # 订单状态未回调更新过
        __thankOrderSuccess()
        __addCallbackData()
        db.session.commit()
        return PayService.callBackReturn(success=True,wechat=cls.wechat)


    @classmethod
    def _createThanks(cls, sender=None, gotback_goods=None, thank_info=None, **kwargs):
        """

        :param sender: 答谢者信息
        :param gotback_goods: 答谢物品信息
        :param thank_info: 答谢信息
        :return:
        """

        def __updateBalance(member_id=0, quantity=0):
            """
            别删，id更新有用
            :param member_id:
            :param quantity:
            :return:
            """
            if quantity != 0:
                member = Member.getById(member_id)
                member.balance += quantity
                db.session.add(member)


        thanks_model = Thank(sender=sender, gotback_goods=gotback_goods, thank_info=thank_info)
        # 发出答谢的用户信息
        # 金额转入目标用户余额
        __updateBalance(member_id=thanks_model.target_member_id, quantity=thanks_model.thank_price)
        SubscribeTasks.send_thank_subscribe.delay(thank_info=queryToDict(thanks_model))
        db.session.commit()

    @classmethod
    def _readReceivedThanks(cls, member_info=None, **kwargs):
        if member_info:
            Thank.readReceivedThanks(member_id=member_info.id)
            db.session.commit()


    @classmethod
    def _insertThanksTrigger(cls, biz_typo=0, goods_id=0, sender_id=0, **kwargs):
        if biz_typo == "拾到":
            # 帖子和认领记录一起更新
            cls.__updateThankedFoundStatus(found_id=goods_id, send_member_id=sender_id)
        else:
            # 归还和寻物帖子一起更新
            cls.__updateThankedReturnStatus(return_id=goods_id)
        Mark.thanked(member_id=sender_id, goods_id=goods_id)

    @classmethod
    def __updateThankedFoundStatus(cls, found_id=0, send_member_id=0):
        if not found_id or not send_member_id:
            return
        if GoodsCasUtil.exec_wrap(found_id, ['nil', 3], 4):
            # 如果没有被删除就更新为已答谢，否则不更新
            Good.batch_update(Good.id == found_id, Good.status == 3,
                              val={'status': 4, 'thank_time': datetime.now()})

    @classmethod
    def __updateThankedReturnStatus(cls, return_id=0):
        if not return_id:
            return
        lost_id = Good.getLinkId([return_id], batch=False)
        # 对方可能正好删除了归还帖子，但寻物贴只有答谢者自己才能删除的帖子，不可能并发操作
        updated = {'status': 4, 'thank_time': datetime.now()}
        GoodsCasUtil.exec_wrap(lost_id[0], ['nil', 3], 4)  # 寻物贴只有自己能操作状态，所以不会冲突
        if GoodsCasUtil.exec_wrap(return_id, ['nil', 3], 4):  # 归还帖对方可以删除
            # 不存在并发操作
            Good.batch_update(or_(Good.id == return_id, Good.id == lost_id[0]),
                              Good.status == 3, val=updated)
        else:
            # 对方正好删除了归还帖子
            Good.batch_update(Good.id == lost_id[0], Good.status == 3, val=updated)

