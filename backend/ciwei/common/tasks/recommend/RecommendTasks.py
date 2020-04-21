# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/4/11 下午6:28
@file: RecommendTasks.py
@desc: 
"""

from sqlalchemy import or_

from application import celery, db, app, es
from common.libs.recommend.DistanceService import DistanceService
from common.libs.recommend.SynonymsService import SynonymsService
from common.models.ciwei.Goods import Good
from common.models.ciwei.Recommend import Recommend
from common.tasks.subscribe import SubscribeTasks

synonyms = SynonymsService()
distance = DistanceService()


@celery.task(name='recommend.test')
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


@celery.task(name='recommend.test2')
def send_mail(words):
    print(words)
    return "can i be used by other celery task?"


@celery.task(name='recommend.auto_recommend_goods', property=1, ignore_result=True)
def autoRecommendGoods(edit_info=None, goods_info=None):
    """
    根据编辑或者新帖子进行推荐匹配
    :param edit_info:
    :param goods_info:
    :return:
    """
    # 字典转成ORM模型
    info = Good()
    info.__dict__ = goods_info

    if edit_info is not None:
        # 编辑
        # 未被用户删除的推荐
        origin_recommends = Recommend.query.filter(Recommend.found_goods_id == goods_info.get('id'),
                                                   Recommend.status != 7)
        # 匹配的关键词是否被修改
        need_recommend = int(edit_info.get('need_recommend', 0))  # 编辑了核心信息
        if need_recommend:
            # 匹配关键字被修改了，可能有些不再匹配，等于帖子被作者删除了
            origin_recommends.update({'status': 7}, synchronize_session=False)
            db.session.commit()
            doAutoRecommendGoods(goods_info=info, edit=True)
        else:
            modified = int(edit_info.get('modified', 0))  # 编辑了非核心信息通知用户去看看
            if modified:
                # 可能是图片/描述/地址等非匹配关键被修改了，更新为未读匹配，但不会再对全局进行自动匹配
                origin_recommends.update({'status': 0}, synchronize_session=False)
                db.session.commit()
    else:
        # 发布
        doAutoRecommendGoods(goods_info=info, edit=False)


def doAutoRecommendGoods(goods_info=None, edit=False):
    """
    自动匹配推荐
    :param edit:
    :param goods_info:
    """
    app.logger.warn("推荐中")

    # 互相匹配（假设予认领的人没有恶意）
    release_type = goods_info.business_type
    if release_type not in (0, 1):
        return
    query = Good.query.filter_by(business_type=1 - release_type, status=1)
    # 筛选物品类别(没有就置-1没有)
    query = query.filter_by(category=goods_info.category)
    # 不能是同一个人发布的拾/失
    query = query.filter(Good.member_id != goods_info.member_id)

    # 拓展搜索词
    search_words = synonyms.getSearchWords(input_word=goods_info.name)
    app.logger.warn("推荐中")
    common_rule = or_(*[Good.name.like(name) for name in search_words])
    # 如果失主姓名是无还匹配，就会匹配上所有无的
    # 如果有失主姓名但是假设寻物启事比失物招领晚发，或者物品名稍有偏差，就匹配不上了
    # 匹配核心用户群：先发了寻物启示，后来了失物招领
    goods_owner_name = goods_info.owner_name
    if goods_owner_name != "无":
        rule = or_(Good.owner_name == goods_owner_name, common_rule)
        query = query.filter(rule)
    else:
        query = query.filter(common_rule)

    # 取用于地址筛查和ID和推荐用的member_id
    goods_list = query.with_entities(Good.id, Good.os_location, Good.member_id,
                                     # openid和recommend_times用于决定和发送订阅消息
                                     Good.openid, Good.recommended_times).all()
    # 筛选距离最近的
    goods_list = distance.filterNearbyGoods(goods_list=goods_list, found_location=goods_info.os_location)

    # 记录需要发送订阅消息的lost_goods
    # 新增推荐记录
    need_notification = []
    for good in goods_list:
        target_member_id = good.member_id if release_type == 1 else goods_info.member_id  # 获得寻物启示贴主id
        lost_goods_id = good.id if release_type == 1 else goods_info.id
        found_goods_id = good.id if release_type == 0 else goods_info.id  # 获取失物招领id
        new_recommend = addRecommendGoods(target_member_id=target_member_id,
                                          found_goods_id=found_goods_id,
                                          lost_goods_id=lost_goods_id,
                                          edit=edit)

        if new_recommend and release_type == 1 and good.recommended_times > 0:
            # 是之前没推荐过的新物品给了寻物启示失主，且该寻物启事还剩寻物消息才发通知
            # 通知：有人可能捡到了你遗失的东西
            need_notification.append(good)

    # 批量更新寻物剩余的匹配通知次数
    if release_type == 1:
        Good.query.filter(Good.business_type == 0, Good.id.in_([item.id for item in need_notification])). \
            update({'recommended_times': 0}, synchronize_session=False)
        db.session.commit()
    app.logger.warn("推荐结束")

    # 异步批量的发送订阅消息[分发给专门负责订阅消息的worker处理]
    # 注意消息经序列化后, need_notification列表中的good变成了纯粹的列表(属性按序排列)
    SubscribeTasks.send_recommend_subscribe_in_batch.delay(lost_list=need_notification, found_goods=goods_info)


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
        db.session.commit()
    # 没有
    elif not repeat_recommend:
        model_recommend = Recommend()
        model_recommend.found_goods_id = found_goods_id
        model_recommend.target_member_id = target_member_id
        model_recommend.lost_goods_id = lost_goods_id
        db.session.add(model_recommend)
        db.session.commit()
    # 是新的推荐
    return repeat_recommend is None
