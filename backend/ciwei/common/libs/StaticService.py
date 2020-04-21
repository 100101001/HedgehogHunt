# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/4/21 上午2:20
@file: StaticService.py
@desc: 
"""
from sqlalchemy import func

from application import es, db
from common.libs.recommend.v2.SyncService import ES_CONSTANTS
from common.models.ciwei.Feedback import Feedback
from common.models.ciwei.Goods import Good
from common.models.ciwei.Member import Member
from common.models.ciwei.Recommend import Recommend
from common.models.ciwei.Report import Report
from common.models.ciwei.Thanks import Thank
from common.models.ciwei.mall.Order import Order


def getGoodsStatics():
    good_type_static = {
        "aggs": {
            "group_by": {"terms": {"field": "business_type"}}
        },
        "size": 0
    }
    res = es.search(index=ES_CONSTANTS['INDEX'], body=good_type_static)
    buckets = {item['key']: item['doc_count'] for item in res['aggregations']['group_by']['buckets']}
    find_num = buckets.get(1, 0)
    lost_num = buckets.get(0, 0)
    return_num = buckets.get(2, 0)
    total_num = find_num + lost_num + return_num
    scan_return_query = {
        "query": {
            "bool": {
                "must": [{"match": {"business_type": 2}}],
                "must_not": [{"match": {"return_goods_id": 0}}]
            }
        },
        "size": 0
    }
    res = es.search(index=ES_CONSTANTS['INDEX'], body=scan_return_query)
    scan_return_num = res['hits']['total']['value']
    lost_return_num = return_num - scan_return_num
    return total_num, find_num, lost_num, lost_return_num, scan_return_num


def getGotBackStatics():
    gotback_query = {
        "query": {
            "bool": {
                "should": [{"match": {"business_type": 1}}, {"match": {"business_type": 2}},
                           {"match": {"status": 1}}, {"match": {"status": 2}}],
                "minimum_should_match": 2
            }
        },
        "size": 0
    }
    res = es.search(index=ES_CONSTANTS['INDEX'], body=gotback_query)
    return res['hits']['total']['value']


def getThankStatics():
    return db.session.query(func.count(Thank.id)).scalar()


def getViewStatics():
    return db.session.query(func.sum(Good.view_count)).scalar()


def getRecommendStatics():
    total_recommend = db.session.query(func.count(Recommend.id)).filter(Recommend.status != 7).scalar()
    hit_recommend = db.session.query(func.count(Recommend.id)).filter(Recommend.found_goods_id == Good.id,
                                                                      Recommend.target_member_id == Good.owner_id).scalar()
    return total_recommend, hit_recommend


def getReportAndFeedbackStatics():
    report_num = db.session.query(func.count(Report.id)).scalar()
    feedback_num = db.session.query(func.count(Feedback.id)).scalar()
    return report_num, feedback_num


def getMemberStatics():
    block_member_number = db.session.query(func.count(Member.id)).filter(Member.status == 0).scalar()
    member_number = db.session.query(func.count(Member.id)).scalar()
    return member_number, block_member_number


def getSalesIncomeStatics():
    income = db.session.query(func.sum(Order.total_price)).filter(Order.status.in_([-7, -5, -6, 1])).scalar()
    return income if income else 0
