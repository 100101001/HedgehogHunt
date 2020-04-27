# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/4/26 下午3:16
@file: GoodProxy.py
@desc: 
"""

from datetime import datetime
from decimal import Decimal


class Good:
    now = datetime.now()
    id = 0
    user_id = 0
    member_id = 100001
    openid = ""
    nickname = ""
    avatar = ""
    mobile = ""
    owner_id = 100002
    name = ""
    owner_name = ""
    os_location = ""
    location = ""
    target_price = Decimal("0.00")
    main_image = ""
    pics = ""
    summary = ""
    business_type = 1
    qr_code_openid = ""
    return_goods_id = 0
    return_goods_openid = ""
    status = 1
    view_count = 0
    top_expire_time = now
    recommended_times = 0
    report_status = 0
    confirm_time = now
    finish_time = now
    thank_time = now
    appeal_time = now
    updated_time = now
    created_time = now
