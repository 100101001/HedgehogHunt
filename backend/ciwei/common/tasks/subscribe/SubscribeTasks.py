# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/4/13 下午6:03
@file: SubscribeTasks.py
@desc: https://mp.weixin.qq.com/wxamp/newtmpl/mytmpl?start=0&limit=10&token=1218603435&lang=zh_CN
"""
import requests

from application import celery, app, APP_CONSTANTS, db
from common.libs.Helper import getCurrentDate
from common.libs.mall.WechatService import WeChatService
from common.models.ciwei.Goods import Good
from common.models.ciwei.Member import Member
from common.tasks.log import LogTasks

SUB_DATE_FORMAT = APP_CONSTANTS['sub_time_format']


@celery.task(name='subscribe.return_finish_batch', property=1, ignore_result=True)
def send_found_finish_msg_in_batch(gotback_founds=None):
    """
    发送公开招领的东西已取回
    :param gotback_founds:
    :return:
    """
    if gotback_founds is None:
        return

    found_infos = Good.query.filter(Good.id.in_(gotback_founds)).with_entities(Good.openid, Good.name,
                                                                               Good.owner_id, Good.finish_time).all()
    # 物品发布者积分再加
    Member.query.filter(Member.id.in_([item.openid for item in found_infos])).update({'credits': Member.credits + 5},
                                                                                     synchronize_session=False)
    # 取出失主昵称
    losers = Member.query.filter(Member.id.in_([item.owner_id for item in found_infos])).with_entities(Member.id,
                                                                                                       Member.nickname).all()
    loser_map = {item.id: item.nickname for item in losers}

    for info in found_infos:
        # 失物认领成功通知
        """
        物品名 Wilson篮球 {{thing1.DATA}}
        认领者 爱丢东西的TJer {{thing2.DATA}}
        认领时间 2019年10月21日 14：05 {{date3.DATA}}
        """
        found_finish = {
            'thing1': {'value': info.name},
            'thing2': {'value': loser_map[info.owner_id]},
            'date3': {'value': info.finish_time.strftime(SUB_DATE_FORMAT)}
        }
        send_subscribe.delay(openid=info.openid, template='finished_found', data=found_finish)
    db.session.commit()


@celery.task(name='subscribe.return_finish_batch', property=1, ignore_result=True)
def send_return_finish_msg_in_batch(gotback_returns=None):
    """
    发送归还的东西已取回了
    :param gotback_returns:
    :return:
    """
    if gotback_returns is None:
        return
    returns = Good.query.filter(Good.id.in_(gotback_returns)).with_entities(Good.openid, Good.owner_id, Good.name,
                                                                            # 发送对象，物品名，失主，取回时间
                                                                            Good.finish_time).all()
    # 物品发布者积分再加
    Member.query.filter(Member.id.in_([item.openid for item in returns])).update({'credits': Member.credits + 5},
                                                                                 synchronize_session=False)
    # 取出失主昵称
    losers = Member.query.filter(Member.id.in_([item.owner_id for item in returns])).with_entities(Member.id,
                                                                                                   Member.nickname).all()
    losers_map = {loser.id: loser.nickname for loser in losers}
    for gotback_info in returns:
        # 寻物归还成功通知
        """
        物品名 Wilson篮球 {{thing1.DATA}}
        失主名 爱丢东西的TJer {{thing2.DATA}}
        取回时间 2019年10月21日 14：05 {{time3.DATA}}
        """
        return_finish = {
            "thing1": {"value": gotback_info.name},
            "thing2": {"value": losers_map[gotback_info.owner_id]},
            "date3": {"value": gotback_info.finish_time.strftime(SUB_DATE_FORMAT)},
        }
        send_subscribe.delay(openid=gotback_info.openid, template="finished_return", data=return_finish)
    db.session.commit()


@celery.task(name='subscribe.recommend_batch', property=2, ignore_result=True)
def send_recommend_subscribe_in_batch(lost_list=None, found_goods=None):
    """
    给丢了东西的用户发送匹配消息
    :return: 异步任务成功执行
    """
    if lost_list is None or found_goods is None:
        return

    recommend_data = {
        "thing1": {"value": found_goods.get('name')},
        "time2": {"value": found_goods.get('created_time', getCurrentDate())},
        "thing3": {"value": found_goods.get('location').split('###')[1]},
    }

    for lost_goods in lost_list:
        # 失物匹配成功通知
        """
        匹配物品 Wilson篮球  {{thing1.DATA}}
        捡拾时间 2020年3月24日 20:20 {{time2.DATA}}
        放置地点 129运动场 {{thing3.DATA}}
        """
        send_subscribe.delay(openid=lost_goods.get('openid'), template="recommend", data=recommend_data)


@celery.task(name='subscribe.send_thank_subscribe', property=1)
def send_thank_subscribe(thank_info=None):
    """
    向被答谢者发送答谢消息
    :return:
    """
    # 失主答谢通知
    """
    答谢者 爱丢东西的TJer
    答谢金额 0.5元
    答谢文字 谢谢你帮我找到了我的Wilson篮球!
    答谢时间 2019年10月25日 14：05
    """
    thank_data = {
        "thing1": {"value": thank_info.get('nickname')},
        "amount2": {"value": thank_info.get('thank_price', 0)},
        "thing3": {"value": thank_info.get('summary')},
        "date4": {"value": thank_info.get('created_time', getCurrentDate())}
    }
    openid = Good.query.filter_by(id=thank_info.get('goods_id')).with_entities(Good.openid).first()
    if openid:
        send_subscribe.delay(openid=openid[0], template='thanks', data=thank_data)


@celery.task(name='subscribe.send_return_subscribe', property=2)
def send_return_subscribe(return_info=None):
    """
    寻物有新的归还时，发送订阅消息
    :param return_info:
    :return:
    """

    return_data = {
        "thing1": {"value": return_info.get('goods_name')},
        "thing2": {"value": return_info.get('returner')},
        "date3": {"value": return_info.get('return_date')}
    }
    # 寻物归还通知
    """
    物品名 Nike衣帽 {{thing1.DATA}}
    归还者 拾金不昧的TJer {{thing2.DATA}}
    归还时间 2019年10月22日 14：05 {{date3.DATA}}
    """
    send_subscribe.delay(openid=return_info.get('rcv_openid'), template='return', data=return_data)


@celery.task(name='subscribe.do_send', property=3)
def send_subscribe(openid='', template='', data=None):
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
    app.logger.info("发送{0}消息, data: {1}".format(template, str(data)))
    wx_resp = requests.post(url, json=data).json()
    app.logger.info("完成{}消息 错误码:{} 错误信息：{}".format(template, wx_resp['errcode'], wx_resp['errmsg']))
    LogTasks.addWechatApiCallLog.delay(url=url.split('?')[0], token=token, req_data=data, resp_data=wx_resp)
