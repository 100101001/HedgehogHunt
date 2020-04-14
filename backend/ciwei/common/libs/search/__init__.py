# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/4/14 下午4:10
@file: __init__.py.py
@desc: elastic search的初始配置
"""

from elasticsearch import Elasticsearch


class FlaskEs(Elasticsearch):
    def __init__(self, app, **kwargs):
        es_config = app.config.get('ES')
        if es_config:
            url = es_config.get('URL', 'http://localhost:9200')
            super().__init__(url, **kwargs)
