import requests

from application import app
from common.libs.Helper import datetime2str
from common.libs.mall.WechatService import WeChatService


def send_finished_subscribe(goods_info):
    """
    给归还物品的人 money
    给发布失物招领的人 money
    :return:
    """
    data = {
        "name1": {"value": goods_info.name},
        "thing2": {"value": "认领成功" if goods_info.business_type == 1 else "归还成功"},
        "date4": {"value": datetime2str(goods_info.updated_time)}
    }
    send_subscribe(goods_info.openid, "finished", data)


def send_thank_subscribe(thanks_info):
    """
    给归还物品的人 money
    给发布失物招领的人 money
    :return:
    """
    from common.models.ciwei.Member import Member
    target_member = Member.query.filter_by(id=thanks_info.target_member_id).first()
    member = Member.query.filter_by(id=thanks_info.member_id).first()
    app.logger.warn("答谢者的名字是{},昵称是{}".format(member.name, member.nickname))
    data = {
        "name1": {"value": member.name if member.name else member.nickname},
        "thing2": {"value": thanks_info.goods_name},
        "amount3": {"value": str(thanks_info.thank_price)},
        "date5": {"value": datetime2str(thanks_info.updated_time)}
    }
    send_subscribe(target_member.openid, "thanks", data)


def send_subscribe(openid, template, data):
    """
    向微信用户发送订阅消息的异步任务
    :param openid: 微信用户
    :param template: 模板类型
    :param data: 模板数据
    :return:
    """
    token = WeChatService.get_wx_token()
    url = "https://api.weixin.qq.com/cgi-bin/message/subscribe/send?access_token={}".format(
        token)
    data = {
        "touser": openid,
        "template_id": app.config["SUBSCRIBE_TEMPLATES"][template],
        "data": data
    }
    wx_resp = requests.post(url, json=data).json()
    app.logger.info("完成{}消息 错误码:{} 错误信息：{}".format(template, wx_resp['errcode'], wx_resp['errmsg']))
