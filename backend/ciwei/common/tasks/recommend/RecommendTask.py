# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/4/11 下午6:28
@file: RecommendTask.py
@desc: 
"""

from sqlalchemy import or_

from application import celery, db, app
from common.libs.recommend.DistanceService import DistanceService
from common.libs.recommend.SynonymsService import SynonymsService
from common.models.ciwei.Goods import Good
from common.models.ciwei.Recommend import Recommend

synonyms = SynonymsService()
distance = DistanceService()


@celery.task
def add_together(goods_info=None, abc=2):
    send_mail.delay("can i use another celery task")
    goods_id = goods_info.get('id')
    goods = Good.query.filter(Good.id == goods_id).first()
    goods.summary = "异步任务测试2"
    db.session.add(goods)
    db.session.commit()
    goods2 = Good.query.filter(Good.id == goods_id).first()
    goods3 = Good.query.filter(Good.id == goods_id + 1).first()
    goods4 = Good.query.filter(Good.id == goods_id + 2).first()
    return str(goods.id) + " , " + str(goods2.summary) + " , " + str(goods3.summary) + " , " + str(goods4.summary)


@celery.task()
def send_mail(words):
    print(words)
    return "can i be used by other celery task?"


@celery.task
def autoRecommendGoods(goods_id=0, edit_info=None, goods_info=None):
    """
    根据编辑或者新帖子进行推荐匹配
    :param edit_info:
    :param goods_id:
    :param goods_info:
    :return:
    """
    if edit_info is not None:
        # 编辑
        # 未被用户删除的推荐
        origin_recommends = Recommend.query.filter(Recommend.found_goods_id == goods_id,
                                                   Recommend.status != 7)
        # 匹配的关键词是否被修改
        need_recommend = int(edit_info.get('need_recommend', 0))  # 编辑了核心信息
        if need_recommend:
            # 匹配关键字被修改了，可能有些不再匹配，等于帖子被作者删除了
            origin_recommends.update({'status': 7}, synchronize_session=False)
            doAutoRecommendGoods(goods_info=goods_info, edit=True)
        else:
            modified = int(edit_info.get('modified', 0))  # 编辑了非核心信息通知用户去看看
            if modified:
                # 可能是图片/描述/地址等非匹配关键被修改了，更新为未读匹配，但不会再对全局进行自动匹配
                origin_recommends.update({'status': 0}, synchronize_session=False)
    else:
        # 发布
        doAutoRecommendGoods(goods_info=goods_info, edit=False)


def doAutoRecommendGoods(goods_info=None, edit=False):
    """
    自动匹配推荐
    :param edit:
    :param goods_info:
    """
    from common.libs import SubscribeService
    app.logger.warn("推荐中")

    # 互相匹配（假设予认领的人没有恶意）
    release_type = goods_info.get('business_type', -1)
    if release_type not in (0, 1):
        return
    query = Good.query.filter_by(business_type=1 - release_type, status=1)
    # 筛选物品类别(没有就置-1没有)
    query = query.filter_by(category=goods_info.get('category', -1))
    # 不能是同一个人发布的拾/失
    query = query.filter(Good.member_id != goods_info.get('member_id', 0))

    # 拓展搜索词
    search_words = synonyms.getSearchWords(input_word=goods_info.get('name', ''))
    app.logger.warn("推荐中")
    common_rule = or_(*[Good.name.like(name) for name in search_words])
    goods_owner_name = goods_info.get('owner_name')
    if goods_owner_name != "无":
        rule = or_(Good.owner_name == goods_info.owner_name, common_rule)
        query = query.filter(rule)
    else:
        query = query.filter(common_rule)

    # 取用于地址筛查和ID和推荐用的member_id
    goods_list = query.with_entities(Good.id, Good.os_location, Good.member_id).all()
    # 筛选距离最近的
    goods_list = distance.filterNearbyGoods(goods_list=goods_list, os_location=goods_info.get('os_location'))

    for good in goods_list:
        target_member_id = good.member_id if release_type == 1 else goods_info.get('member_id', 0)  # 获得寻物启示贴主id
        lost_goods_id = good.id if release_type == 1 else goods_info.get('id')
        found_goods_id = good.id if release_type == 0 else goods_info.get('id')  # 获取失物招领id
        new_recommend = addRecommendGoods(target_member_id=target_member_id,
                                          found_goods_id=found_goods_id,
                                          lost_goods_id=lost_goods_id,
                                          edit=edit)
        if new_recommend and release_type == 1:
            # 是之前没推荐过的新物品给了寻物启示失主，才发通知
            # 通知：有人可能捡到了你遗失的东西
            SubscribeService.send_recommend_subscribe(goods_info=good)
    app.logger.warn("推荐结束")


def addRecommendGoods(target_member_id=0, found_goods_id=0, lost_goods_id=0, edit=False):
    """
    增加新的记录，进行防重
    归还和通知会加进推荐
    :param edit:
    :param target_member_id:
    :param found_goods_id:
    :param lost_goods_id: 只是用于记录一下（在查看推荐记录时好看一下，匹配的动因）
    :return:
    """
    if not target_member_id or not found_goods_id:
        return False
    repeat_recommend = Recommend.query.filter_by(found_goods_id=found_goods_id,
                                                 target_member_id=target_member_id,
                                                 lost_goods_id=lost_goods_id).first()
    # 有但修改了
    if repeat_recommend and edit:
        repeat_recommend.status = 0
        db.session.add(repeat_recommend)
    # 没有
    model_recommend = Recommend()
    model_recommend.found_goods_id = found_goods_id
    model_recommend.target_member_id = target_member_id
    model_recommend.lost_goods_id = lost_goods_id
    db.session.add(model_recommend)
    db.session.commit()
    # 是新的推荐
    return repeat_recommend is None
