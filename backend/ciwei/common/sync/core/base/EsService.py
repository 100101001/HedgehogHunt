# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/4/25 下午11:59
@file: EsService.py
@desc: 
"""

from elasticsearch import helpers, NotFoundError

from application import app, es
from common.libs.Helper import isInstance

ES_CONSTANTS = app.config['ES']


def syncGoodsToES(goods_info=None, edit=False):
    """
    新增or编辑物品
    :param goods_info:
    :param edit:
    :return:
    """
    if not goods_info:
        return "NO INFO TO INSERT"

    goods_id = goods_info.id
    location = goods_info.os_location.split("###")[-3:]  # 寻物启事没有地址默认设置为 不知道###不知道###0###0
    business_type = goods_info.business_type

    # 通用数据
    body = {
        'id': goods_id,
        'name': goods_info.name,
        'member_id': goods_info.member_id,
        'business_type': business_type,
        'lng': eval(location[2]),
        'lat': eval(location[1]),
        # 订阅消息
        'openid': goods_info.openid,
        'created_time': goods_info.created_time,
        'loc': location[0],
        'location': goods_info.location,
        'os_location': goods_info.os_location,
        # 其他同步数据
        'owner_name': goods_info.owner_name,
        'summary': goods_info.summary,
        'status': goods_info.status,
        'updated_time': goods_info.updated_time,
        'main_image': goods_info.main_image,
        'pics': goods_info.pics,
        'nickname': goods_info.nickname,
        'avatar': goods_info.avatar,
        "author_mobile": goods_info.author_mobile,
        'mobile': goods_info.mobile,
        'top_expire_time': goods_info.top_expire_time,
        'return_goods_id': goods_info.return_goods_id,
        'return_goods_openid': goods_info.return_goods_openid,
        'qr_code_openid': goods_info.qr_code_openid,
        'view_count': goods_info.view_count,
        'user_id': goods_info.user_id,
        'report_status': goods_info.report_status,
        'confirm_time': goods_info.confirm_time,
        'finish_time': goods_info.finish_time,
        'thank_time': goods_info.thank_time,
        'appeal_time': goods_info.appeal_time
    }
    if edit:
        try:
            res = es.update(index=ES_CONSTANTS['INDEX'], id=goods_id, body={'doc': body})
            app.logger.info("搜索数据更新: " + str(res))
        except NotFoundError as e:
            res = str(e)
            app.logger.error(res)
    else:
        res = es.create(index=ES_CONSTANTS['INDEX'], id=goods_id, body=body)
        app.logger.info("搜索数据插入: " + str(res))
    return res



def syncUpdatedGoodsToES(goods_ids=None, updated=None, goods_info=None):
    """
    更新入口，如果多条更新就走批量更新，否则直接调取update接口
    :param goods_info:
    :param goods_ids:
    :param updated:
    :return:
    """

    if not updated and not goods_ids and not goods_info:
        return
    if goods_info:
        syncGoodsToES(goods_info=goods_info, edit=True)
    if goods_ids and updated:
        if isInstance(goods_ids, list, set):
            __syncUpdatedGoodsToESBulk(goods_ids=goods_ids, updated=updated)
        else:
            es.update(index=ES_CONSTANTS['INDEX'], id=goods_ids, body={'doc': updated})


def __syncUpdatedGoodsToESBulk(goods_ids=None, updated=None):
    """
    批量更新
    :param goods_ids:
    :param updated:
    :return:
    """
    if not goods_ids or not updated:
        return
    actions = []
    i = 0
    for goods_id in goods_ids:
        action = {
            '_op_type': 'update',
            '_index': ES_CONSTANTS['INDEX'],
            '_id': goods_id if isInstance(goods_id, int) else goods_id[0],
            'doc': updated
        }
        i += 1
        actions.append(action)
    if i > 0:
        helpers.bulk(es, actions, raise_on_exception=False, raise_on_error=False)
