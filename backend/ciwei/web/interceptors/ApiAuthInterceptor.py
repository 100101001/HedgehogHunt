# -*- coding: utf-8 -*-
import json

from application import app
from flask import request, g, jsonify

from common.cahce import redis_conn_db_1
from common.libs.Helper import queryToDict
from common.models.ciwei.Member import Member
import re

'''
api认证
'''


@app.before_request
def before_request_api():
    api_ignore_urls = app.config['API_IGNORE_URLS']
    path = request.path
    if '/api' not in path:
        return

    member_info = check_member_login()
    g.member_info = None
    if member_info:
        g.member_info = member_info

    pattern = re.compile('%s' % "|".join(api_ignore_urls))
    if pattern.match(path):
        return

    if not member_info:
        resp = {'code': -1, 'msg': 'please login~', 'data': {}}
        return jsonify(resp)

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
        mem_key = 'member_{0}'.format(str(member_id))
        member_str = redis_conn_db_1.get(mem_key)
        if not member_str:
            member_info = Member.query.filter_by(id=member_id).first()
            redis_conn_db_1.set(mem_key, json.dumps(queryToDict(member_info)))
        else:
            member_info = Member()
            member_info.__dict__ = json.loads(member_str)
    except Exception:
        return False

    if member_info is None:
        return False

    # if auth_info[0] != MemberService.geneAuthCode( member_info ):
    #     return False
    #
    if member_info.status != 1:
        return False

    return member_info
