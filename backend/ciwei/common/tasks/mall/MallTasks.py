# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/4/12 下午3:35
@file: MallTasks.py
@desc: 
"""
import datetime

from application import celery
from common.libs.mall.PayService import Pay
from common.models.ciwei.mall.Order import Order


@celery.task(name="mall.auto_close_expire_order")
def auto_close_expire_order():
    """
    定时关单的任务
    :return:
    """
    # 取出所有超时未支付的订单
    time_threshold = datetime.datetime.now() - datetime.timedelta(seconds=1800)
    order_list = Order.query.filter(Order.status == -8,
                                    Order.updated_time <= time_threshold).all()
    for order in order_list:
        # 关闭订单的事物
        Pay.closeOrder(order_id=order.id)

