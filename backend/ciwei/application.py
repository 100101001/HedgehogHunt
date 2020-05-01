import os

from flask import Flask

from common.loggin import getLoggingHandler

# 测试需要使用绝对路径无论从哪里调用都共用base_setting.py
APP_ROOT = os.path.dirname(os.path.abspath(__file__))


class Application(Flask):
    def __init__(self, import_name, template_folder=None, static_folder=None, root_path=None):
        super(Application, self).__init__(import_name, template_folder=template_folder, static_folder=static_folder,
                                          root_path=root_path)

        self.config.from_pyfile('config/base_setting.py')
        # self.config.from_pyfile('config/production_setting.py')
        # if 'ops_config' in os.environ:
        #     self.config.from_pyfile('config\\%s_setting.py' % os.environ['ops_config'])
        # 只用于缓存wx服务端API的 access_token，如果过期再获取更新缓
        # 强制时区是中国
        os.environ['TZ'] = 'Asia/Shanghai'
        # 日志
        handler = getLoggingHandler()
        self.logger.addHandler(handler)


# __name__ 就是 application
app = Application(__name__, template_folder=APP_ROOT + '/web/templates', root_path=APP_ROOT,
                  static_folder=APP_ROOT + '/web/static')
APP_CONSTANTS = app.config['CONSTANTS']
# Celery 做异步和定时任务
from common.tasks import FlaskCelery

celery = FlaskCelery()
celery.init_app(app)
# elasticSearch 做搜索
from common.search import FlaskEs

es = FlaskEs(app)
# SQLAlchemy 数据库,兼具同步服务
from common.sync.db import SyncQuery
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy(query_class=SyncQuery)
db.init_app(app)
from common.sync.db.listeners import *
from common.loggin.db.listeners import *
from common.models.triggers import *
# 数据库迁移
from flask_migrate import Migrate
from flask_script import Manager

manager = Manager(app)
migrate = Migrate(app=app, db=db)
migrate.init_app(app, db)
# 应用常数

# """函数模板,将类中的方法引入进来，注入到"""
# app.add_template_global(UrlManager.buildStaticUrl, 'buildStaticUrl')
# app.add_template_global(UrlManager.buildUrl, 'buildUrl')
# app.add_template_global(UrlManager.buildImageUrl, 'buildImageUrl')

# 引入www是测试需要勿删除
from www import *
