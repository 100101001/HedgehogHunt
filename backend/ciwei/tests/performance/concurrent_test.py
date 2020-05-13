# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/5/12 上午1:19
@file: concurrent.py
@desc:  http://docs.python-requests.org/zh_CN/latest/user/quickstart.html
# https://cloud.tencent.com/developer/article/1578759
# https://git.weixin.qq.com/minitest/minium-doc/tree/master
# https://python-parallel-programmning-cookbook.readthedocs.io/zh_CN/latest/chapter2/13_Evaluating_the_performance_of_multithread_applications.html
"""

# 同一接口的并发请求，检查功能与性能
from concurrent.futures._base import wait, ALL_COMPLETED
from concurrent.futures.thread import ThreadPoolExecutor
from threading import Thread, Lock

import requests

from tests.performance import response_time, concurrent_output


class ConcurrentTestV2:
    def __init__(self):
        self.pool = ThreadPoolExecutor(max_workers=10, thread_name_prefix='test_')
        self.tasks = []
        self._lock = Lock()
        self.cost = 0
        self.run_times = 0

    def run(self, func, *args):
        future = self.pool.submit(func, *args)
        future.add_done_callback(self._calResponseTimeCallback)
        self.tasks.append(future)

    def _calResponseTimeCallback(self, future):
        with self._lock:
            self.run_times += 1
            self.cost += future.result()

    def avgResponseTime(self):
        wait(self.tasks, return_when=ALL_COMPLETED)
        return round(self.cost/self.run_times, 4)



class ConcurrentTest(Thread):

    def __init__(self, func, *args):
        # 获取运行函数和七参数
        super(ConcurrentTest, self).__init__()
        self.func = func
        self.args = args
        self.res = None

    def run(self):
        self.res = self.func(*self.args)

    def getResult(self):
        Thread.join(self)
        return self.res


class RestfulApis:
    @classmethod
    @response_time
    def releaseGoods(cls, ):
        url = ''
        """
        URL: https://xunhui.opencs.cn/api/goods/create
        HEADERS:
        Authorization: jNssQ1flutxjBE7sbA/oFOWWffKmiGA5Lc8ET223kHMUfTx/DNXL8WFrOgjY+X19
        content-type: application/x-www-form-urlencoded
        
        FORM DATA:
        os_location: 上海市杨浦区彰武路,同济大学四平路校区-图书馆,31.283310854,121.504270427
        goods_name: 校园卡
        mobile: 17717852647
        owner_name: 李依璇
        summary: 测试发布
        business_type: 1
        location: 
        img_list: http://tmp/wx3a7bac4ab0184c76.o6zAJsyTdR5-7tTXbaZ78VVTtlBI.wXE2trQcvPnab0bf49b34f7e854791e85f13e4b9e5b3.jpg
        is_top: 0
        days: 0
        edit: 0
        """
        auth = 'jNssQ1flutxjBE7sbA/oFOWWffKmiGA5Lc8ET223kHMUfTx/DNXL8WFrOgjY+X19'
        content_type = 'application/x-www-form-urlencoded'

        requests.post(url=url, data={}, headers={'Authorization': auth, 'content-type': content_type})

    @classmethod
    @response_time
    def getNewHint(cls):
        url = 'https://xunhui.opencs.cn/api/member/new/hint'
        auth = 'jNssQ1flutxjBE7sbA/oFOWWffKmiGA5Lc8ET223kHMUfTx/DNXL8WFrOgjY+X19'
        resp = requests.get(url, headers={'Authorization': auth})
        if resp.status_code != 200:
            raise Exception('出错了')

    @classmethod
    @response_time
    def searchGoods(cls, mix_kw, owner_name, address):
        url = 'https://xunhui.opencs.cn/api/goods/search?status=0&' \
              'mix_kw={0}&owner_name={1}&p=1&business_type=1&filter_address={2}'.format(mix_kw, owner_name, address)
        resp = requests.get(url=url)
        if resp.status_code != 200:
            raise Exception('出错了')


class TestInitiator:
    concurrent_num = 100

    def __init__(self):
        self.f = open('outputs/current_test.log', 'w')
        self.test_executor = ConcurrentTestV2()

    def runAll(self):
        all_tests = self.__testMethods()
        for t in all_tests:
            m = getattr(self, t, None)
            if m:
                m()

    def __del__(self):
        self.f.close()

    def old_initiate(self, func, concurrent_num=100, argsGen=None):
        ths = []

        @response_time
        def __concurrentApiCall():
            for i in range(concurrent_num):
                th = ConcurrentTest(func, *argsGen() if argsGen else ())
                ths.append(th)
            for t in ths:
                t.start()

        call_duration = round(__concurrentApiCall(), 4)

        def __calAverage():
            cost = 0.0
            for t in ths:
                cost += t.getResult()
            return round(cost / concurrent_num, 4)

        return call_duration, concurrent_num, func.__name__, __calAverage()

    def initiate(self, func, concurrent_num=100, argsGen=None):
        @response_time
        def __concurrentApiCall():
            for i in range(concurrent_num):
                self.test_executor.run(func, *argsGen() if argsGen else ())
        call_duration = round(__concurrentApiCall(), 4)
        return call_duration, concurrent_num, func.__name__, self.test_executor.avgResponseTime()

    @concurrent_output
    def test_initiateSearch(self):
        import random

        def searchFilterGen():
            mix_kw = ''.join([chr(random.randint(0x4e00, 0x9fbf)) for _ in range(3)])
            owner_name = ''.join([chr(random.randint(0x4e00, 0x9fbf)) for _ in range(3)])
            goods_name = ''.join([chr(random.randint(0x4e00, 0x9fbf)) for _ in range(3)])
            return mix_kw, owner_name, goods_name

        concurrent_num = 100
        return self.initiate(RestfulApis.searchGoods, concurrent_num, searchFilterGen)

    @concurrent_output
    def test_initiateHint(self):
        concurrent_num = 100
        return self.initiate(RestfulApis.getNewHint, concurrent_num)

    def __testMethods(self):
        return list(filter(lambda m: m.startswith("test_")
                                     and callable(getattr(self, m)), dir(self)))

    def __allMethods(self):
        return list(filter(lambda m: not m.startswith("__") and not m.endswith("__")
                                     and callable(getattr(self, m)), dir(self)))


if __name__ == '__main__':
    test_runner = TestInitiator()
    test_runner.runAll()
    # out_put_rows = [test_runner.initiateSearch()]
