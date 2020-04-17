# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/4/17 下午5:08
@file: GoodsService.py
@desc: 
"""
import datetime

from sqlalchemy import func

from application import db
from common.cahce import redis_conn_db_1, cas, CacheKeyGetter
from common.libs.Helper import queryToDict
from common.libs.MemberService import MemberService
from common.libs.recommend.v2 import SyncService
from common.models.ciwei.Mark import Mark
from common.tasks.recommend.v2 import RecommendTasks
from common.tasks.sms import SmsTasks
from common.tasks.sync import SyncTasks


def returnToLostSuccess(return_goods=None, lost_goods=None):
    """
    
    :param return_goods:
    :param lost_goods: 
    :return: 
    """
    lost_id = lost_goods.id
    return_goods.status = 1
    return_goods.return_goods_id = lost_id
    return_goods.return_goods_openid = lost_goods.openid  # 用于被归还的用户快速查找归还通知
    # 寻物贴链接归还贴，状态置为预先寻回
    return_id = return_goods.id
    lost_goods.return_goods_id = return_id
    lost_goods.return_goods_openid = return_goods.openid  # 用于判断是归还用户查看了帖子详情
    now = datetime.datetime.now()
    lost_goods.confirm_time = now  # 指的是归还时间
    lost_goods.status = 2
    db.session.add(lost_goods)
    db.session.add(return_goods)
    MemberService.updateCredits(member_id=return_goods.member_id)
    db.session.commit()
    # 新归还帖
    SyncService.syncGoodsToES(goods_info=return_goods, edit=False)
    # 更新寻贴
    SyncService.syncUpdatedGoodsToES(goods_id=lost_id, updated={'return_goods_id': return_id,
                                                                'return_goods_openid': return_goods.openid,
                                                                'confirm_time': now,
                                                                'status': 2})


def scanReturnSuccess(scan_goods=None, notify_id=''):
    # 链接归还的对象，直接就是对方的物品(如若不是可举报)
    scan_goods.qr_code_openid = notify_id
    scan_goods.status = 2
    db.session.add(scan_goods)
    MemberService.updateCredits(member_id=scan_goods.member_id)
    db.session.commit()
    # ES同步
    SyncService.syncGoodsToES(goods_info=scan_goods, edit=False)
    # 通知
    params = {
        'location': scan_goods.location,
        'goods_name': scan_goods.name,
        'rcv_openid': notify_id,
        'trig_openid': scan_goods.openid,
        'trig_member_id': scan_goods.member_id
    }
    SmsTasks.notifyQrcodeOwner.delay(params=params)


def releaseGoodsSuccess(goods_info=None, edit_info=None):
    is_edit = edit_info is not None
    if is_edit:
        goods_id = goods_info.id
        edit_key = CacheKeyGetter.goodsEditKey(goods_id)
        status = redis_conn_db_1.get(edit_key)
        goods_info.status = int(status)
        cas.exec(goods_id, 7, status)
        redis_conn_db_1.delete(edit_key)
    else:
        goods_info.status = 1

    db.session.add(goods_info)
    MemberService.updateCredits(member_id=goods_info.member_id)
    db.session.commit()
    # ES同步
    SyncService.syncGoodsToES(goods_info=goods_info, edit=is_edit)
    # RS同步
    serializable_goods_info = queryToDict(goods_info)
    SyncTasks.syncNewGoodsToRedis.delay(goods_info=serializable_goods_info)
    # 匹配
    RecommendTasks.autoRecommendGoods(edit_info=edit_info, goods_info=serializable_goods_info)


def getNoMarksAfterDelPremark(cancel_mark_tuples=None):
    """
    取消认领后,可能没有人人领
    :param cancel_mark_tuples: [(mark_key, found_id)]
    :return:
    """
    no_marks = []
    for m_key, found_id in cancel_mark_tuples:
        marks = redis_conn_db_1.smembers(m_key)
        if marks:
            no_mark = len(marks) == 1 and marks[0] == '-1'
        else:
            cnt = db.session.query(func.count(Mark.id)).filter(Mark.goods_id == found_id, Mark.status != 7).scalar()
            no_mark = cnt == 0
        if no_mark and cas.exec(found_id, 2, 1):
            # 这里不会出问题，因为认领那里，进入后设置成了 7，缓存和数据库都提交后，才会被设置成2。
            no_marks.append(found_id)
