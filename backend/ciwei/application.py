from flask import Flask
from flask_caching import Cache
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
# from common.libs.UrlManager import UrlManager
import os


class Application(Flask):
    def __init__(self, import_name, template_folder=None, static_folder=None, root_path=None):
        # super(Application,self).__init__(import_name,template_folder=template_folder,static_folder=None,root_path=root_path)
        super(Application, self).__init__(import_name, template_folder=template_folder, static_folder=static_folder,
                                          root_path=root_path)
        self.config.from_pyfile('config/base_setting.py')

        # if 'ops_config' in os.environ:
        #   self.config.from_pyfile('config\\%s_setting.py' % os.environ['ops_config'])
        cache.init_app(self)
        db.init_app(self)


db = SQLAlchemy()
cache = Cache(config={'CACHE_TYPE': 'simple', 'CACHE_DEFAULT_TIMEOUT': 90})
# app=Application(__name__,template_folder=os.getcwd()+'/web/templates',root_path=os.getcwd(),static_folder=os.getcwd()+'/web/static')
app = Application(__name__, root_path=os.getcwd(), static_folder=os.getcwd() + '/web/static')
manager = Manager(app)

# """函数模板,将类中的方法引入进来，注入到"""
# app.add_template_global(UrlManager.buildStaticUrl, 'buildStaticUrl')
# app.add_template_global(UrlManager.buildUrl, 'buildUrl')
# app.add_template_global(UrlManager.buildImageUrl, 'buildImageUrl')
