#!/usr/bin/python3.6.8
#Editor weichaoxu

# -*- coding:utf-8 -*-
from flask import Blueprint
route_api=Blueprint('api_page',__name__)
#此处的方法有先后顺序，只有前面先定义了route_api之后，Member里面才能够引用member
#之后才能再引用回来，如果把后面这行代码放到定义route_api之前，那么将会提示无法引用
#********而import *则是把Member中所有代码都引用过来了，这样不会再发生404找不到的错误了
from web.controllers.api.Member import *
from web.controllers.api.User import *
from web.controllers.api.Upload import *
from web.controllers.api.Goods import *
from web.controllers.api.Record import *
from web.controllers.api.Report import *
from web.controllers.api.test import *
from web.controllers.api.Feedback import *
from web.controllers.api.Static import *
from web.controllers.api.Adv import *

@route_api.route("/")
def index():
    return "Jmall Api V1.0"