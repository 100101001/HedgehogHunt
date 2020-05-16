# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/4/29 上午1:09
@file: GoodsCasUtil.py
@desc: 
"""
from common.cahce.core import cas


class GoodsCasUtil:

    lock = cas


    @staticmethod
    def getIntId(item):
        return item[0] if isinstance(item, tuple) else item

    @classmethod
    def judgePair(cls, op_ids, op_exp=0, op_new=0, pair_ids=None, pair_exp=0, pair_new=0):
        """
        op_ids 是指搜索获取到的，对这些id物品进行接口操作，状态一定在redis中的物品
        pair_ids 是指在op_ids上进行操作，引起的连带操作的物品
        成对进行状态校验
        :return:
        """
        total_num = len(op_ids)
        for i in range(total_num):
            ok1 = cls.lock.exec(cls.getIntId(op_ids[i]), op_exp, op_new)
            ok2 = cls.lock.exec_wrap(cls.getIntId(pair_ids[i]), [pair_exp, 'nil'], pair_new)
            if not ok1 or not ok2:
                for o in range(i):
                    cls.lock.exec(cls.getIntId(op_ids[o]), op_new, op_exp)
                    cls.lock.exec(cls.getIntId(pair_ids[o]), pair_new, pair_exp)
                if ok1:
                    cls.lock.exec(cls.getIntId(op_ids[i]), op_new, op_exp)
                if ok2:
                    cls.lock.exec(cls.getIntId(pair_ids[i]), pair_new, pair_exp)
                return False
        return True


    @classmethod
    def judge(cls, goods_ids=None, exp_val=0, new_val=0):
        """
        在id上进行删除之外的操作，比如认领，判断不可以后提示用户存在冲突
        :param goods_ids:
        :param exp_val:
        :param new_val:
        :return:
        """


        total_num = len(goods_ids)
        for i in range(total_num):
            if not cls.lock.exec(cls.getIntId(goods_ids[i]), exp_val, new_val):
                # 回滚
                for o in range(i):
                    cls.lock.exec(cls.getIntId(goods_ids[o]), new_val, exp_val)
                return False
        return True

    @classmethod
    def set(cls, goods_ids=None, exp_val=0, new_val=0):
        """
        不会起冲突，只是设置
        :param goods_ids:
        :param exp_val:
        :param new_val:
        :return:
        """
        for gid in goods_ids:
            cls.lock.exec(cls.getIntId(gid), exp_val, new_val)

    @classmethod
    def filter(cls, goods_ids=None, exp_val=0, new_val=0):
        """
        删除一类的操作，过滤可以删除的进行删除，不提示用户存在冲突
        :param goods_ids:
        :param exp_val:
        :param new_val:
        :return:
        """
        ok_ids = []
        for item in goods_ids:
            if cls.lock.exec_wrap(cls.getIntId(item), [exp_val, 'nil'], new_val):
                ok_ids.append(item)
        return ok_ids

    @classmethod
    def exec_wrap(cls, *args, **kwargs):
        return cls.lock.exec_wrap(*args, **kwargs)

    @classmethod
    def exec(cls, *args, **kwargs):
        return cls.lock.exec(*args, **kwargs)
