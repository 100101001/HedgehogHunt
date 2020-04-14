# # encoding: utf-8
# """
# @author: github/100101001
# @contact: 17702113437@163.com
# @time: 2020/4/11 下午5:07
# @file: main.py
# @desc: 初始化Celery配置
# """
# import flask
# from celery import Celery
#
#
# class FlaskCelery(Celery):
#
#     def __init__(self, *args, **kwargs):
#
#         super(FlaskCelery, self).__init__(*args, **kwargs)
#         self.patch_task()
#
#         if 'app' in kwargs:
#             self.init_app(kwargs['app'])
#
#     def patch_task(self):
#         TaskBase = self.Task
#         _celery = self
#
#         class ContextTask(TaskBase):
#             abstract = True
#
#             def __call__(self, *args, **kwargs):
#                 if flask.has_app_context():
#                     return TaskBase.__call__(self, *args, **kwargs)
#                 else:
#                     with _celery.app.app_context():
#                         return TaskBase.__call__(self, *args, **kwargs)
#
#         self.Task = ContextTask
#
#     def init_app(self, app):
#         self.app = app
#         self.config_from_object(app.config)

