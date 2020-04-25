# -*- coding: utf-8 -*-

import re

from flask import request, g, jsonify

from application import app
from common.cahce import CacheQueryService, CacheOpService
from common.models.ciwei.Member import Member

'''
api认证
'''


@app.before_request
def before_request_api():
    api_ignore_urls = app.config['API_IGNORE_URLS']
    path = request.path
    if '/api' not in path:
        return

    pattern = re.compile('%s' % "|".join(api_ignore_urls))
    if pattern.match(path):
        return
    # if path in api_ignore_urls:
    #     return

    member_info = check_member_login()
    g.member_info = None
    if member_info:
        if member_info.status != 1:
            resp = {'code': -1, 'msg': '因恶意操作，您已被封号，如有异议请申诉', 'data': {}}
            return resp
        g.member_info = member_info

    return


'''
判断用户是否已经登录
'''


def check_member_login():
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
