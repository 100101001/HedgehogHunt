#!/usr/bin/python3.6.8
#Editor weichaoxu

# -*- coding:utf-8 -*-

from flask import g
from flask import render_template
import datetime
import uuid
from application import db
from common.models.ciwei.Member import Member

def iPagination( params ):
    import math

    ret = {
        "is_prev":1,
        "is_next":1,
        "from" :0 ,
        "end":0,
        "current":0,
        "total_pages":0,
        "page_size" : 0,
        "total" : 0,
        "url":params['url']
    }

    total = int( params['total'] )
    page_size = int( params['page_size'] )
    page = int( params['page'] )
    display = int( params['display'] )
    total_pages = int( math.ceil( total / page_size ) )
    total_pages = total_pages if total_pages > 0 else 1
    if page <= 1:
        ret['is_prev'] = 0

    if page >= total_pages:
        ret['is_next'] = 0

    semi = int( math.ceil( display / 2 ) )

    if page - semi > 0 :
        ret['from'] = page - semi
    else:
        ret['from'] = 1

    if page + semi <= total_pages :
        ret['end'] = page + semi
    else:
        ret['end'] = total_pages

    ret['current'] = page
    ret['total_pages'] = total_pages
    ret['page_size'] = page_size
    ret['total'] = total
    ret['range'] = range( ret['from'],ret['end'] + 1 )
    return ret

'''
统一渲染方法，用于包装一次渲染模板的方法，以实现传输g变量的功能
如果某个方法需要写很多次，那说不定就是可以用再次包装的方式来进行统一部署，以实现一次编写
'''
def ops_render(template,context={}):
    if 'current_user' in g:
        context['current_user']=g.current_user

    return render_template(template,**context)

'''
统一的获取时间方法
'''
def getCurrentDate(format="%Y-%m-%d %H:%M:%S"):
    return datetime.datetime.now().strftime(format)


'''
根据某个字段获取一个dict值出来
'''
def getDictFilterField(db_model,select_field,key_field,id_list):
    ret={}
    query=db_model.query
    if id_list and len(id_list)>0:
        #filter_by只能做简单的查询，filter才可以做复杂的查询功能
        query=query.filter(select_field.in_(id_list))

    list=query.all()
    if not list:
        return ret
    for item in list:
        if not hasattr(item,key_field):
            break
        ret[getattr(item,key_field)]=item
    return ret

def selectFilterObj(obj,field):
    ret=[]
    new_obj=[]
    for item in obj:
        if not hasattr(item,field):
            continue
        if getattr(item,field) in ret:
            continue

        ret.append(getattr(item, field))
        # if field=='member_id':
        #     member_info=Member.query.filter_by(id=item.member_id).first()
        #     if not member_info:
        #         continue
        #     else:
        #         ret.append(getattr(item,field))
        #         new_obj.append(item)
        # else:
        #     ret.append(getattr(item, field))
        #     new_obj.append(item)

    return ret

def getUuid():
    #uuid基本可以保证唯一性
    #根据设备硬件生成32位的随机字符串
    #uuid4可能会重复，所以使用uuid5
    now = datetime.datetime.now()
    uuid_now=str(uuid.uuid5(uuid.NAMESPACE_DNS,now.strftime("%Y%m%d%H%M%S"))).replace("-","")
    return uuid_now
