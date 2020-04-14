# -*- coding: utf-8 -*-
import datetime
import decimal
import hashlib
import json
import random
import time

from application import db
from common.libs.Helper import getCurrentDate
from common.libs.mall.ProductService import ProductService
from common.models.ciwei.BalanceOder import BalanceOrder
from common.models.ciwei.logs.thirdservice.BalanceOrderCallbackData import BalanceOrderCallbackData
from common.models.ciwei.GoodsTopOrder import GoodsTopOrder
from common.models.ciwei.logs.thirdservice.GoodsTopOrderCallbackData import GoodsTopOrderCallbackData
from common.models.ciwei.Member import Member
from common.models.ciwei.ThankOrder import ThankOrder
from common.models.ciwei.logs.thirdservice.ThankOrderCallbackData import ThankOrderCallbackData
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
            # 筛查下单参数
            if decimal.Decimal(item['price']) < 0:
                continue_cnt += 1
                continue

            pay_price = pay_price + decimal.Decimal(item['price']) * int(item['number'])
            product_ids.append(item['id'])

        if continue_cnt >= len(items):
            resp['code'] = -1
            resp['msg'] = '商品items为空~~'
            return resp

        yun_price = params.get('yun_price', 0)  # 运费
        discount_price = params.get('discount_price', 0)  # 折扣
        discount_type = params.get('discount_type', '')  # 折扣类型
        note = params.get('note', '')  # 备注
        express_address_id = params.get('express_address_id', 0)  # 快递地址
        express_info = params.get('express_info', {})  # 收货信息

        # 计算总价，使用decimal精确计算
        yun_price = decimal.Decimal(yun_price)  # 运费转换
        discount_price = decimal.Decimal(discount_price)  # 折扣转换
        total_price = pay_price + yun_price - discount_price

        # 执行事务：下订单，和订单列表
        # 更新订单包含产品的库存，库存更新悲观锁并发控制
        # 记录库存变化日志
        try:
            tmp_product_list = db.session.query(Product).filter(Product.id.in_(product_ids)) \
                .with_for_update().all()

            tmp_product_stock_mapping = {}
            for tmp_item in tmp_product_list:
                tmp_product_stock_mapping[tmp_item.id] = tmp_item.stock_cnt

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
                # 下单前产品剩余的库存数
                tmp_left_stock = tmp_product_stock_mapping[item['id']]

                if decimal.Decimal(item['price']) < 0:
                    continue

                # 库存不足
                if int(item['number']) > int(tmp_left_stock):
                    raise Exception("您购买的商品太火爆了，剩余：%s,你购买%s~~" % (tmp_left_stock, item['number']))
                # 库存更新
                tmp_ret = Product.query.filter_by(id=item['id']).update({
                    "stock_cnt": int(tmp_left_stock) - int(item['number'])
                })
                if not tmp_ret:
                    raise Exception("下单失败请重新下单")

                # 库存
                tmp_order_item = OrderProduct()
                tmp_order_item.order_id = model_order.id
                tmp_order_item.member_id = member_id
                tmp_order_item.product_num = item['number']
                tmp_order_item.price = item['price']
                tmp_order_item.product_id = item['id']
                tmp_order_item.note = note
                tmp_order_item.updated_time = tmp_order_item.created_time = getCurrentDate()
                db.session.add(tmp_order_item)

                ProductService.setStockChangeLog(product_id=item['id'], quantity=-int(item['number']), note="在线购买",
                                                 stock_cnt=tmp_left_stock)
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

    def closeOrder(self, order_id=0):
        """
        关单数据操作：日志, Order状态=>0,库存
        :param order_id: 订单ID
        :return: 是否关单成功
        """
        if order_id < 1:
            return False
        order_info = Order.query.filter_by(id=order_id, status=-8).first()
        if not order_info:
            return False

        # 更新关闭订单中的Product库存
        order_items = OrderProduct.query.filter_by(order_id=order_id).all()
        if order_items:
            for item in order_items:
                tmp_product_info = Product.query.filter_by(id=item.product_id).with_for_update().first()
                if tmp_product_info:
                    # 加回库存
                    stock_cnt_before_change = tmp_product_info.stock_cnt
                    tmp_product_info.stock_cnt = stock_cnt_before_change + item.product_num
                    db.session.add(tmp_product_info)
                    db.session.commit()
                    # 库存变更日志
                    ProductService.setStockChangeLog(product_id=item.product_id, quantity=item.product_num,
                                                     note="订单取消", stock_cnt=stock_cnt_before_change)

        # 更新Order状态 => 0
        order_info.status = 0
        db.session.add(order_info)
        db.session.commit()

        # 用户余额增回
        if order_info.discount_type == "账户余额":
            # 用户余额加回事物
            member_info = Member.query.filter_by(id=order_info.member_id).first()
            if member_info:
                member_info.balance += order_info.discount_price
                db.session.add(member_info)
                db.session.commit()

        return True

    def orderSuccess(self, order_id=0, params=None):
        """
        支付成功后,更新订单状态,记录销售日志,根据折扣类型扣除用户余额
        消息提醒队列
        :param order_id:
        :param params:
        :return: 数据库操作成功
        """
        try:
            # 更新Order支付状态与物流状态
            # 该订单的商品销售日志
            order_info = Order.query.filter_by(id=order_id).first()
            if not order_info or order_info.status not in [-8, -7]:
                return True

            order_info.pay_sn = params.get('pay_sn', '')
            order_info.status = 1
            order_info.express_status = -7
            db.session.add(order_info)

            order_items = OrderProduct.query.filter_by(order_id=order_id).all()
            for order_item in order_items:
                # 产品的销售数
                tmp_product = Product.query.filter_by(id=order_item.product_id).first()
                tmp_product.sale_cnt += order_item.product_num
                db.session.add(tmp_product)
                # 销售日志
                tmp_model_sale_log = ProductSaleChangeLog()
                tmp_model_sale_log.product_id = order_item.product_id
                tmp_model_sale_log.quantity = order_item.product_num
                tmp_model_sale_log.price = order_item.price
                tmp_model_sale_log.member_id = order_item.member_id
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
        order_info.transaction_id = params.get('pay_sn', '')
        order_info.status = 1
        order_info.paid_time = params.get('paid_time', getCurrentDate())
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
        order_info.transaction_id = params.get('pay_sn', '')
        order_info.status = 1
        order_info.paid_time = params.get('paid_time', getCurrentDate())
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
        order_info.transaction_id = params.get('pay_sn', '')
        order_info.status = 1
        order_info.paid_time = params.get('paid_time', getCurrentDate())
        db.session.add(order_info)
        db.session.commit()
        return True

    def addPayCallbackData(self, pay_order_id=0, callback_type='pay', data=''):
        """
        微信支付回调记录
        :param pay_order_id:
        :param callback_type:
        :param data:
        :return:
        """
        # 新增
        model_callback = OrderCallbackData()
        model_callback.order_id = pay_order_id
        if callback_type == "pay":
            model_callback.pay_data = data
            model_callback.refund_data = ''
        else:
            model_callback.refund_data = data
            model_callback.pay_data = ''

        db.session.add(model_callback)
        db.session.commit()
        return True

    def addGoodsTopPayCallbackData(self, pay_order_id=0, callback_type='pay', data=''):
        """
        微信支付回调记录
        :param pay_order_id:
        :param callback_type:
        :param data:
        :return:
        """
        # 新增
        model_callback = GoodsTopOrderCallbackData()
        model_callback.top_order_id = pay_order_id
        if callback_type == "pay":
            model_callback.pay_data = data
            model_callback.refund_data = ''
        else:
            model_callback.refund_data = data
            model_callback.pay_data = ''

        db.session.add(model_callback)
        db.session.commit()
        return True

    def addThankPayCallbackData(self, pay_order_id=0, callback_type='pay', data=''):
        """
        微信支付回调记录
        :param pay_order_id:
        :param callback_type:
        :param data:
        :return:
        """
        # 新增
        model_callback = ThankOrderCallbackData()
        model_callback.thank_order_id = pay_order_id
        if callback_type == "pay":
            model_callback.pay_data = data
            model_callback.refund_data = ''
        else:
            model_callback.refund_data = data
            model_callback.pay_data = ''

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
                                        Order.updated_time <= datetime.datetime.now() - datetime.timedelta(
                                            seconds=1800)).all()
        for order in order_list:
            self.closeOrder(order_id=order.id)

Pay = PayService()