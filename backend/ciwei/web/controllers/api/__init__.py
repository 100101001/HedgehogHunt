# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2019/12/10 下午1:11
@file: __init__.py
@desc:
"""
from flask import Blueprint

route_api = Blueprint('api_page', __name__)

from web.controllers.api.Member import *
from web.controllers.api.User import *
from web.controllers.api.Goods import *
from web.controllers.api.Thanks import *
from web.controllers.api.Record import *
from web.controllers.api.Report import *
from web.controllers.api.Appeal import *
from web.controllers.api.Feedback import *
from web.controllers.api.Static import *
from web.controllers.api.Adv import *
from web.controllers.api.QrCode import *
from web.controllers.api.mall.Product import *
from web.controllers.api.mall.Cart import *
from web.controllers.api.mall.ProductOrder import *
from web.controllers.api.mall.Address import *
from web.controllers.api.mall.My import *

