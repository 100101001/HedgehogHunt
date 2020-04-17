# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/4/12 下午11:01
@file: SmsTasks.py
@desc: 
"""

import datetime
from decimal import Decimal

from application import celery, db
from common.libs import LogService
from common.libs.CryptService import Cipher
from common.libs.sms import SMSService
from common.libs.sms.SMSService import ACS_CONSTANTS
from common.models.ciwei.Member import Member
from common.models.ciwei.MemberSmsPkg import MemberSmsPkg
from common.models.ciwei.logs.thirdservice.AcsSmsSendLog import AcsSmsSendLog


@celery.task(name="sms.notify_qrcode_owner")
def notifyQrcodeOwner(params=None):
    """
    通知失主
    :return:
    """
    if not params:
        return "NO PARAMS"
    # 物品信息
    put_location = params.get('location', '')
    goods_name = params.get('goods_name', '')
    if not put_location or not goods_name:
        return "NO GOODS_INFO"
    put_location = put_location.split("###")
    if len(put_location) != 4:
        return "NO LOCATION"
    # 收发信息
    trig_member_id = params.get('trig_member_id', 0)
    trig_openid = params.get('trig_openid', '')
    rcv_openid = params.get('rcv_openid', '')
    if not rcv_openid or not trig_member_id or not trig_openid:
        return "NO RCV_TRIG"
    # 有效用户
    rcv_member_info = Member.query.filter_by(openid=rcv_openid, status=1).first()
    if rcv_member_info is None:
        print("NO USER")
        return "NO USER"

    now = datetime.datetime.now()
    # 判断是否发送短信
    # 频率对 TODO 是否改成用户允许的频率
    recent_rcv_notify = AcsSmsSendLog.query.filter(AcsSmsSendLog.rcv_openid == rcv_openid,
                                     AcsSmsSendLog.template_id == ACS_CONSTANTS['TEMP_IDS']['NOTIFY'],
                                     AcsSmsSendLog.acs_code == "OK",
                                     AcsSmsSendLog.created_time >= now - datetime.timedelta(minutes=1)).first()
    if recent_rcv_notify:
        # 一周只发一次失物通知
        return "TOO FREQ"

    # 有钱
    op_status = 0  # 扣短信包通知次数
    rcv_member_pkg = MemberSmsPkg.query.filter(MemberSmsPkg.open_id == rcv_openid,
                                    MemberSmsPkg.expired_time <= now,
                                    MemberSmsPkg.left_notify_times > 0).first()
    if not rcv_member_pkg:
        if rcv_member_info.left_notify_times > 0:
            # 扣用户通知次数
            op_status = 1
        elif rcv_member_info.balance >= Decimal('0.10'):
            # 扣用户余额
            op_status = 2
        else:
            # 没钱88
            return "NO MONEY"

    if rcv_member_info:
        # 取出解密后的手机
        mobile = Cipher.decrypt(text=rcv_member_info.mobile)
        trig_rcv_info = {
            'trig_member_id': trig_member_id,
            'trig_openid': trig_openid,
            'rcv_openid': rcv_openid,
            'rcv_member_id': rcv_member_info.id
        }
        send_ok = SMSService.send_lost_notify(phone=mobile, goods_name=goods_name,
                                              location=put_location, trig_rcv_info=trig_rcv_info)
        if send_ok:
            if op_status == 0:
                LogService.setMemberSmsPkgChange(sms_pkg=rcv_member_pkg, unit=-1, old_times=rcv_member_pkg.left_notify_times, note="失物通知")
                rcv_member_pkg.left_notify_times -= 1
                db.session.add(rcv_member_pkg)
            elif op_status == 1:
                LogService.setMemberNotifyTimesChange(member_info=rcv_member_info, unit=-1, old_times=rcv_member_info.left_notify_times, note="失物通知")
                rcv_member_info.left_notify_times -= 1
                db.session.add(rcv_member_info)
            elif op_status == 2:
                LogService.setMemberBalanceChange(member_info=rcv_member_info, unit=-Decimal("0.10"))
                rcv_member_info.balance -= Decimal("0.10")
                db.session.add(rcv_member_info)

    db.session.commit()
    return "OK"
