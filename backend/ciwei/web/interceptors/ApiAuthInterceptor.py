# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2019/11/09 下午3:10
@file: ApiAuthInterceptor.py 过滤器 (在配置文件中配置无需拦截验证的URL)
@desc:
"""
import re

from flask import request, g

from application import app
from common.cahce.core import CacheQueryService, CacheOpService
from common.models.ciwei.Member import Member



@app.before_request
def before_request_api():
    """
    封号和登录检测
    :return:
    """
    api_ignore_urls = app.config['API_IGNORE_URLS']
    path = request.path
    if '/api' not in path:
        return

    pattern = re.compile('%s' % "|".join(api_ignore_urls))
    if pattern.match(path):
        return

    member_info = check_member_login()
    g.member_info = None
    if member_info:
        if member_info.status != 1:
            resp = {'code': -1, 'msg': '因恶意操作，您已被封号，如有异议请申诉', 'data': {}}
            return resp
        g.member_info = member_info

    return


def check_member_login():
    """
    登录验证
    :return:
    """
    auth_cookie = request.headers.get("Authorization")

    if auth_cookie is None:
        return False

    auth_info = auth_cookie.split("#")

    if len(auth_info) != 2:
        return False

    try:
        member_id = auth_info[1]
        member_info = CacheQueryService.getMemberCache(member_id=member_id)
        if not member_info:
            # 缓存不命中
            member_info = Member.query.filter_by(id=member_id).first()
            CacheOpService.setMemberCache(member_info=member_info)
    except Exception:
        return False

    return member_info
