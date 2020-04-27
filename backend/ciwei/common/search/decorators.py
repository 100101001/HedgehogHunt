# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/4/28 上午2:09
@file: decorators.py
@desc: 
"""
from functools import wraps

from application import APP_CONSTANTS, es
from common.libs import RecordService
from common.sync.core.base.EsService import ES_CONSTANTS


def goods_record_db_search(func):
    @wraps(func)
    def search_and_paginate(*args, **kwargs):
        query = func(*args, **kwargs)
        search_rule = RecordService.searchBarFilter(owner_name=kwargs.get('owner_name', ''),
                                                    goods_name=kwargs.get('mix_kw', ''))
        p = max(int(kwargs.get('p', 1)), 1)
        page_size = APP_CONSTANTS['page_size']
        offset = (p - 1) * page_size
        # 举报的filter可有可无
        report_rule = kwargs.get('report_rule')
        if report_rule:
            query.filter(report_rule)
        # 排序规则必须有
        order_rule = kwargs.get('order_rule')
        goods_list = query.filter(search_rule).order_by(order_rule).offset(offset).limit(page_size).all()
        return goods_list

    return search_and_paginate


def goods_record_es_search(func):
    @wraps(func)
    def search_and_paginate(*args, **kwargs):
        query = func(*args, **kwargs)

        # 搜索栏
        search_bar_must = []
        owner_name = kwargs.get('owner_name')
        if owner_name:
            search_bar_must.append({"match": {"owner_name": owner_name}})
        goods_name = kwargs.get('mix_kw')
        if goods_name:
            search_bar_must.append({"match": {"name": goods_name}})
        os_location = kwargs.get('filter_address')
        if os_location:
            search_bar_must.append({"match": {"loc": os_location}})
        query['query']['bool']['must'].extend(search_bar_must)

        # 分页
        p = max(int(kwargs.get('p', 1)), 1)
        page_size = APP_CONSTANTS['page_size']
        offset = (p - 1) * page_size
        query['from'] = offset
        query['size'] = page_size
        # 搜索结果返回
        res = es.search(index=ES_CONSTANTS['INDEX'], body=query)
        goods_list = res['hits']['hits']
        return goods_list

    return search_and_paginate
