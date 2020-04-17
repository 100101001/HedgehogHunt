# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/4/13 下午6:03
@file: SubscribeTasks.py
@desc: 
"""
import requests

from application import celery, app, APP_CONSTANTS, db
from common.libs.mall.WechatService import WeChatService
from common.models.ciwei.Goods import Good
from common.models.ciwei.Member import Member
from common.tasks.log import LogTasks

SUB_DATE_FORMAT = APP_CONSTANTS['sub_time_format']


@celery.task(name='subscribe.return_finish_batch')
def send_found_finish_msg_in_batch(gotback_founds=None):
    if gotback_founds is None:
        return False

    found_infos = Good.query.filter(Good.id.in_(gotback_founds)).with_entities(Good.openid, Good.name,
                                                                               Good.owner_id, Good.finish_time).all()
    Member.query.filter(Member.id.in_([item.openid for item in found_infos])).update({'credits': Member.credits + 5},
                                                                                     synchronize_session=False)
    losers = Member.query.filter(Member.id.in_([item.owner_id for item in found_infos])).with_entities(Member.id,
                                                                                                       Member.nickname).all()
    loser_map = {item.id: item.nickname for item in losers}

    for info in found_infos:
        # 失物认领成功通知
        """
        物品名 Wilson篮球
        认领者 爱丢东西的TJer
        认领时间 2019年10月21日 14：05
        """
        found_finish = {
            'thing1': {'value': info.name},
            'thing2': {'value': loser_map[info.owner_id]},
            'date3': {'value': info.finish_time.strftime(SUB_DATE_FORMAT)}
        }
        send_subscribe(openid=info.openid, template='finish', data=found_finish)
    db.session.commit()
    return True


@celery.task(name='subscribe.return_finish_batch')
def send_return_finish_msg_in_batch(gotback_returns=None):

    if gotback_returns is None:
        return False
    returns = Good.query.filter(Good.id.in_(gotback_returns)).with_entities(Good.openid, Good.owner_id, Good.name,  # 发送对象，物品名，失主，取回时间
                                                                            Good.finish_time).all()
    Member.query.filter(Member.id.in_([item.openid for item in returns])).update({'credits': Member.credits + 5},
                                                                                 synchronize_session=False)
    losers = Member.query.filter(Member.id.in_([item.owner_id for item in returns])).with_entities(Member.id,
                                                                                                   Member.nickname).all()
    losers_map = {loser.id: loser.nickname for loser in losers}
    for gotback_info in returns:
        # 归还成功通知
        """
        物品名 Wilson篮球
        失主名 爱丢东西的TJer
        取回时间 2019年10月21日 14：05
        """
        return_finish = {
            "thing1": {"value": gotback_info.name},
            "thing2": {"value": losers_map[gotback_info.owner_id].nickname},
            "date3": {"value": gotback_info.finish_time.strftime(SUB_DATE_FORMAT)},
        }
        send_subscribe(openid=gotback_info.openid, template="return", data=return_finish)
    db.session.commit()
    return True


@celery.task(name='subscribe.recommend_batch')
def send_recommend_subscribe_in_batch(lost_goods_list=None, found_goods=None):
    """
    给丢了东西的用户发送消息
    :return: 异步任务成功执行
    """
    if lost_goods_list is None or found_goods is None:
        return False
    found_goods_name = found_goods.get('name')
    found_goods_time = found_goods.get('create_time')
    found_goods_put_loc = found_goods.get('location').split('###')[1]
    recommend_data = {
        "thing1": {"value": found_goods_name},
        "time2": {"value": found_goods_time},
        "thing3": {"value": found_goods_put_loc},
    }

    for lost_goods in lost_goods_list:
        send_subscribe(openid=lost_goods[3], template="recommend", data=recommend_data)
    return True


@celery.task(name='subscribe.do_send')
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
    wx_resp = requests.post(url, json=data).json()
    app.logger.info("完成{}消息 错误码:{} 错误信息：{}".format(template, wx_resp['errcode'], wx_resp['errmsg']))
    LogTasks.addWechatApiCallLog.delay(url=url.split('?')[0], token=token, req_data=data, resp_data=wx_resp)
