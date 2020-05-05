# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/4/26 上午12:01
@file: RedisService.py
@desc: 
"""
import json

from application import app
from common.cahce.core import redis_conn_db_3, redis_conn_db_4
from common.sync.core.base import synonyms


def syncNewGoodsToRedis(*args):
    for arg in args:
        __syncNewGoodsToRedis(goods_info=arg)


def __syncNewGoodsToRedis(goods_info=None):
    """
    有新的候选数据
    :param goods_info:
    :return:
    """
    if goods_info.business_type == 2 or goods_info.status != 1:
        app.logger.warn("{0}.{1}".format(goods_info.business_type, goods_info.status))
        return
    goods_id = goods_info.id
    location = goods_info.os_location.split("###")[-3:]
    goods_name = goods_info.name
    business_type = goods_info.business_type
    created_time = goods_info.created_time
    cls_list = synonyms.getWordClassesSync(goods_name)
    # 寻物放库3, 拾物放库4
    redis_conn = redis_conn_db_3 if business_type == 0 else redis_conn_db_4
    ele = json.dumps({
        # 关系数据库和地址筛选
        'id': goods_id,
        'lng': eval(location[2]),
        'lat': eval(location[1]),
        'member_id': goods_info.member_id,
        # 订阅消息
        'openid': goods_info.openid,
        'name': goods_name,
        'created_time': created_time if isinstance(created_time, str) else created_time.strftime("%Y-%m-%d %H:%M:%S"),
        'loc': location[0]
    })
    for k in cls_list:
        app.logger.warn('{0}.同步add.{1}'.format(k, goods_id))
        # 把物品添加到该类别下的物品集合
        redis_conn.hset(k, goods_id, ele)
    if cls_list:
        # 把物品id对应的类别存一下，方便删除
        redis_conn.set(goods_id, ','.join(cls_list))


def syncDelGoodsToRedis(*args, business_type=0):
    for arg in args:
        __syncDelGoodsToRedis(goods_id=arg, business_type=business_type)


def __syncDelGoodsToRedis(goods_id=0, business_type=0):
    """
    状态变更就删除
    :param business_type:
    :param goods_id:
    :return:
    """
    # 寻物放库3, 拾物放库4
    redis_conn = redis_conn_db_3 if business_type == 0 else redis_conn_db_4
    word_cls = redis_conn.get(goods_id)
    if word_cls:
        # 物品在redis中
        word_cls = word_cls.split(',')
        for cls in word_cls:
            app.logger.warn('{0}.同步rem.{1}'.format(cls, goods_id))
            # 把物品从到对应类别下的物品集合从移除
            redis_conn.hdel(cls, goods_id)
        redis_conn.delete(goods_id)
