

'''
蓝图功能，对所有的url进行统一的配置
'''

from application import app

#导入文件夹时默认访问的就是init文件，所以不需要api.init
from web.controllers.api import route_api
app.register_blueprint(route_api,url_prefix='/api')

from web.controllers.exception import exception
app.register_blueprint(exception, url_prefix='/error')

#用于加载静态文件，没有这个路由则图片都无法加载
from web.controllers.static import route_static
app.register_blueprint(route_static,url_prefix='/static')



'''
统一拦截器
'''
from web.interceptors.ApiAuthInterceptor import *