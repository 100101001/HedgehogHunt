# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/5/11 下午11:41
@file: TaskService.py
@desc: 
"""
from common.tasks.log import LogTasks
from common.tasks.recommend.v2 import RecommendTasks
from common.tasks.sms import SmsTasks
from common.tasks.subscribe import SubscribeTasks
from common.tasks.sync import SyncTasks


class TaskHandlers:
    __handlers = {
        'sync': SyncTasks,
        'log': LogTasks,
        'recommend': RecommendTasks,
        'subscribe': SubscribeTasks,
        'sms': SmsTasks
    }


    @classmethod
    def dispatch(cls, op, **kwargs):
        handler = cls.__handlers.get(op)
        return handler
