# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/4/28 上午2:09
@file: time.py
@desc: 
"""
from functools import wraps

from application import APP_CONSTANTS, es
from common.libs import RecordService
from common.sync.core.base.EsService import ES_CONSTANTS


def db_search(out_num=1, query_index=0):
    def search(func):
        @wraps(func)
        def search_and_paginate(*args, **kwargs):

            out = func(*args, **kwargs)
            if out_num == 1:
                query = out
            else:
                query = out[query_index]

            # 搜索条件可有可无，目前支持物品和答谢记录搜索
            search_rule = RecordService.searchBarFilter(owner_name=kwargs.get('owner_name'),
                                                        goods_name=kwargs.get('mix_kw'),
                                                        record_type=int(kwargs.get('record_type', 1)))
            p = max(int(kwargs.get('p', 1)), 1)
            page_size = APP_CONSTANTS['page_size']
            offset = (p - 1) * page_size
            # 举报的filter可有可无
            report_rule = kwargs.get('report_rule')
            if report_rule is not None:
                query.filter(report_rule)
            # 排序规则必须有
            order_rule = kwargs.get('order_rule')
            model_list = query.filter(search_rule).order_by(order_rule).offset(offset).limit(page_size).all()

            if out_num == 1:
                return model_list
            else:
                return (model_list, *out[1:])

        return search_and_paginate

    return search


def es_search(func):
    @wraps(func)
    def search_and_paginate(*args, **kwargs):
        query = func(*args, **kwargs)

        # 搜索栏
        search_bar_must = []
        owner_name = kwargs.get('owner_name')
        if owner_name:
            search_bar_must.append({"match": {"owner_name": owner_name}})
        goods_name = kwargs.get('goods_name')
        if goods_name:
            search_bar_must.append({"match": {"name": {"query": goods_name, "minimum_should_match": "90%", "boost": 5}}})
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
