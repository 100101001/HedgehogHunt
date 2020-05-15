# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/4/12 下午11:01
@file: SmsTasks.py
@desc: 
"""

from application import celery, db
from common.libs.sms.SmsNotifyService import SmsNotifyHandler


@celery.task(name="sms.notify_qrcode_owner", ignore_result=True)
def notifyQrcodeOwner(params=None):
    """
    通知失主
    :return:
    """
    if not params:
        return
    # 物品信息
    put_location = params.get('location')
    goods_name = params.get('goods_name')
    if not put_location or not goods_name:
        return
    put_location = put_location.split("###")
    if len(put_location) != 4:
        return
    # 收发信息
    trig_rcv = params.get('trig_rcv')
    rcv_openid = trig_rcv.get('rcv_openid')
    handler = SmsNotifyHandler(openid=rcv_openid)
    # 判断是否发送短信
    # if not handler.validUser() or handler.tooFreq() or not handler.hasCharger():
    #     return
    if handler.validUser() and not handler.tooFreq():
        handler.sendSmsNotify(goods_name=goods_name, location=put_location, trig_rcv=trig_rcv)
        db.session.commit()
    # send_ok = handler.sendSmsNotify(goods_name=goods_name, location=put_location, trig_rcv=trig_rcv)
    # if send_ok:
    #     handler.charge()
    # db.session.commit()


