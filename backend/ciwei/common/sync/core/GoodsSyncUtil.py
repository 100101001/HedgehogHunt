# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/4/26 上午12:08
@file: GoodsSyncUtil.py
@desc: 
"""
from common.sync.core.base import EsService
from common.tasks.sync import SyncTasks


class GoodsSyncUtil:

    @staticmethod
    def doSyncBatch(*args):
        for sync_arg in args:
            GoodsSyncUtil.__doSync(**sync_arg)

    @staticmethod
    def __doSync(updated_kwargs=None, new_kwargs=None, del_kwargs=None, redis_kwargs=None):
        """
        单次变更接口
        :param redis_kwargs:
        :param del_kwargs:
        :param new_kwargs:
        :param updated_kwargs:
        :return:
        """
        if updated_kwargs is not None:
            GoodsSyncUtil.__syncUpdateToEs(updated_kwargs=updated_kwargs)
        if new_kwargs is not None:
            GoodsSyncUtil.__syncNewToEs(new_kwargs=new_kwargs)
        if del_kwargs is not None:
            GoodsSyncUtil.__syncDelToEs(del_kwargs=del_kwargs)
        if redis_kwargs is not None:
            GoodsSyncUtil.__addOrDelGoodsToRedis(redis_kwargs=redis_kwargs)

    @staticmethod
    def __syncUpdateToEs(updated_kwargs=None):
        """
        数据更新到ES
        :param updated_kwargs:
        :return:
        """
        if not updated_kwargs:
            return
        if isinstance(updated_kwargs, list):
            # 多个物品更新的内容不同，更新内容同样的可能是批次的
            for item in updated_kwargs:
                EsService.syncUpdatedGoodsToES(**item)
        elif isinstance(updated_kwargs, dict):
            # 更新的内容一样
            EsService.syncUpdatedGoodsToES(**updated_kwargs)

    @staticmethod
    def __syncNewToEs(new_kwargs=None):
        """
        新的物品同步到ES
        :param new_kwargs:
        :return:
        """
        if not new_kwargs:
            return
        if isinstance(new_kwargs, list):
            # 多个更新
            for item in new_kwargs:
                EsService.syncGoodsToES(**item)
        elif isinstance(new_kwargs, dict):
            # 单个
            EsService.syncGoodsToES(**new_kwargs)

    @staticmethod
    def __syncDelToEs(del_kwargs=None):
        """
        将物品的删除同步到ES
        :param del_kwargs:
        :return:
        """
        if not del_kwargs:
            return
        if isinstance(del_kwargs, list):
            # 多个更新
            for item in del_kwargs:
                EsService.syncSoftDelGoodsToES(**item)
        elif isinstance(del_kwargs, dict):
            # 单个
            EsService.syncSoftDelGoodsToES(**del_kwargs)

    @staticmethod
    def __addOrDelGoodsToRedis(redis_kwargs=None):
        if not redis_kwargs:
            return
        add_args = redis_kwargs.get('add')
        del_args = redis_kwargs.get('rem')
        if add_args:
            SyncTasks.addGoodsToRedis.delay(**add_args)
        if del_args:
            SyncTasks.syncDelGoodsToRedis.delay(**del_args)
