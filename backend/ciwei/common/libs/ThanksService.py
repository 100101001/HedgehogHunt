# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/4/19 下午4:45
@file: ThanksService.py
@desc: 
"""
import datetime
from decimal import Decimal

from sqlalchemy import or_

from application import db
from common.cahce.GoodsCasUtil import GoodsCasUtil
from common.libs.MemberService import MemberService
from common.models.ciwei.Goods import Good
from common.models.ciwei.Mark import Mark
from common.models.ciwei.Thanks import Thank


def sendThanksToGoods(send_member=None, thanked_goods=None, thank_info=None):
    """

    :param send_member: 答谢者信息
    :param thanked_goods: 答谢物品信息
    :param thank_info: 答谢信息
    :return:
    """
    thanks_model = Thank()
    # 发出答谢的用户信息
    thanks_model.member_id = send_member.id  # 发出答谢的人
    thanks_model.nickname = send_member.nickname  # 发出答谢的人
    thanks_model.avatar = send_member.avatar  # 发出答谢的人
    # 被答谢物品信息
    thanks_model.target_member_id = int(thanked_goods.get('auther_id', 0))
    thanks_model.goods_id = int(thanked_goods.get('goods_id', 0))  # 答谢的物品id
    thanks_model.goods_name = thanked_goods.get('goods_name', '拾物')  # 答谢的物品名
    thanks_model.owner_name = thanked_goods.get('owner_name', '无')  # 答谢的物品的失主名
    business_type = int(thanked_goods.get('business_type', 1))  # 答谢的物品类型
    thanks_model.business_desc = "拾到" if business_type == 1 else "归还"
    # 答谢信息
    thanks_model.thank_price = Decimal(thank_info.get('target_price', '0')).quantize(Decimal('0.00'))  # 答谢金额
    thanks_model.order_sn = thank_info.get('order_sn', '')  # 答谢支付订单
    thanks_model.summary = thank_info.get('thanks_text', '谢谢你的举手之劳！')  # 答谢文字，前端已判空

    # 金额转入目标用户余额
    MemberService.updateBalance(member_id=thanks_model.target_member_id, unit=thanks_model.thank_price, note='答谢赏金')
    db.session.add(thanks_model)
    return thanks_model


# TODO now func
def updateThankedFoundStatus(found_id=0, send_member_id=0):
    """
    更新认领记录和拾物状态
    :param found_id:
    :param send_member_id:
    :return:
    """
    if not found_id or not send_member_id:
        return
    if GoodsCasUtil.exec_wrap(found_id, ['nil', 3], 4):
        # 如果没有被删除就更新为已答谢，否则不更新
        Good.query.filter_by(id=found_id, status=3).update({'status': 4, 'thank_time': datetime.datetime.now()})
    Mark.query.filter(Mark.member_id == send_member_id,
                      Mark.goods_id == found_id,
                      Mark.status == 1).update({'status': 2}, synchronize_session=False)


def updateThankedReturnStatus(return_id=0):
    """
    更新归还物和对应的寻物状态
    :param return_id:
    :return:
    """
    if not return_id:
        return
    lost_id = Good.query.filter_by(id=return_id).with_entities(Good.return_goods_id).first()
    # 对方可能正好删除了归还帖子，但寻物贴只有答谢者自己才能删除的帖子，不可能并发操作
    updated = {'status': 4, 'thank_time': datetime.datetime.now()}
    GoodsCasUtil.exec_wrap(lost_id, ['nil', 3], 4)  # 寻物贴只有自己能操作状态，所以不会冲突
    if GoodsCasUtil.exec_wrap(return_id, ['nil', 3], 4):  # 归还帖对方可以删除让状态变为 7
        # 不存在并发操作
        Good.query.filter(or_(Good.id == return_id, Good.id == lost_id[0]),
                          Good.status == 3).update(updated)
    else:
        # 对方正好删除了归还帖子
        Good.query.filter(Good.id == lost_id[0],
                          Good.status == 3).update(updated)




