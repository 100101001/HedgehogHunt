# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/5/12 上午1:22
@file: reliability_test.py
@desc: 
"""

# 负载70~90，检查系统稳定性
from threading import Timer

from tests.performance.performance_test_base import RestfulApisCallerAsync

timer = None
counter = 0


class ReliabilityTestInitiator(RestfulApisCallerAsync):

    def runAll(self, high_load_num=100):
        # 参数可通过性能-负载曲线获得
        for i in range(high_load_num):
            self.random_call()
        global timer
        global counter
        counter += 1
        if counter < 10:
            timer = Timer(5, self.runAll)
            timer.start()


if __name__ == '__main__':
    test_runner = ReliabilityTestInitiator()
    test_runner.runAll(100)
