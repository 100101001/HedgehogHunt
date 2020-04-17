# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/4/16 上午6:38
@file: SyncTasks.py
@desc: 
"""
from application import celery
from common.libs.recommend.v2 import SyncService
from common.models.ciwei.Goods import Good


@celery.task(name='sync.recommend_new', property=10)
def syncNewGoodsToRedis(goods_info=None):
    """
    新帖子发布
    :param goods_info:
    :return:
    """
    goods = Good()
    goods.__dict__ = goods_info
    SyncService.syncNewGoodsToRedis(goods_info=goods)


@celery.task(name='sync.recommend_recover_batch', property=10)
def synRecoverGoodsToRedis(goods_ids=None):
    """
    物品从  n -> 1
    :param goods_ids:
    :return:
    """
    goods_infos = Good.query.filter(Good.id.in_(goods_ids)).all()
    for goods_info in goods_infos:
        SyncService.syncNewGoodsToRedis(goods_info=goods_info)


@celery.task(name='sync.recommend_del_batch', property=10)
def syncDelGoodsToRedis(goods_ids=None, business_type=0):
    """
    物品从 1 -> n
    :param business_type:
    :param goods_ids:
    :return:
    """
    for goods_id in goods_ids:
        SyncService.syncDelGoodsToRedis(goods_id=goods_id, business_type=business_type)


if __name__ == "__main__":
    pass
