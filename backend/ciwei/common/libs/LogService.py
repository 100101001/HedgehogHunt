# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/4/13 下午4:38
@file: LogService.py
@desc: 
"""
import json

from flask import request, g

from application import db
from common.libs.sms.SMSService import PRODUCT_NAME
from common.models.ciwei.logs.change.MemberBalanceChangeLog import MemberBalanceChangeLog
from common.models.ciwei.logs.change.MemberNotifyTimeChangeLog import MemberNotifyTimeChangeLog
from common.models.ciwei.logs.change.MemberPhoneChangeLog import MemberPhoneChangeLog
from common.models.ciwei.logs.change.MemberSmsPkgChangeLog import MemberSmsPkgChangeLog
from common.models.ciwei.logs.change.MemberStatusChangeLog import MemberStatusChangeLog
from common.models.ciwei.logs.thirdservice.AcsSmsSendLog import AcsSmsSendLog
from common.models.ciwei.logs.thirdservice.WechatServerApiLog import WechatServerApiLog
from common.models.ciwei.mall.ProductSaleChangeLog import ProductSaleChangeLog


def setMemberSmsPkgChange(sms_pkg=None, unit=0, old_times=0):
    """
    记录会员通知短信包的次数变化
    :param sms_pkg:
    :param old_times:
    :param unit:
    :return:
    """
    change_log_model = MemberSmsPkgChangeLog()
    change_log_model.member_id = sms_pkg.member_id
    change_log_model.openid = sms_pkg.openid
    change_log_model.pkg_id = sms_pkg.id
    change_log_model.unit = unit
    change_log_model.notify_times = old_times
    change_log_model.note = "短信通知"
    db.session.add(change_log_model)


def setMemberNotifyTimesChange(member_info=None, unit=0, old_times=0):
    """
    记录会员通知次数变化
    :param old_times:
    :param member_info:
    :param unit:
    :return:
    """
    change_log_model = MemberNotifyTimeChangeLog()
    change_log_model.member_id = member_info.id
    change_log_model.openid = member_info.openid
    change_log_model.unit = unit
    change_log_model.notify_times = old_times
    change_log_model.note = "短信充值" if unit > 0 else "短信通知"
    db.session.add(change_log_model)


def setMemberBalanceChange(member_info=None, unit=0, old_balance=0):
    """
    记录会员账户余额变化
    :param old_balance:
    :param member_info:
    :param unit:
    :return:
    """
    change_log_model = MemberBalanceChangeLog()
    change_log_model.member_id = member_info.id
    change_log_model.openid = member_info.openid
    change_log_model.unit = unit
    change_log_model.total_balance = old_balance
    note = request.values.get('note')
    change_log_model.note = note if note else ('答谢赏金' if unit > 0 else '短信通知')
    db.session.add(change_log_model)


def addAcsSmsSendLog(sms_resp=None, phone="", temp_id="", temp_params=None, sign_name="", trig_rcv_info=None):
    """
    添加阿里云短信发送日志
    :param trig_rcv_info:
    :param sms_resp:
    :param phone:
    :param temp_id:
    :param temp_params:
    :param sign_name:
    :return:
    """
    sms_send_log = AcsSmsSendLog()
    # 操作用户信息
    sms_send_log.trig_member_id = trig_rcv_info.get('trig_member_id')
    sms_send_log.rcv_member_id = trig_rcv_info.get('rcv_member_id')
    sms_send_log.trig_openid = trig_rcv_info.get('trig_openid')
    sms_send_log.rcv_openid = trig_rcv_info.get('rcv_openid')
    # 三方业务数据信息
    sms_send_log.sign_name = sign_name
    sms_send_log.template_id = temp_id
    sms_send_log.params = json.dumps(temp_params)
    sms_send_log.phone_number = phone
    sms_send_log.biz_uuid = sms_resp.get('business_sn')
    sms_send_log.acs_request_id = sms_resp.get('RequestId')
    sms_send_log.acs_biz_id = sms_resp.get('BizId', '')
    sms_send_log.acs_code = sms_resp.get('Code')
    sms_send_log.acs_product_name = PRODUCT_NAME
    sms_resp.pop('business_sn')
    sms_send_log.acs_resp_data = json.dumps(sms_resp)
    db.session.add(sms_send_log)
    db.session.commit()


def addWechatApiCallLog(url='', token='', req_data=None, resp_data=None):
    """
    微信服务端API调用日志
    :param url:
    :param token:
    :param req_data:
    :param resp_data:
    :return:
    """
    api_log_model = WechatServerApiLog()
    api_log_model.url = url
    api_log_model.token = token
    api_log_model.req_data = json.dumps(req_data)
    api_log_model.resp_data = json.dumps(resp_data)
    db.session.add(api_log_model)
    db.session.commit()


def setMemberStatusChange(member_info=None, user_id=0, old_status=0, new_status=0, stuff_id=0, stuff_type=-1,
                          note="恶意发帖"):
    """
    记录会员账户状态变化
    :param stuff_type:
    :param stuff_id:
    :param user_id:
    :param new_status:
    :param old_status:
    :param member_info:
    :param note:
    :return:
    """
    change_log_model = MemberStatusChangeLog()
    change_log_model.user_id = user_id
    change_log_model.stuff_id = stuff_id
    change_log_model.stuff_type = stuff_type  # 物品或者答谢
    change_log_model.member_id = member_info.id
    change_log_model.openid = member_info.openid
    change_log_model.old_status = old_status
    change_log_model.new_status = new_status
    change_log_model.note = note
    db.session.add(change_log_model)


def setMemberMobileChange(member_info=None, new_mobile='', old_mobile=''):
    """
    用户手机变更记录
    :param member_info:
    :param new_mobile:
    :param old_mobile:
    :return:
    """
    change_log_model = MemberPhoneChangeLog()
    change_log_model.member_id = member_info.id
    change_log_model.openid = member_info.openid
    change_log_model.new_mobile = new_mobile
    change_log_model.old_mobile = old_mobile
    db.session.add(change_log_model)



def setProductSaleChange(product_id=0, product_num=0):
    """
    产品销售变更日志
    :param product_id:
    :param product_num:
    :return:
    """
    sale_log = ProductSaleChangeLog()
    sale_log.product_id = product_id
    sale_log.quantity = product_num
    sale_log.price = product_id * product_num
    sale_log.member_id = getattr(g.member_info, 'id', 0)
    db.session.add(sale_log)


