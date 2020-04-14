# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/4/11 下午4:54
@file: __init__.py.py
@desc: 初始化Celery配置,以下包含了集成Flask的必需配置项
"""

import flask
from celery import Celery


class FlaskCelery(Celery):

    def __init__(self, *args, **kwargs):

        super(FlaskCelery, self).__init__(*args, **kwargs)
        self.patch_task()

        if 'app' in kwargs:
            self.init_app(kwargs['app'])

    def patch_task(self):
        """
        任务运行上下文为Flask app
        :return:
        """
        TaskBase = self.Task
        _celery = self

        class ContextTask(TaskBase):
            abstract = True

            def __call__(self, *args, **kwargs):
                if flask.has_app_context():
                    return TaskBase.__call__(self, *args, **kwargs)
                else:
                    with _celery.app.app_context():
                        return TaskBase.__call__(self, *args, **kwargs)

        self.Task = ContextTask

    def init_app(self, app):
        """
        celery配置与flask配置写在同一个配置里,从flask app的配置对象中加载
        :param app:
        :return:
        """
        self.app = app
        self.config_from_object(app.config)

