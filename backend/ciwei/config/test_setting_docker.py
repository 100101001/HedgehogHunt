# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/5/12 下午3:59
@file: test_setting_docker.py
@desc: 
"""
SQLALCHEMY_DATABASE_URI = 'mysql://root:wcx9517530@db/ciwei_db_test?charset=utf8mb4'
# elastic search 的配置
ES = {
    'URL': 'http://es:9200',
    'INDEX': 'goods_test'
}

# cache 缓存的配置
REDIS = {
    'CACHE_REDIS_HOST': 'redis',
    'CACHE_REDIS_PORT': 6379,
    'CACHE_REDIS_DB': {
        'HOT': 5,
        'CAS': 6,
        'LOST': 7,
        'FOUND': 8
    },
    'CACHE_REDIS_PASSWORD': 'lyx147'
}