SERVER_PORT = 8999
# IP = '127.0.0.1'
IP = '192.168.1.116'
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

# CELERY配置
CELERY_BROKER_URL = 'amqp://root:qweasd123@localhost:5672/ciwei'
CELERY_RESULT_BACKEND = 'redis://localhost:6379'

# 过滤url，登录页面本身的url要跳过
API_IGNORE_URLS = [
    "^/api"
]

STATUS_MAPPING = {
    "1": "正常",
    "0": "已删除"
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
    # TODO: 开通微信支付后,填写商户ID,商户签名密钥
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
    "recommend": "zSCF_j0kTfRvPe8optyb5sx8F25S3Xc9yCvvObXFCh4",
    "finished": "Vx58nqU-cfi07bu4mslzCFhFyGTT52Xk4zlsrwC-MVA",
    "thanks": "gBSM-RF5b3L_PoT3f1u8ibxZMz-qzAsNSZy2LSBPsG8"
}

UPLOAD = {
    'ext': ['jpg', 'bmp', 'jpeg', 'png'],
    'prefix_path': '/web/static/upload/',
    'prefix_url': '/static/upload/'
}

APP = {
    # 'domain': "http://100.68.70.139:8999",
    'domain': "http://" + IP + ":8999",
}

ACS_SMS = {
    'ACCESS_KEY_ID': "LTAIiT0TFPLB4i4j",
    'ACCESS_KEY_SECRET': "UVOjJwxTnT1kv5GpvY4BX7YMDhgWOu",
    'TEMP_IDS': {
        'VERIFY': 'SMS_186612670',
        'NOTIFY': 'SMS_186598289'
    },
    'SIGN_NAMES': {
        'VERIFY': '应寻',
        'NOTIFY': '闪寻'
    }
}
