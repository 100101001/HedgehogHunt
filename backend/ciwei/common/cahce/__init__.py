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


class CasLua:
    def __init__(self, flask_redis):
        self.r = flask_redis
        self._lua1 = self.r.register_script("""
        local val = redis.call('get', KEYS[1])
        local ok1 = ARGV[1] == 'nil' and not val
        local ok2 = ARGV[1] == val
        if ok1 or ok2 then
            redis.call('set', KEYS[1], ARGV[2])
            redis.call('expire', KEYS[1], 3600)
            return 1
        else
            return 0
        end
                """)
        self._lua2 = self.r.register_script("""
        local val = redis.call('get', KEYS[1])
        local len = #ARGV
        for i=1, len - 1 do
            if ARGV[i] == 'nil' and not val or ARGV[i] == val then
                redis.call('set', KEYS[1], ARGV[len])
                redis.call('expire', KEYS[1], 3600)
                return 1
            end
        end
        return 0
        """)

    def exec(self, key, expect_val, new_val):
        return int(self._lua1([key], [expect_val, new_val]))

    def exec_wrap(self, key, expected_vals, new_val):
        expected_vals.append(new_val)
        return int(self._lua2([key], expected_vals))


# 基于redis的乐观锁
redis_pool = redis.ConnectionPool(host=app.config['REDIS']['CACHE_REDIS_HOST'],
                                  port=app.config['REDIS']['CACHE_REDIS_PORT'], db=2, max_connections=10)
redis_conn = redis.Redis(connection_pool=redis_pool)
cas = CasLua(flask_redis=redis_conn)
