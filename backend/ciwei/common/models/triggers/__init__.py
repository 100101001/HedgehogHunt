# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/5/2 上午1:27
@file: __init__.py.py
@desc: 
"""
from sqlalchemy import event

from common.libs.ThanksService import ThankHandler
from common.models.ciwei.Thanks import Thank


@event.listens_for(Thank, 'after_insert')
def updateGoodsMarkStatusAfterThanks(mapper, connection, target):
    ThankHandler.deal('insert_trig', biz_typo=target.business_desc, goods_id=target.goods_id, sender_id=target.member_id)
