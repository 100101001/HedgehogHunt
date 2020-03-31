# -*- coding: utf-8 -*-
import decimal
import hashlib
import json
import random
import time

from flask import g

from application import db
from common.libs.Helper import getCurrentDate, seconds2str
from common.libs.MemberService import MemberService
from common.libs.mall.ProductService import ProductService
from common.models.ciwei.BalanceOder import BalanceOrder
from common.models.ciwei.BalanceOrderCallbackData import BalanceOrderCallbackData
from common.models.ciwei.GoodsTopOrder import GoodsTopOrder
from common.models.ciwei.GoodsTopOrderCallbackData import GoodsTopOrderCallbackData
from common.models.ciwei.ThankOrder import ThankOrder
from common.models.ciwei.ThankOrderCallbackData import ThankOrderCallbackData
from common.models.ciwei.mall.Order import Order
from common.models.ciwei.mall.OrderCallBackData import OrderCallbackData
from common.models.ciwei.mall.OrderProduct import OrderProduct
from common.models.ciwei.mall.Product import Product
from common.models.ciwei.mall.ProductSaleChangeLog import ProductSaleChangeLog


class PayService:

    def __init__(self):
        pass

    def createOrder(self, member_id, items=None, params=None):
        """
        创建Order,OderProduct,更新Product库存
        记录商品库存&销售日志
        :param member_id:
        :param items:
        :param params:
        :return: 订单id,流水号,待支付价格
        """
        resp = {'code': 200, 'msg': '操作成功~', 'data': {}}

        # 总价=运费+商品价格
        pay_price = decimal.Decimal(0.00)
        continue_cnt = 0
        product_ids = []
        for item in items:
            if decimal.Decimal(item['price']) < 0:
                continue_cnt += 1
                continue

            pay_price = pay_price + decimal.Decimal(item['price']) * int(item['number'])
            product_ids.append(item['id'])

        if continue_cnt >= len(items):
            resp['code'] = -1
            resp['msg'] = '商品items为空~~'
            return resp

        yun_price = params['yun_price'] if params and 'yun_price' in params else 0
        discount_price = params['discount_price'] if params and 'discount_price' in params else 0
        discount_type = params['discount_type'] if params and 'discount_type' in params else ''
        note = params['note'] if params and 'note' in params else ''
        express_address_id = params['express_address_id'] if params and 'express_address_id' in params else 0
        express_info = params['express_info'] if params and 'express_info' in params else {}
        yun_price = decimal.Decimal(yun_price)
        discount_price = decimal.Decimal(discount_price)
        total_price = pay_price + yun_price - discount_price

        # 执行事务：新增Order和OrderProduct，更新Product库存
        # 新增ProductSaleChangeLog和ProductStockChangeLog
        # 库存更新悲观锁并发控制
        try:
            tmp_product_list = db.session.query(Product).filter(Product.id.in_(product_ids)) \
                .with_for_update().all()

            tmp_food_stock_mapping = {}
            for tmp_item in tmp_product_list:
                tmp_food_stock_mapping[tmp_item.id] = tmp_item.stock_cnt

            model_order = Order()
            model_order.order_sn = self.geneOrderSn()
            model_order.member_id = member_id
            model_order.total_price = total_price
            model_order.yun_price = yun_price
            model_order.pay_price = pay_price
            model_order.discount_price = discount_price
            model_order.discount_type = discount_type
            model_order.note = note
            model_order.status = -8
            model_order.express_status = -8
            model_order.express_address_id = express_address_id
            model_order.express_info = json.dumps(express_info)
            model_order.updated_time = model_order.created_time = getCurrentDate()
            db.session.add(model_order)

            for item in items:
                tmp_left_stock = tmp_food_stock_mapping[item['id']]

                if decimal.Decimal(item['price']) < 0:
                    continue

                if int(item['number']) > int(tmp_left_stock):
                    raise Exception("您购买的这美食太火爆了，剩余：%s,你购买%s~~" % (tmp_left_stock, item['number']))

                tmp_ret = Product.query.filter_by(id=item['id']).update({
                    "stock_cnt": int(tmp_left_stock) - int(item['number'])
                })
                if not tmp_ret:
                    raise Exception("下单失败请重新下单")

                tmp_order_item = OrderProduct()
                tmp_order_item.order_id = model_order.id
                tmp_order_item.member_id = member_id
                tmp_order_item.product_num = item['number']
                tmp_order_item.price = item['price']
                tmp_order_item.product_id = item['id']
                tmp_order_item.note = note
                tmp_order_item.updated_time = tmp_order_item.created_time = getCurrentDate()
                db.session.add(tmp_order_item)
                # db.session.flush()

                ProductService.setStockChangeLog(item['id'], -item['number'], "在线购买")
            db.session.commit()
            resp['data'] = {
                'id': model_order.id,
                'order_sn': model_order.order_sn,
                'total_price': str(total_price)
            }
        except Exception as e:
            db.session.rollback()
            print(e)
            resp['code'] = -1
            resp['msg'] = "下单失败请重新下单"
            resp['msg'] = str(e)
            return resp
        return resp

    def closeOrder(self, pay_order_id=0):
        """
        关单数据操作：日志, Order状态,库存
        :param pay_order_id:
        :return:
        """
        if pay_order_id < 1:
            return False
        order_info = Order.query.filter_by(id=pay_order_id, status=-8).first()
        if not order_info:
            return False

        # 更新Product库存,日志,更新Order状态
        order_items = OrderProduct.query.filter_by(order_id=pay_order_id).all()
        if order_items:
            for item in order_items:
                tmp_product_info = Product.query.filter_by(id=item.product_id).first()
                if tmp_product_info:
                    tmp_product_info.stock_cnt = tmp_product_info.stock_cnt + item.product_num
                    tmp_product_info.updated_time = getCurrentDate()
                    db.session.add(tmp_product_info)
                    db.session.commit()
                    ProductService.setStockChangeLog(item.product_id, item.product_num, "订单取消")

        order_info.status = 0
        order_info.updated_time = getCurrentDate()
        db.session.add(order_info)
        db.session.commit()
        return True

    def orderSuccess(self, pay_order_id=0, params=None):
        """
        支付成功后,更新订单状态,记录销售日志,根据折扣类型扣除用户余额
        消息提醒队列
        :param pay_order_id:
        :param params:
        :return: 数据库操作成功
        """
        try:
            # 更新Order支付状态与物流状态
            # 该订单的商品销售日志
            order_info = Order.query.filter_by(id=pay_order_id).first()
            if not order_info or order_info.status not in [-8, -7]:
                return True

            order_info.pay_sn = params['pay_sn'] if params and 'pay_sn' in params else ''
            order_info.status = 1
            order_info.express_status = -7
            order_info.updated_time = getCurrentDate()
            db.session.add(order_info)

            pay_order_items = OrderProduct.query.filter_by(order_id=pay_order_id).all()
            for order_item in pay_order_items:
                tmp_product = Product.query.filter_by(id=order_item.product_id).first()
                tmp_product.sale_cnt += order_item.product_num
                db.session.add(tmp_product)
                tmp_model_sale_log = ProductSaleChangeLog()
                tmp_model_sale_log.product_id = order_item.product_id
                tmp_model_sale_log.quantity = order_item.product_num
                tmp_model_sale_log.price = order_item.price
                tmp_model_sale_log.member_id = order_item.member_id
                tmp_model_sale_log.created_time = getCurrentDate()
                db.session.add(tmp_model_sale_log)

            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(e)
            return False

        return True

    def goodsTopOrderSuccess(self, pay_order_id=0, params=None):
        """
        支付成功后,更新订单状态
        :param pay_order_id:
        :param params:
        :return: 数据库操作成功
        """

        # 更新TopOrder支付状态
        order_info = GoodsTopOrder.query.filter_by(id=pay_order_id).first()
        if not order_info or order_info.status not in [0]:
            return True
        order_info.transaction_id = params['pay_sn'] if params and 'pay_sn' in params else ''
        order_info.status = 1
        order_info.updated_time = getCurrentDate()
        order_info.paid_time = params['paid_time'] if params and 'paid_time' in params else getCurrentDate()
        db.session.add(order_info)
        db.session.commit()
        return True

    def thankOrderSuccess(self, pay_order_id=0, params=None):
        """
        支付成功后,更新订单状态
        :param pay_order_id:
        :param params:
        :return: 数据库操作成功
        """

        # 更新ThankOrder支付状态
        order_info = ThankOrder.query.filter_by(id=pay_order_id).first()
        if not order_info or order_info.status not in [0]:
            return True
        order_info.transaction_id = params['pay_sn'] if params and 'pay_sn' in params else ''
        order_info.status = 1
        order_info.updated_time = getCurrentDate()
        order_info.paid_time = params['paid_time'] if params and 'paid_time' in params else getCurrentDate()
        db.session.add(order_info)
        db.session.commit()
        return True

    def balanceOrderSuccess(self, pay_order_id=0, params=None):
        """
        支付成功后,更新订单状态
        :param pay_order_id:
        :param params:
        :return: 数据库操作成功
        """
        # 更新BalanceOrder支付状态
        order_info = BalanceOrder.query.filter_by(id=pay_order_id).first()
        if not order_info or order_info.status not in [0]:
            return True
        order_info.transaction_id = params['pay_sn'] if params and 'pay_sn' in params else ''
        order_info.status = 1
        order_info.updated_time = getCurrentDate()
        order_info.paid_time = params['paid_time'] if params and 'paid_time' in params else getCurrentDate()
        db.session.add(order_info)
        db.session.commit()
        return True

    def addPayCallbackData(self, pay_order_id=0, type='pay', data=''):
        """
        微信支付回调记录
        :param pay_order_id:
        :param type:
        :param data:
        :return:
        """
        # 新增
        model_callback = OrderCallbackData()
        model_callback.order_id = pay_order_id
        if type == "pay":
            model_callback.pay_data = data
            model_callback.refund_data = ''
        else:
            model_callback.refund_data = data
            model_callback.pay_data = ''

        model_callback.created_time = model_callback.updated_time = getCurrentDate()
        db.session.add(model_callback)
        db.session.commit()
        return True

    def addGoodsTopPayCallbackData(self, pay_order_id=0, type='pay', data=''):
        """
        微信支付回调记录
        :param pay_order_id:
        :param type:
        :param data:
        :return:
        """
        # 新增
        model_callback = GoodsTopOrderCallbackData()
        model_callback.top_order_id = pay_order_id
        if type == "pay":
            model_callback.pay_data = data
            model_callback.refund_data = ''
        else:
            model_callback.refund_data = data
            model_callback.pay_data = ''

        model_callback.created_time = model_callback.updated_time = getCurrentDate()
        db.session.add(model_callback)
        db.session.commit()
        return True

    def addThankPayCallbackData(self, pay_order_id=0, type='pay', data=''):
        """
        微信支付回调记录
        :param pay_order_id:
        :param type:
        :param data:
        :return:
        """
        # 新增
        model_callback = ThankOrderCallbackData()
        model_callback.thank_order_id = pay_order_id
        if type == "pay":
            model_callback.pay_data = data
            model_callback.refund_data = ''
        else:
            model_callback.refund_data = data
            model_callback.pay_data = ''

        model_callback.created_time = model_callback.updated_time = getCurrentDate()
        db.session.add(model_callback)
        db.session.commit()
        return True

    def addBalancePayCallbackData(self, pay_order_id=0, type='pay', data=''):
        """
        微信支付回调记录
        :param pay_order_id:
        :param type:
        :param data:
        :return:
        """
        # 新增
        model_callback = BalanceOrderCallbackData()
        model_callback.balance_order_id = pay_order_id
        if type == "pay":
            model_callback.pay_data = data
            model_callback.refund_data = ''
        else:
            model_callback.refund_data = data
            model_callback.pay_data = ''

        model_callback.created_time = model_callback.updated_time = getCurrentDate()
        db.session.add(model_callback)
        db.session.commit()
        return True

    def geneOrderSn(self):
        """
        :return:不重复的流水号
        """
        m = hashlib.md5()
        sn = None
        while True:
            # 毫秒级时间戳-千万随机数
            sn_str = "%s-%s" % (int(round(time.time() * 1000)), random.randint(0, 9999999))
            m.update(sn_str.encode("utf-8"))
            sn = m.hexdigest()
            if not Order.query.filter_by(order_sn=sn).first():
                break
        return sn

    def geneGoodsTopOrderSn(self):
        """
        :return:不重复的流水号
        """
        m = hashlib.md5()
        sn = None
        while True:
            # 毫秒级时间戳-千万随机数
            sn_str = "%s-%s" % (int(round(time.time() * 1000)), random.randint(0, 9999999))
            m.update(sn_str.encode("utf-8"))
            sn = m.hexdigest()
            if not GoodsTopOrder.query.filter_by(order_sn=sn).first():
                break
        return sn

    def geneThankOrderSn(self):
        """
        :return:不重复的流水号
        """
        m = hashlib.md5()
        sn = None
        while True:
            # 毫秒级时间戳-千万随机数
            sn_str = "%s-%s" % (int(round(time.time() * 1000)), random.randint(0, 9999999))
            m.update(sn_str.encode("utf-8"))
            sn = m.hexdigest()
            if not ThankOrder.query.filter_by(order_sn=sn).first():
                break
        return sn

    def geneBalanceOrderSn(self):
        """
        :return:不重复的流水号
        """
        m = hashlib.md5()
        sn = None
        while True:
            # 毫秒级时间戳-千万随机数
            sn_str = "%s-%s" % (int(round(time.time() * 1000)), random.randint(0, 9999999))
            m.update(sn_str.encode("utf-8"))
            sn = m.hexdigest()
            if not BalanceOrder.query.filter_by(order_sn=sn).first():
                break
        return sn

    def autoCloseOrder(self, member_id=0):
        """
        自动关单
        :param member_id:
        :return:
        """
        order_list = Order.query.filter(Order.member_id == member_id, Order.status == -8,
                                        Order.updated_time <= seconds2str(time.time() - 1800)).all()
        member_info = g.member_info
        for order in order_list:
            self.closeOrder(pay_order_id=order.id)
            if order.discount_price != 0:
                member_info.balance += order.discount_price
                db.session.add(member_info)
                db.session.commit()
