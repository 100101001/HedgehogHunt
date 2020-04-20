from celery.schedules import crontab

SERVER_PORT = 8999
# IP = '127.0.0.1'
IP = '192.168.0.116'
# IP='100.68.70.139'
# IP='47.102.201.193'
DEBUG = True

# MYSQL数据库配置
SQLALCHEMY_ECHO = True

PAGE_SIZE = 50
PAGE_DISPLAY = 10

SQLALCHEMY_DATABASE_URI = 'mysql://root:wcx9517530@47.102.201.193/ciwei_db_test?charset=utf8mb4'
# SQLALCHEMY_DATABASE_URI = 'mysql://root:wcx9517530@188.131.240.205/ciwei_db1?charset=utf8mb4'
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ENCODING = 'utf-8'

# celery 异步任务框架的配置
BROKER_URL = 'amqp://root:qweasd123@localhost:5672/ciwei'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_TIMEZONE = 'Asia/Shanghai'
CELERY_ENABLE_UTC = True
# celery 日志文件
CELERYD_LOG_FILE = '/home/ellen/repos/HedgehogHunt/backend/logs/celery-beats.log'
CELERYBEAT_LOG_FILE = '/home/ellen/repos/HedgehogHunt/backend/logs/celery-beats.log'
# celery 消息序列器
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
# celery 定时任务
CELERYBEAT_SCHEDULE = {
    # 30分钟未支付订单自动关单
    'auto_close_expire_order_every_quarter': {
        'task': 'mall.auto_close_expire_order',
        'schedule': crontab(minute='*/15'),  # 每15分钟执行一次
        'options': {'queue': 'mall_queue', 'routing_key': 'for_mall', 'delivery_mode': 'transient'}  # 定时清理的消息如果丢失是没有关系的
    },
    'incr_read_count_to_db_every_day': {
        'task': 'sync.incr_read_count_to_db',
        'schedule':  crontab(minute=0, hour=0),  # 每天的凌晨执行任务
        'options': {'queue': 'sync_queue', 'routing_key': 'for_sync'}
    }
}
# celery 检查schedule中是否有要执行的任务的间隔可以睡10分钟
CELERYBEAT_MAX_LOOP_INTERVAL = 600
# celery的任务队列  ## exchange_type有:1:N, N:1, 1:1
CELERY_QUEUES = {
    'mall_queue': {  # 指定各个队列的exchange,和worker处理来自不同队列任务时的优先级。同一队列的任务优先级通过@task的property属性设定。
        'exchange': 'mall_queue',
        'exchange_type': 'direct',
        'routing_key': 'for_mall',
        'consumer_arguments': {'x-priority': 5}
    },
    'sms_queue': {
        'exchange': 'sms_queue',
        'exchange_type': 'direct',
        'routing_key': 'for_sms',
        'consumer_arguments': {'x-priority': 5}
    },
    'recommend_queue': {
        'exchange': 'recommend_queue',
        'exchange_type': 'direct',
        'routing_key': 'for_recommend',
        'consumer_arguments': {'x-priority': 1}
    },
    'subscribe_queue': {
        'exchange': 'subscribe_queue',
        'exchange_type': 'direct',
        'routing_key': 'for_subscribe',
        'consumer_arguments': {'x-priority': 1}
    },
    'sync_queue': {
        'exchange': 'sync_queue',
        'exchange_type': 'direct',
        'routing_key': 'for_sync',
        'consumer_arguments': {'x-priority': 10}
    },
    'log_queue': {
        'exchange': 'log_queue',
        'exchange_type': 'direct',
        'routing_key': 'for_log',
        'consumer_arguments': {'x-priority': 5}
    }
}
# celery任务路由
CELERY_ROUTES = {
    'sms.*': {
        'queue': 'sms_queue',
        'routing_key': 'for_sms'
    },
    'recommend.*': {
        'queue': 'recommend_queue',
        'routing_key': 'for_recommend'
    },
    'subscribe.*': {
        'queue': 'subscribe_queue',
        'routing_key': 'for_subscribe'
    },
    'mall.*': {
        'queue': 'mall_queue',
        'routing_key': 'for_mall'
    },
    'log.wechat.subscribe': {
        'queue': 'log',
        'routing_key': 'for_log',
        'delivery_mode': 'transient'  # 丢失也无所谓，关闭默认的消息持久化，提升速度
    },
    'sync.*': {
        'queue': 'sync_queue',
        'routing_key': 'for_sync'
    }
}

# cache 缓存的配置
REDIS = {
    'CACHE_TYPE': 'redis',
    'CACHE_DEFAULT_TIMEOUT': 60*60*24,
    'CACHE_REDIS_HOST': 'localhost',
    'CACHE_REDIS_PORT': 6379,
    'CACHE_REDIS_DB': 1,
    'CACHE_REDIS_PASSWORD': ''
}

# elastic search 的配置
ES = {
    'URL': 'http://localhost:9200',
    'DOC_TYPE': 'search_recommend',
    'INDEX': 'goods'
}

# 过滤url，登录页面本身的url要跳过
API_IGNORE_URLS = [
    '^/api'
]

STATUS_MAPPING = {
    '1': '正常',
    '0': '已删除'
}

OPENCS_APP = {
    # OPENCS小程序APPID
    # 'appid':'wx5200a1c1ec8db155',
    # 'appkey':'edc155dc275e436903943e7d5090080e',

    # Uni-济旦财APPID
    # 'appid': 'wx3dcef10870796776',
    # 'appkey': 'b0624f70f278c11ceb560874dd5948c7',

    # 济人济市APPID
    'appid': 'wx3a7bac4ab0184c76',
    'appkey': 'bd8a906e46adc59dd0e7e3110e90c46c',
    'mch_id': '1578527401',
    'mch_key': '01e1856cee125886ad9b3314e52dbc87',
    'callback_url': '/api/order/callback'
}

UNIS = {
    'ext': ['jpg', 'bmp', 'jpeg', 'png'],
    'prefix_path': '/web/static/unis/',
    'prefix_url': '/static/unis/'
}

PRODUCT = {
    'ext': ['jpg', 'bmp', 'jpeg', 'png'],
    'prefix_path': '/web/static/product/',
    'prefix_url': '/static/product/'
}

QR_CODE = {
    'ext': 'jpg',
    'prefix_path': '/web/static/qr_code/',
    'prefix_url': '/static/qr_code/'
}

SUBSCRIBE_TEMPLATES = {
    'recommend': 'eT6wS62k3KzRNagqnZOd_Fuui0As0GBX7fYfpUSyi0Y',  # 给寻物启事发帖者发送匹配通知
    'finished_found':  '_dAjVN6DHEewP_z01WhKXlZ7xY9nfs_OEtVbnBC88MU',  # 向失物招领发布者发送被取回的通知
    'finished_return': '4JEcTuWKyXwYQM2kYbQoPkG8WBB52cKdsP9FxiSSqEY',  # 归还者归还时订阅，如果对方确认或者取回了，发送
    'return': 'bHZTF62ciS-03u8MmGe0cA7YMVHdGpwH-bY9wrmfDfY',  # 给寻物启事发帖者，如果有人归还就通知
    'thanks': 'MxeBoTL5FcGb8DGtQtsoesFS5VmEd67KlRtMAQj8hoI'  # 给失物招领发帖者发送答谢通知
}

UPLOAD = {
    'ext': ['jpg', 'bmp', 'jpeg', 'png'],
    'prefix_path': '/web/static/upload/',
    'prefix_url': '/static/upload/'
}

APP = {
    # 'domain': 'http://100.68.70.139:8999',
    'domain': 'http://' + IP + ':8999',
}

ACS_SMS = {
    'ACCESS_KEY_ID': 'LTAIiT0TFPLB4i4j',
    'ACCESS_KEY_SECRET': 'UVOjJwxTnT1kv5GpvY4BX7YMDhgWOu',
    'TEMP_IDS': {
        'VERIFY': 'SMS_186612670',
        'NOTIFY': 'SMS_186598289'
    },
    'SIGN_NAMES': {
        'VERIFY': '应寻',
        'NOTIFY': '闪寻'
    }
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
    'page_size': 10
}
