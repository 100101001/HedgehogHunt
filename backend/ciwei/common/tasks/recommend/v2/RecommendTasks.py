# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/4/16 上午3:46
@file: RecommendTasks.py
@desc: 
"""

from application import celery
from common.libs.recommend.v2.RecommendService import RecommendHandler
from common.models.proxy.GoodProxy import GoodProxy


@celery.task(name='recommend.auto_recommend_goods', property=1)
def autoRecommendGoods(edit_info=None, goods_info=None):
    goods = GoodProxy()
    goods.__dict__ = goods_info
    RecommendHandler.filter(edit_info=edit_info, goods_info=goods)
