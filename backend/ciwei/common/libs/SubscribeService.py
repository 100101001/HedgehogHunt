import requests

from application import app
from common.libs.Helper import datetime2str
from common.libs.mall.WechatService import WeChatService


def send_recommend_subscribe(goods_info):
    """
    新帖发布时，对首次匹配成功的帖子，发送一个订阅消息，给捡到东西的用户成就感，丢了东西的用户app有用的感觉
    :return:
    """

    # 只在第一次会告知有匹配的
    goods_info.recommended_times += 1
    if goods_info.recommended_times > 1:
        return

    data = {
            "thing1": {"value": "有人丢了你捡到的东西了!" if goods_info.business_type == 1 else "有人捡到你丢的东西了!"},
            "thing2": {"value": goods_info.name},
            "thing3": {"value": datetime2str(goods_info.created_time)}
    }
    print(data)
    send_subscribe(goods_info.openid, "recommend", data)


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
    member = Member.query.filter_by(id=thanks_info.target_member_id).first()
    data = {
        "name1": thanks_info.owner_name,
        "thing2": thanks_info.goods_name,
        "amount3": str(thanks_info.price),
        "date5": datetime2str(thanks_info.updated_time)
    }
    send_subscribe(member.openid, "thanks", data)


def send_subscribe(openid, template, data):
    """
    向微信用户发送订阅消息
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
