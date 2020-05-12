# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/4/30 下午2:17
@file: __init__.py.py
@desc: 
"""
import redis

from application import app

if __name__ == "__main__":
    pass


class CasLua:
    def __init__(self, flask_redis):
        self.r = flask_redis
        # 单个值
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
        # 多个可能的值
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
REDIS_CONF = app.config['REDIS']
REDIS_HOST = REDIS_CONF['CACHE_REDIS_HOST']
REDIS_PORT = REDIS_CONF['CACHE_REDIS_PORT']
REDIS_PWD = REDIS_CONF['CACHE_REDIS_PASSWORD']
REDIS_DBS = REDIS_CONF['CACHE_REDIS_DB']
redis_pool_cas = redis.ConnectionPool(host=REDIS_HOST,
                                      port=REDIS_PORT, password=REDIS_PWD, db=REDIS_DBS['CAS'], max_connections=10,
                                      decode_responses=True)
redis_conn_cas = redis.StrictRedis(connection_pool=redis_pool_cas)
cas = CasLua(flask_redis=redis_conn_cas)
# 由于数据库设计的非冗余导致的频繁数据库查询
redis_pool_cache = redis.ConnectionPool(host=REDIS_HOST,
                                        port=REDIS_PORT, password=REDIS_PWD, db=REDIS_DBS['HOT'], max_connections=10,
                                        decode_responses=True)
redis_conn_cache = redis.StrictRedis(connection_pool=redis_pool_cache)


# 由于匹配，存放在3，4里的 cls -> {id,lng,lat,author_id} === biz_type:1
# 由于匹配，存放在3，4里的 cls -> {id,lng,lat,author_id}  === biz_type:0
redis_pool_lost = redis.ConnectionPool(host=REDIS_HOST,
                                       port=REDIS_PORT, password=REDIS_PWD, db=REDIS_DBS['LOST'], max_connections=10,
                                       decode_responses=True)
redis_conn_lost = redis.StrictRedis(connection_pool=redis_pool_lost)
redis_pool_found = redis.ConnectionPool(host=REDIS_HOST,
                                        port=REDIS_PORT, password=REDIS_PWD, db=REDIS_DBS['FOUND'], max_connections=10,
                                        decode_responses=True)
redis_conn_found = redis.StrictRedis(connection_pool=redis_pool_found)