# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/5/2 上午1:27
@file: __init__.py.py
@desc: 
"""
from sqlalchemy import event

from common.libs import ThanksService
from common.models.ciwei.Mark import Mark
from common.models.ciwei.Thanks import Thank


@event.listens_for(Thank, 'after_insert')
def updateGoodsMarkStatusAfterThanks(mapper, connection, target):
    business_type = target.business_desc
    if business_type == "拾到":
        # 帖子和认领记录一起更新
        ThanksService.updateThankedFoundStatus(found_id=target.goods_id, send_member_id=target.member_id)
    else:
        # 归还和寻物帖子一起更新
        ThanksService.updateThankedReturnStatus(return_id=target.goods_id)
    Mark.query.filter(Mark.member_id == target.member_id,
                      Mark.goods_id == target.goods_id,
                      Mark.status == 1).update({'status': 2}, synchronize_session=False)
