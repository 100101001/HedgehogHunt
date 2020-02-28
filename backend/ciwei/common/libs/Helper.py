#!/usr/bin/python3.6.8

# -*- coding:utf-8 -*-

from flask import g
from flask import render_template
import datetime
import uuid

from common.models.ciwei.Member import Member


def iPagination(params):
    import math

    ret = {
        "is_prev": 1,
        "is_next": 1,
        "from": 0,
        "end": 0,
        "current": 0,
        "total_pages": 0,
        "page_size": 0,
        "total": 0,
        "url": params['url']
    }

    total = int(params['total'])
    page_size = int(params['page_size'])
    page = int(params['page'])
    display = int(params['display'])
    total_pages = int(math.ceil(total / page_size))
    total_pages = total_pages if total_pages > 0 else 1
    if page <= 1:
        ret['is_prev'] = 0

    if page >= total_pages:
        ret['is_next'] = 0

    semi = int(math.ceil(display / 2))

    if page - semi > 0:
        ret['from'] = page - semi
    else:
        ret['from'] = 1

    if page + semi <= total_pages:
        ret['end'] = page + semi
    else:
        ret['end'] = total_pages

    ret['current'] = page
    ret['total_pages'] = total_pages
    ret['page_size'] = page_size
    ret['total'] = total
    ret['range'] = range(ret['from'], ret['end'] + 1)
    return ret


'''
统一渲染方法，用于包装一次渲染模板的方法，以实现传输g变量的功能
如果某个方法需要写很多次，那说不定就是可以用再次包装的方式来进行统一部署，以实现一次编写
'''


def ops_render(template, context={}):
    if 'current_user' in g:
        context['current_user'] = g.current_user

    return render_template(template, **context)


'''
统一的获取时间方法
'''


def getCurrentDate(date_format="%Y-%m-%d %H:%M:%S"):
    return datetime.datetime.now().strftime(date_format)


def str2seconds(format_time='', date_format="%Y-%m-%d %H:%M:%S"):
    """
    将格式时间串转成时间戳
    :param format_time:
    :param date_format:
    :return:
    """
    import time
    return time.mktime(time.strptime(format_time, date_format))


def seconds2str(seconds, date_format="%Y-%m-%d %H:%M:%S"):
    """
    时间戳转成时间串
    :param seconds:
    :param date_format:
    :return:
    """
    import time
    return time.strftime(date_format, time.localtime(seconds))

def datetime2str(target, date_format="%Y-%m-%d %H:%M:%S"):
    return target.strftime(date_format)

'''
根据某个字段获取一个dict值出来
'''


def getDictFilterField(db_model, select_field, key_field, field_list):
    """
    从表中获取key_field值在field_list中的所有记录
    构造 field_value -> model 字典
    :param db_model: 实体(表)
    :param select_field: 实体属性
    :param key_field: 表字段
    :param field_list:
    :return:
    """
    ret = {}
    query = db_model.query
    if field_list and len(field_list) > 0:
        # filter_by只能做简单的查询，filter才可以做复杂的查询功能
        query = query.filter(select_field.in_(field_list))

    model_list = query.all()
    if not model_list:
        return ret
    for item in model_list:
        # 跳过继续循环
        if not hasattr(item, key_field):
            continue
        ret[getattr(item, key_field)] = item
    return ret


def selectFilterObj(obj, field):
    """
    从对象列表中取出属性列表
    :param obj: 对象列表
    :param field: 属性
    :return: 属性列表
    """
    ret = []
    new_obj = []
    for item in obj:
        if not hasattr(item, field):
            continue
        if getattr(item, field) in ret:
            continue

        ret.append(getattr(item, field))
        # if field == 'member_id':
        #     member_info = Member.query.filter_by(id=item.member_id).first()
        #     if not member_info:
        #         continue
        #     else:
        #         ret.append(getattr(item, field))
        #         new_obj.append(item)
        # else:
        #     ret.append(getattr(item, field))
        #     new_obj.append(item)

    return ret


def getUuid():
    # uuid基本可以保证唯一性
    # 根据设备硬件生成32位的随机字符串
    # uuid4可能会重复，所以使用uuid5
    now = datetime.datetime.now()
    uuid_now = str(uuid.uuid5(uuid.NAMESPACE_DNS, now.strftime("%Y%m%d%H%M%S"))).replace("-", "")
    return uuid_now


from datetime import datetime as cdatetime  # 有时候会返回datatime类型

from datetime import date, time

from flask_sqlalchemy import Model

from sqlalchemy import DateTime, Numeric, Date, Time  # 有时又是DateTime


def queryToDict(models):
    if isinstance(models, list):

        if isinstance(models[0], Model):

            lst = []

            for model in models:
                gen = model_to_dict(model)

                dit = dict((g[0], g[1]) for g in gen)

                lst.append(dit)

            return lst

        else:

            res = result_to_dict(models)

            return res

    else:

        if isinstance(models, Model):

            gen = model_to_dict(models)

            dit = dict((g[0], g[1]) for g in gen)

            return dit

        else:

            res = dict(zip(models.keys(), models))

            find_datetime(res)

            return res


# 当结果为result对象列表时，result有key()方法

def result_to_dict(results):
    res = [dict(zip(r.keys(), r)) for r in results]

    # 这里r为一个字典，对象传递直接改变字典属性

    for r in res:
        find_datetime(r)

    return res


def model_to_dict(model):  # 这段来自于参考资源

    for col in model.__table__.columns:

        if isinstance(col.type, DateTime):

            value = convert_datetime(getattr(model, col.name))

        elif isinstance(col.type, Numeric):

            value = float(getattr(model, col.name))

        else:

            value = getattr(model, col.name)

        yield (col.name, value)


def find_datetime(value):
    for v in value:

        if (isinstance(value[v], cdatetime)):
            value[v] = convert_datetime(value[v])  # 这里原理类似，修改的字典对象，不用返回即可修改


def convert_datetime(value):
    if value:

        if (isinstance(value, (cdatetime, DateTime))):

            return value.strftime("%Y-%m-%d %H:%M:%S")

        elif (isinstance(value, (date, Date))):

            return value.strftime("%Y-%m-%d")

        elif (isinstance(value, (Time, time))):

            return value.strftime("%H:%M:%S")

    else:

        return ""
