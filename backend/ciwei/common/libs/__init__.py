# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/4/28 下午7:48
@file: __init__.py
@desc:
"""
class A:
    @staticmethod
    def func(a):
        print("jjj")

class B(A):
    @classmethod
    def func(cls, a):
        super().func("a")
        print("nnn")
        cls.func2("aa")
        cls.func3("3")

    @classmethod
    def func2(cls, n):
        print("222")

    @staticmethod
    def func3(a):
        print("3333")

if __name__ == "__main__":
    B.func("a")