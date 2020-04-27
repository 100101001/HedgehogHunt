# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/4/16 上午6:38
@file: SyncTasks.py
@desc: 
"""
from application import celery
from common.libs.Helper import isInstance
from common.models.ciwei.Goods import Good
from common.sync.core.base import RedisService


@celery.task(name='sync.recommend_add', property=10)
def addGoodsToRedis(goods_ids=None, goods_info=None):
    """
    新的统一向redis添加候选物品的方法，通过id向数据库查取数据后插入redis
    :param goods_info:
    :param goods_ids:
    :return:
    """
    if goods_ids:
        if isInstance(goods_ids, list, set):
            goods = Good.query.filter(Good.id.in_(goods_ids)).all()
            RedisService.syncNewGoodsToRedis(*goods)
        else:
            goods = Good.query.filter_by(id=goods_ids).first()
            RedisService.syncNewGoodsToRedis(goods)
    if goods_info:
        goods = Good()
        goods.__dict__ = goods_info
        RedisService.syncNewGoodsToRedis(goods)


@celery.task(name='sync.recommend_del', property=10)
def syncDelGoodsToRedis(goods_ids=None, business_type=0):
    """
    物品从 1 -> n
    :param business_type:
    :param goods_ids:
    :return:
    """
    if business_type == 2:
        return
    if isInstance(goods_ids, list, set):
        RedisService.syncDelGoodsToRedis(*goods_ids, business_type=business_type)
    else:
        RedisService.syncDelGoodsToRedis(goods_ids, business_type=business_type)


@celery.task(name='sync.incr_read_count_to_db', property=5)
def syncIncrReadCountToDb():
    """
    定时任务
    :return:
    """
    from common.libs import GoodsService
    GoodsService.syncUpdatedReadCountInRedisToDb()
