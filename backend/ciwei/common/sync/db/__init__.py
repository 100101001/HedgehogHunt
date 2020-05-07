# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/4/26 下午1:28
@file: __init__.py.py
@desc: 
"""
from flask_sqlalchemy import BaseQuery


class SyncQuery(BaseQuery):
    def update(self, values, synchronize_session=None, update_args=None, redis_arg=None):
        def __setRedisArg(arg=None):
            if arg in (-1, 0):
                return {'typo': 'rem', 'rem': dict(business_type=-arg)}
            elif arg == 1:
                return {'typo': 'add', 'add': dict()}

        self.session.redis_arg = __setRedisArg(redis_arg)
        synchronize_session = 'fetch' if synchronize_session is None else synchronize_session
        return super().update(values, synchronize_session=synchronize_session, update_args=update_args)
