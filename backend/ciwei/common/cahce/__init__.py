# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/4/12 下午11:49
@file: __init__.py.py
@desc:  基于redis的CAS乐观锁
"""
import redis

from application import app
from flask_redis import FlaskRedis

class CasLua:
    def __init__(self, flask_redis):
        self.r = flask_redis
        self._lua = self.r.register_script("""
        local val = redis.call('get', KEYS[1])
        local ok1 = ARGV[1] == 'nil' and not val
        local ok2 = ARGV[1] == val
        if ok1 or ok2 then
            redis.call('set', KEYS[1], ARGV[2])
            return 1
        else
            return 0
        end
                """)

    def exec(self, key, expect_val, new_val):
        return int(self._lua([key], [expect_val, new_val]))


# 基于redis的乐观锁
redis_pool = redis.ConnectionPool(host=app.config['REDIS']['CACHE_REDIS_HOST'],
                                  port=app.config['REDIS']['CACHE_REDIS_PORT'], max_connections=10, db=2)
redis = redis.Redis(redis_pool)
cas = CasLua(flask_redis=redis)
