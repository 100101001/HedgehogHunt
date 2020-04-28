# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/3/25 下午2:02
@file: SMSService.py
@desc: 
"""

import random

from common.libs import LogService
from common.libs.sms.aliyunsdkdysmsapi.request.v20170525 import SendSmsRequest
import json
from aliyunsdkcore.client import AcsClient
import uuid
from aliyunsdkcore.profile import region_provider
from aliyunsdkcore.http import method_type as MT
from application import app
from common.models.ciwei.logs.thirdservice.AcsSmsSendLog import AcsSmsSendLog


# 注意：不要更改
REGION = "cn-hangzhou"
PRODUCT_NAME = "Dysmsapi"
DOMAIN = "dysmsapi.aliyuncs.com"
ACS_CONSTANTS = app.config['ACS_SMS']

acs_client = AcsClient(ACS_CONSTANTS['ACCESS_KEY_ID'], ACS_CONSTANTS['ACCESS_KEY_SECRET'], REGION)
region_provider.add_endpoint(PRODUCT_NAME, REGION, DOMAIN)


def send_sms(business_id=None, phone_numbers='', sign_name='', template_code='', template_param=None):
    smsRequest = SendSmsRequest.SendSmsRequest()
    # 申请的短信模板编码,必填
    smsRequest.set_TemplateCode(template_code)

    # 短信模板变量参数
    if template_param is not None:
        smsRequest.set_TemplateParam(template_param)

    # 设置业务请求流水号，必填。
    smsRequest.set_OutId(business_id)

    # 短信签名
    smsRequest.set_SignName(sign_name)

    # 数据提交方式
    smsRequest.set_method(MT.POST)

    # 数据提交格式
    # smsRequest.set_accept_format(FT.JSON)

    # 短信发送的号码列表，必填。
    smsRequest.set_PhoneNumbers(phone_numbers)

    # 调用短信发送接口，返回json
    smsResponse = acs_client.do_action_with_exception(smsRequest)

    app.logger.info(smsResponse)
    return json.loads(smsResponse)


def send_verify_code(phone="", code="", trig_rcv_info=None):
    """
    发送短信，返回响应数据
    :param trig_rcv_info:
    :param phone:
    :param code:
    :return:
    """
    if not phone or not code:
        return False
    _business_id = genBizUUid()
    params = {"code": code}
    temp_id = ACS_CONSTANTS['TEMP_IDS']['VERIFY']
    sign_name = ACS_CONSTANTS['SIGN_NAMES']['VERIFY']
    resp = send_sms(business_id=_business_id, phone_numbers=phone, sign_name=sign_name,
                    template_code=temp_id, template_param=params)
    resp['business_sn'] = _business_id
    # TODO 如果能够保证消息队列处理的可靠可以异步
    LogService.addAcsSmsSendLog(sms_resp=resp, phone=phone, temp_id=temp_id, temp_params=params, sign_name=sign_name, trig_rcv_info=trig_rcv_info)
    return resp and 'Code' in resp and resp['Code'] == 'OK'


def send_lost_notify(phone='', goods_name='', location=None, trig_rcv_info=None):
    """
    发送失物通知
    :param trig_rcv_info:
    :param phone:
    :param goods_name:
    :param location:
    :return:
    """
    if not phone or not goods_name or not location:
        return False

    _business_id = genBizUUid()
    params = {
        'goods_name': goods_name,
        'location': location
    }
    temp_id = ACS_CONSTANTS['TEMP_IDS']['NOTIFY']
    sign_name = ACS_CONSTANTS['SIGN_NAMES']['NOTIFY']
    resp = send_sms(business_id=_business_id, phone_numbers=phone, sign_name=sign_name,
                    template_code=temp_id, template_param=params)
    resp['business_sn'] = str(_business_id)
    # TODO 如果能够保证消息队列处理的可靠可以异步
    LogService.addAcsSmsSendLog(sms_resp=resp, phone=phone, temp_id=temp_id, temp_params=params, sign_name=sign_name, trig_rcv_info=trig_rcv_info)
    return resp and 'Code' in resp and resp['Code'] == 'OK'


def generate_sms_code():
    """
    生成6位验证码
    :return: 码
    """
    code = []
    for i in range(6):
        code.append(str(random.randint(0, 9)))
    return ''.join(code)


def genBizUUid():
    while True:
        bid = uuid.uuid1()
        log = AcsSmsSendLog.query.filter_by(biz_uuid=str(bid)).first()
        if log is None:
            break
    return bid


