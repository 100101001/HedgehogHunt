from flask import Flask
from flask_caching import Cache
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate
# from common.libs.UrlManager import UrlManager
import os
from common.libs.search import FlaskEs
from common.tasks import FlaskCelery
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
        # 只用于缓存wx服务端API的 access_token，如果过期再获取更新缓存
        cache.init_app(self, self.config['REDIS'])
        db.init_app(self)
        celery.init_app(self)
        # 强制时区是中国
        os.environ['TZ'] = 'Asia/Shanghai'
        # 日志
        handler = getLoggingHandler()
        self.logger.addHandler(handler)


db = SQLAlchemy()
cache = Cache()
# 异步和定时任务
celery = FlaskCelery()
# __name__ 就是 application
app = Application(__name__, template_folder=APP_ROOT + '/web/templates', root_path=APP_ROOT,
                  static_folder=APP_ROOT + '/web/static')
# 搜索
es = FlaskEs(app)
# 数据库迁移
manager = Manager(app)
migrate = Migrate(app=app, db=db)
migrate.init_app(app, db)
# 应用常数
APP_CONSTANTS = app.config['CONSTANTS']
# """函数模板,将类中的方法引入进来，注入到"""
# app.add_template_global(UrlManager.buildStaticUrl, 'buildStaticUrl')
# app.add_template_global(UrlManager.buildUrl, 'buildUrl')
# app.add_template_global(UrlManager.buildImageUrl, 'buildImageUrl')

# 引入www是测试需要勿删除
from www import *
