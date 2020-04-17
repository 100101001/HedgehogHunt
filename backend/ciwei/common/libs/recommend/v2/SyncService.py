# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/4/15 下午11:51
@file: SyncService.py
@desc: 用于同步推荐使用的数据
"""
import json

from elasticsearch import helpers

from application import es, app
from common.cahce import redis_conn_db_3, redis_conn_db_4
from common.libs.recommend.v2.SynonymsService import SynonymsService

synonyms = SynonymsService()
ES_CONSTANTS = app.config['ES']


def syncNewGoodsToRedis(goods_info=None):
    """
    有新的候选数据
    :param goods_info:
    :return:
    """
    goods_id = goods_info.id
    location = goods_info.os_location.split("###")[-3:]
    goods_name = goods_info.name
    business_type = goods_info.business_type

    cls_list = synonyms.getWordClassesSync(goods_name)
    # 寻物放库3, 拾物放库4
    redis_conn = redis_conn_db_3 if business_type == 0 else redis_conn_db_4
    ele = json.dumps({
        'id': goods_id,
        'lng': eval(location[2]),
        'lat': eval(location[1]),
        'member_id': goods_info.member_id,
        # 订阅消息
        'name': goods_name,
        'created_time': goods_info.created_time,
        'loc': location[0]
    })
    for k in cls_list:
        app.logger.info("redis sync")
        redis_conn.hset(k, goods_id, ele)
    if cls_list:
        # 把 id 对应的类别表存一下，方便删除
        redis_conn.set(goods_id, ','.join(cls_list))


def syncDelGoodsToRedis(goods_id=0, business_type=0):
    """
    状态变更就删除
    :param business_type:
    :param goods_id:
    :return:
    """

    # es.delete(index=ES_CONSTANTS['INDEX'], doc_type=ES_CONSTANTS['DOC_TYPE'], id=goods_id)
    # 寻物放库3, 拾物放库4
    redis_conn = redis_conn_db_3 if business_type == 0 else redis_conn_db_4
    word_cls = redis_conn.get(goods_id).split(',')
    for cls in word_cls:
        app.logger.info("redis sync")
        redis_conn.hdel(cls, goods_id)
    redis_conn.delete(goods_id)


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
        'created_time': goods_info.created_time,
        'loc': location[0],
        # 其他同步数据
        'owner_name': goods_info.owner_name,
        'summary': goods_info.summary,
        'status': goods_info.status,
        'updated_time': goods_info.updated_time,
        'main_image': goods_info.main_image,
        'pics': goods_info.pics,
        'nickname': goods_info.nickname,
        'avatar': goods_info.avatar,
        'mobile': goods_info.mobile,
        'top_expire_time': goods_info.top_expire_time,
        'return_goods_id': goods_info.return_goods_id,
        'return_goods_openid': goods_info.return_goods_openid,
        'qr_code_openid': goods_info.qr_code_openid,
        'view_count': goods_info.view_count,
        'report_status': goods_info.report_status,
        'confirm_time': goods_info.confirm_time,
        'finish_time': goods_info.finish_time,
        'thank_time': goods_info.thank_time,
        'appeal_time': goods_info.appeal_time
    }
    if edit:
        res = es.update(index=ES_CONSTANTS['INDEX'], id=goods_id, body={'doc': body})
    else:
        res = es.create(index=ES_CONSTANTS['INDEX'], id=goods_id, body=body)
    app.logger.info("搜索数据插入: " + str(res))
    return res


def syncDeleteGoodsToESBulk(goods_ids=None):
    """
    批量删除不再使用的数据
    :param goods_ids:
    :return:
    """
    must = {'must': [{'ids': {'values': goods_ids}}]}
    return es.delete_by_query(index=ES_CONSTANTS['INDEX'], body={'query': {'bool': must}})


def syncUpdatedGoodsToESBulk(goods_ids=None, updated=None):
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
            '_index': ES_CONSTANTS['INDEX'],
            '_id': goods_id,
            '_source': updated
        }
        i += 1
        actions.append(action)
    if i > 0:
        helpers.bulk(es, actions)


def syncUpdatedGoodsToES(goods_id=0, updated=None):
    """
    更新单条数据
    :param goods_id:
    :param updated:
    :return:
    """
    if not updated:
        return
    res = es.update(index=ES_CONSTANTS['INDEX'], id=goods_id, body={'doc': updated})
    return res
