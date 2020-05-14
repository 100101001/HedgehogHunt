# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/5/12 下午3:59
@file: test_setting_docker.py
@desc: 
"""
SQLALCHEMY_DATABASE_URI = 'mysql://root:wcx9517530@db/ciwei_db_test?charset=utf8mb4'
CELERY_RESULT_BACKEND = 'redis://:lyx147@redis/5'
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
        'HOT': 6,
        'CAS': 7,
        'LOST': 8,
        'FOUND': 9
    },
    'CACHE_REDIS_PASSWORD': 'lyx147'
}

CONSTANTS = {
    'time_format_short': '%Y-%m-%d %H:%M',
    'time_format_long': '%Y-%m-%d %H:%M:%S',
    'sub_time_format': '%Y年%m月%d日 %H:%M',
    'sys_author': {
        'member_id': '100001',
        'openid': 'bPk3u33u+sqUiuxJ/+ubfQ==',
        'avatar': 'https://wx.qlogo.cn/mmopen/vi_32/7jCR4QflwchksTBcyakicSepWVQdfbHIQL2glRrkY7ic52iaXqfuBb2tlQ8ELlaGWZDXFgKM4zAMeQZSiaaJtibI3gQ/132',
        'nickname': '鲟回-管理员'
    },
    'default_lost_loc': '不知道###不知道###0###0',
    'default_loc': ['不知道', '不知道', 0, 0],
    'is_all_user_val': '1',
    'stuff_type': {
        'goods': 1,
        'thanks': 0
    },
    'page_size': 10,
    'max_pages_allowed': 50,
    'sp_product': {
        'client_mobile': '17717852647',
        'qrcode': {
            'id': 15,
            'price': 0.02
        },
        'sms_pkg': {
            'id': 16,
            'price': 4.5
        },
        'sms': {
            'id': 17,
            'price': 0.1
        },
        'top': {
            'price': 0.02,
            'days': 7
        },
        'free_sms': {
            'times': 5
        }
    }
}