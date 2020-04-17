# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/4/14 下午4:45
@file: ESTasks.py
@desc: 将mysql的数据同步到es中去
"""
from application import celery, es, APP_CONSTANTS, app, cache


# tmp_data = {
#     "id": item.id,
#     "goods_name": item.name,
#     "owner_name": item.owner_name,
#     "updated_time": str(item.updated_time),
#     "business_type": item.business_type,
#     "summary": item.summary,
#     "main_image": UrlManager.buildImageUrl(item.main_image),
#     "auther_name": item.nickname,
#     "avatar": item.avatar,
#     "selected": False,
#     "status_desc": str(item.status_desc),  # 静态属性，返回状态码对应的文字
#     "top": item.top_expire_time > now
# }

# tmp_data = {
#     "id": item.id,  # 供前端用户点击查看详情用的
#     "new": 1 if op_status != 2 else (
#         0 if only_new else goods_id_recommend_status_map.get(item.id, 1)),
#     # 不存在时置不是new记录
#     "goods_name": item.name,
#     "owner_name": item.owner_name,
#     "updated_time": str(item.updated_time),
#     "business_type": item.business_type,
#     "summary": item.summary,
#     "main_image": UrlManager.buildImageUrl(item.main_image),
#     "auther_name": item.nickname,
#     "avatar": item.avatar,
#     "unselectable": item.status == 5 or (item.status != 2 and status == 0 and op_status == 1),  # 前端编辑禁止选中
#     "selected": False,  # 供前端选中删除记录用的属性
#     "status_desc": str(item.status_desc),  # 静态属性，返回状态码对应的文字
#     "top": item.top_expire_time > now,  # 是否为置顶记录
#     "location": item.location.split("###")[1] if op_status == 0 or op_status == 5 else ""  # 归还贴和发布贴概要可看地址
# }
# data_goods_list.append(tmp_data)


@celery.task(name='sync.es.on_update_goods_info')
def on_update_goods_info(goods_info=None):
    business_type = goods_info.get('business_type')
    goods_id = goods_info.get('id')
    es.update(index='goods_search', doc_type=business_type, id=goods_id, body=getGoodsInfoBody(body_type='search', goods_info=goods_info))
    es.update(index='goods_recommend', doc_type=business_type, id=goods_id, body=getGoodsInfoBody(body_type='recommend', goods_info=goods_info))


# @celery.task(name='sync.es.on_insert_goods_info')
# def on_insert_goods_info(goods_info=None):
#     """
#     为了搜索和匹配推荐插入ES
#     :param goods_info:
#     :return:
#     """
#     if not goods_info:
#         return "NO INFO TO INSERT"
#     business_type = goods_info.get('business_type')
#     goods_id = goods_info.get('id')
#     res1 = es.create(index='goods_search', doc_type=business_type, id=goods_id, body=getGoodsInfoBody(body_type='search', goods_info=goods_info))
#     app.logger.info("搜索数据插入: " + str(res1))
#     res2 = es.create(index='goods_recommend', doc_type=business_type, id=goods_id, body=getGoodsInfoBody(body_type='recommend', goods_info=goods_info))
#     app.logger.info("推荐数据插入: " + str(res2))
#     return "INSERT SUCCESS"


@celery.task(name='sync.es.on_insert_goods_info')
def on_insert_goods_info(goods_info=None):
    """
    为了搜索和匹配推荐插入ES
    :param goods_info:
    :return:
    """
    if not goods_info:
        return "NO INFO TO INSERT"
    business_type = goods_info.get('business_type')
    goods_id = goods_info.get('id')
    # 通用数据
    body_common = {
        'id': goods_id,
        'goods_name': goods_info.get('name'),
        'owner_name': goods_info.get('owner_name'),
        'business_type': business_type,
        'summary': goods_info.get('summary'),
        'status': goods_info.get('status'),
    }
    # 搜索数据
    body_search = {
        'updated_time': goods_info.get('updated_time').strftime(APP_CONSTANTS['time_format_long']),
        'main_image': goods_info.get('main_image'),
        'auther_name': goods_info.get('nickname'),
        'avatar': goods_info.get('avatar'),
        'top_expire': goods_info.get('top_expire_time'),
        'location': goods_info.get('location')  # 放置地点
    }.update(body_common)
    res1 = es.create(index='goods_info', doc_type='search', id=goods_id, body=body_search)
    app.logger.info("搜索数据插入: " + str(res1))
    return "INSERT SUCCESS"


def getGoodsInfoBody(body_type='recommend', goods_info=None):
    """

    :param body_type:
    :param goods_info:
    :return:
    """
    @cache.memoize(timeout=60)
    def getCommonBody(common_goods_info=None):
        return {
            'id': common_goods_info.get('id'),
            'goods_name': common_goods_info.get('name'),
            'owner_name': common_goods_info.get('owner_name'),
            'business_type': common_goods_info.get('business_type'),
            'summary': common_goods_info.get('summary'),
            'status': common_goods_info.get('status'),
        }

    def getSearchBody():
        return {
            'updated_time': goods_info.get('updated_time').strftime(APP_CONSTANTS['time_format_long']),
            'main_image': goods_info.get('main_image'),
            'auther_name': goods_info.get('nickname'),
            'avatar': goods_info.get('avatar'),
            'top_expire': goods_info.get('top_expire_time'),
            'location': goods_info.get('location')  # 放置地点
        }

    def getRecommendBody():
        return {
            'auther_id': goods_info.get('member_id'),  # 作者ID, 用于筛选不是自己和自己配对上
            'os_location': goods_info.get('os_location')  # 实际捡拾和丢失地点, 用于距离筛选
        }

    if body_type == 'recommend':
        return getCommonBody(goods_info).update(getRecommendBody())
    elif body_type == 'search':
        return getCommonBody(goods_info).update(getSearchBody())

