# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/4/26 下午3:00
@file: listeners.py
@desc: 
"""
from flask_sqlalchemy import event

from application import db
from common.libs.Helper import queryToDict
from common.models.ciwei.Goods import Good
from common.sync.core.GoodsSyncUtil import GoodsSyncUtil


@event.listens_for(db.session, 'after_bulk_update')
def syncUpdateToEs(bulk_update, **kwargs):
    """
    一次数据库事务中，批量更新goods后，
    获取到更新过的物品ID，将构造的同步参数设置到session此次DB事务的session中去
    :param bulk_update:
    :param kwargs:
    :return:
    """
    table_name = str(getattr(getattr(bulk_update, 'primary_table', None), 'description', None))
    if table_name == 'goods':
        # 更新的是物品
        updated_rows = getattr(bulk_update, 'matched_rows', None)
        if updated_rows:
            def __setRedisArgs(g_ids=None, args=None):
                if args:
                    func_typo = args.pop('typo', None)
                    func_args = args.get(func_typo)
                    if isinstance(func_args, dict):
                        func_args.setdefault('goods_ids', g_ids)

            def __setSyncArgs(g_ids=None):
                sync_args = getattr(bulk_update.session, 'sync_args', None)
                if not sync_args:
                    # 此次事务中仅有的一次Good的update
                    bulk_update.session.sync_args = [dict(updated_kwargs=dict(goods_ids=g_ids, updated=bulk_update.values.copy()),
                             redis_kwargs=redis_arg)]
                else:
                    # 此次事务存在多个Good的update
                    bulk_update.session.sync_args.append(
                        dict(updated_kwargs=dict(goods_ids=g_ids, updated=bulk_update.values.copy()),
                             redis_kwargs=redis_arg))

            goods_ids = [item[0] for item in updated_rows]
            redis_arg = getattr(bulk_update.session, 'redis_arg', None)
            # goods_ids设置到redis参数中去
            __setRedisArgs(goods_ids, redis_arg)
            # 添加本次批量更新的sync参数到本次scoped_session中去
            __setSyncArgs(goods_ids)


@event.listens_for(db.session, 'after_commit')
def batchSyncUpdatedGoodsAfterCommit(session):
    """
    提交后，检查有没有bulk_updated的同步需求，并进行同步
    :param session:
    :return:
    """
    sync_args = getattr(session, 'sync_args', None)
    if sync_args:
        # 执行本次会话中所有批量更新需要进行的sync操作
        GoodsSyncUtil.doSyncBatch(*sync_args)


@event.listens_for(Good.status, 'set')
def listenGoodsStatusChange(target, new_val, old_val, e):
    def __setRedisArgs(val):
        # 将redis参数设置到模型的会话参数中去
        state = getattr(target, '_sa_instance_state', None)  # 一个下划线，标示可以更改，只是受到保护
        session = getattr(state, 'session', None)
        if session:
            session._redis_arg = val

    if old_val != new_val and target.business_type != 2 and target.report_status == 0:
        # 将redis参数设置到模型的会话参数中去
        if old_val == 1:
            __setRedisArgs(-1)
        elif new_val == 1:
            __setRedisArgs(1)


@event.listens_for(Good.report_status, 'set')
def listenGoodsStatusChange(target, new_val, old_val, e):
    def __setRedisArgs(val):
        # 将redis参数设置到模型的会话参数中去
        state = getattr(target, '_sa_instance_state', None)  # 一个下划线，标示可以更改，只是受到保护
        session = getattr(state, 'session', None)
        if session:
            session._redis_arg = val

    if old_val != new_val and target.business_type != 2 and target.status == 1:
        if old_val == 0:
            __setRedisArgs(-1)
        elif new_val == 0:
            __setRedisArgs(1)


@event.listens_for(Good, 'after_update')
def syncUpdatedGoodsAfterCommit(mapper, connection, target):
    """
    非批量更新接口，同步物品
    :param mapper:
    :param connection:
    :param target:
    :return:
    """

    def __getRedisArgs():
        state = getattr(target, '_sa_instance_state', None)  # 一个下划线，标示可以更改，只是受到保护
        session = getattr(state, 'session', None)
        arg = getattr(session, '_redis_arg', None)
        if arg == -1:
            return {'rem': dict(goods_ids=target.id, business_type=target.business_type)}
        elif arg == 1:
            return {'add': dict(goods_info=queryToDict(target))}

    sync_arg = dict(updated_kwargs=dict(goods_info=target), redis_kwargs=__getRedisArgs())
    GoodsSyncUtil.doSyncBatch(sync_arg)


@event.listens_for(Good, 'after_insert')
def syncNewGoodsAfterCommit(mapper, connection, target):
    """
    插入新数据后，同步到ES
    :param mapper:
    :param connection:
    :param target:
    :return:
    """

    def __getRedisArgs():
        if target.business_type != 2 and target.status == 1:
            return {'add': dict(goods_ids=target.id)}

    sync_arg = dict(new_kwargs=dict(goods_info=target), redis_kwargs=__getRedisArgs())
    GoodsSyncUtil.doSyncBatch(sync_arg)
