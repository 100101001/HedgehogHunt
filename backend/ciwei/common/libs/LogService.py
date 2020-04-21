# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/4/13 下午4:38
@file: LogService.py
@desc: 
"""
import json

from application import db
from common.libs.sms.SMSService import PRODUCT_NAME
from common.models.ciwei.logs.change.MemberBalanceChangeLog import MemberBalanceChangeLog
from common.models.ciwei.logs.change.MemberNotifyTimeChangeLog import MemberNotifyTimeChangeLog
from common.models.ciwei.logs.change.MemberSmsPkgChangeLog import MemberSmsPkgChangeLog
from common.models.ciwei.logs.thirdservice.AcsSmsSendLog import AcsSmsSendLog
from common.models.ciwei.logs.thirdservice.WechatServerApiLog import WechatServerApiLog


def setMemberSmsPkgChange(sms_pkg=None, unit=0, old_times=0, note="答谢"):
    """
    记录会员通知短信包的次数变化
    :param sms_pkg:
    :param old_times:
    :param unit:
    :param note:
    :return:
    """
    change_log_model = MemberSmsPkgChangeLog()
    change_log_model.member_id = sms_pkg.member_id
    change_log_model.openid = sms_pkg.openid
    change_log_model.pkg_id = sms_pkg.id
    change_log_model.unit = unit
    change_log_model.notify_times = old_times
    change_log_model.note = note
    db.session.add(change_log_model)


def setMemberNotifyTimesChange(member_info=None, unit=0, old_times=0, note="答谢"):
    """
    记录会员通知次数变化
    :param old_times:
    :param member_info:
    :param unit:
    :param note:
    :return:
    """
    change_log_model = MemberNotifyTimeChangeLog()
    change_log_model.member_id = member_info.id
    change_log_model.openid = member_info.openid
    change_log_model.unit = unit
    change_log_model.notify_times = old_times
    change_log_model.note = note
    db.session.add(change_log_model)


def setMemberBalanceChange(member_info=None, unit=0, old_balance=0, note="答谢"):
    """
    记录会员账户余额变化
    :param old_balance:
    :param member_info:
    :param unit:
    :param note:
    :return:
    """
    change_log_model = MemberBalanceChangeLog()
    change_log_model.member_id = member_info.id
    change_log_model.openid = member_info.openid
    change_log_model.unit = unit
    change_log_model.total_balance = old_balance
    change_log_model.note = note
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