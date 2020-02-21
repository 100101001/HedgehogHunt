# -*- coding: utf-8 -*-
import time
from application import app


class UrlManager(object):
    def __init__(self):
        pass

    @staticmethod
    def buildUrl(path):
        return path

    @staticmethod
    def buildStaticUrl(path):
        # 如果配置文件里面没有设置版本号这个参数，则取时间戳，如果设置了，那么直接取配置好的版本号
        # release_version=app.config.get('RELEASE_VERSION')
        # ver = "%s"%(int(time.time())) if not release_version else release_version
        ver = "%s" % (int(time.time()))
        path = "/static" + path + "?ver=" + ver
        return UrlManager.buildUrl(path)

    @staticmethod
    def buildImageUrl(path, image_type='UPLOAD'):
        """
        :param path:
        :param image_type: 0-UPLOAD, 1-QR_CODE
        :return:
        """
        # 返回绝对路径
        # url='域名'+"图片前缀"+"key"
        app_config = app.config
        url = app_config['APP']['domain'] + app_config[image_type]['prefix_url'] + path
        return url

    @staticmethod
    def buildApiUrl(route):
        return app.config['APP']['domain'] + "/api" + route
