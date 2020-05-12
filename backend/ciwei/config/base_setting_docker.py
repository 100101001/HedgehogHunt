# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/5/9 上午11:07
@file: base_setting_docker.py.py
@desc: 
"""

SQLALCHEMY_DATABASE_URI = 'mysql://root:wcx9517530@db/ciwei_db?charset=utf8mb4'
# celery 异步任务框架的配置
BROKER_URL = 'amqp://root:qweasd123@rmq/ciwei'
CELERY_RESULT_BACKEND = 'redis://:lyx147@redis/0'

# elastic search 的配置
ES = {
    'URL': 'http://es:9200',
    'INDEX': 'goods'
}
