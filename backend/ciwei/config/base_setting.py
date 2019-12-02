SERVER_PORT = 8999
IP = '127.0.0.1'
# IP='100.68.70.139'
DEBUG = True
SQLALCHEMY_ECHO = True

PAGE_SIZE = 50
PAGE_DISPLAY = 10

SQLALCHEMY_DATABASE_URI = 'mysql://root:wcx9517530@127.0.0.1/ciwei_db'
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ENCODING = 'utf-8'

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

    #Uni-济旦财APPID
    #'appid': 'wx3dcef10870796776',
    #'appkey': 'b0624f70f278c11ceb560874dd5948c7',

    # 济人济市APPID
    'appid': 'wx3a7bac4ab0184c76',
    'appkey': 'bd8a906e46adc59dd0e7e3110e90c46c'
}

UPLOAD = {
    'ext': ['jpg', 'bmp', 'jpeg', 'png'],
    'prefix_path': '/web/static/upload/',
    'prefix_url': '/static/upload/'
}

APP = {
    # 'domain':'http://0.0.0.0:8999'
    # 'domain':'http://192.168.31.66:8999'
    # 'domain': "http://100.68.70.139:8999",
    'domain': "http://" + IP + ":8999",
}
