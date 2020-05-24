# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/5/12 上午1:19
@file: concurrent_test.py
@desc:  http://docs.python-requests.org/zh_CN/latest/user/quickstart.html
# https://cloud.tencent.com/developer/article/1578759
# https://git.weixin.qq.com/minitest/minium-doc/tree/master
# https://python-parallel-programmning-cookbook.readthedocs.io/zh_CN/latest/chapter2/13_Evaluating_the_performance_of_multithread_applications.html
"""

# 同一接口的并发请求，检查功能与性能
from tests.performance import concurrent_output, loop_call_duration
from tests.performance.performance_test_base import RestfulApisCallerAsync


class ConcurrentTestInitiator(RestfulApisCallerAsync):
    def __init__(self):
        super(ConcurrentTestInitiator, self).__init__('concurrent_test.log', 'concurrent_call.log')
        self._callers = self.getAllModuleCallers()

    @concurrent_output
    def runAll(self, mixed_concurrent_num=10):
        @loop_call_duration
        def __concurrentApiCall():
            for i in range(mixed_concurrent_num):
                self.random_call()

        call_duration = round(__concurrentApiCall(), 4)
        return call_duration, mixed_concurrent_num, ','.join(self.getAllModuleCallers()), self.avgResponseTime()


if __name__ == '__main__':
    test_runner = ConcurrentTestInitiator()
    test_runner.runAll(1000)
