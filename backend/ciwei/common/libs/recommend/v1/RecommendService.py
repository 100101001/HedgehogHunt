# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/4/28 下午7:48
@file: RecommendService.py
@desc:
"""

from typing import List

from sqlalchemy import and_

from application import db, app, APP_CONSTANTS
from common.consts import FOUND
from common.libs.Helper import queryToDict
from common.libs.recommend.v1.DistanceService import DistanceService
from common.libs.recommend.v1.SynonymsService import SynonymsService
from common.models.ciwei.Goods import Good
from common.models.ciwei.Recommend import Recommend
from common.models.proxy.GoodProxy import GoodProxy
from common.tasks.subscribe import SubscribeTasks


class RecommendHandler:
    synonyms = SynonymsService()
    distance = DistanceService()

    @classmethod
    def filter(cls, **kwargs):
        next_handler = ReleaseHandler
        next_filter = getattr(next_handler, 'filter', None)
        if next_filter:
            next_filter(**kwargs)

    @classmethod
    def _doAutoRecommendGoods(cls, goods_info=None, edit=False):
        """
        自动匹配推荐

        :param edit:
        :param goods_info: 已经序列化过，反序列化的goods，不用担心commit影响
        """
        app.logger.info("推荐中： 物品ID {0}, 编辑推荐 {1}".format(goods_info.id, edit))

        release_type = goods_info.business_type
        goods_list = cls.__doFilterPossibleGoods(goods_info=goods_info)
        # 记录需要发送订阅消息的lost_goods
        # 新增推荐记录
        need_notification = set()
        for good in goods_list:
            good_id = good.id
            target_member_id = good.member_id if release_type == 1 else goods_info.member_id  # 获得寻物启示贴主id
            lost_goods_id = good_id if release_type == 1 else goods_info.id  # 如果发布的是失物招领，lost_id就是匹配上的物品列表的id
            found_goods_id = good_id if release_type == 0 else goods_info.id  # 如果发布的是寻物启事，found_id就是匹配上的物品列表的id
            new_recommend = cls.__addRecommendGoods(target_member_id=target_member_id,
                                                    found_goods_id=found_goods_id,
                                                    lost_goods_id=lost_goods_id,
                                                    rel_score=1,
                                                    edit=edit)

            if new_recommend and release_type == FOUND:
                # 如果发布了失物招领，需要给新匹配上的寻物启示发匹配成功通知
                need_notification.add(good.openid)
        db.session.commit()
        app.logger.info("推荐结束：物品ID {0}, 编辑推荐 {1}".format(goods_info.id, edit))
        if need_notification:
            # 有需要发送消息的，异步批量的发送订阅消息
            app.logger.info("发送订阅消息")
            SubscribeTasks.send_recommend_subscribe_in_batch.delay(lost_list=need_notification,
                                                                   found_goods=goods_info.__dict__ if isinstance(
                                                                       goods_info, GoodProxy) else queryToDict(
                                                                       goods_info))

    @classmethod
    def __addRecommendGoods(cls, target_member_id=0, found_goods_id=0, lost_goods_id=0, rel_score=1, edit=False):
        """
        增加新的记录，进行防重

        :param rel_score:
        :param edit: 是否是编辑后的推荐
        :param target_member_id: 推送的会员对象
        :param found_goods_id: 捡到的物品
        :param lost_goods_id: 只是用于记录一下（在查看推荐记录时好看一下，匹配的动因）
        :return: 是否新增推荐，用于给用户发送订阅消息
        """
        if not target_member_id or not found_goods_id:
            return False
        app.logger.info("本轮推荐结果： 拾物{0} 匹配上 失物{1}".format(found_goods_id, lost_goods_id))
        # 可能会匹配上不同的，这里就只给一个用户匹配上一个拾物，取最接近的失物ID记录
        repeat_found_recommends = Recommend.getExistFoundRecommend(found_id=found_goods_id, member_id=target_member_id)
        # 单独记录推荐对
        repeat_recommend = Recommend.filterSamePair(lost_id=lost_goods_id, same_found=repeat_found_recommends)
        # 有但修改了
        if repeat_recommend and edit:
            repeat_recommend.status = 0
            repeat_recommend.rel_score = rel_score
            db.session.add(repeat_recommend)
        # 没有
        elif not repeat_recommend:
            model_recommend = Recommend()
            model_recommend.found_goods_id = found_goods_id
            model_recommend.target_member_id = target_member_id
            model_recommend.lost_goods_id = lost_goods_id
            model_recommend.rel_score = rel_score
            db.session.add(model_recommend)
        # 是新的拾物推荐
        return len(repeat_found_recommends) == 0

    @classmethod
    def __doFilterPossibleGoods(cls, goods_info=None) -> List[Good]:
        """
        直接在MySQL中搜索，使用名词同义词进行搜索

        :param goods_info:
        :return:
        """
        possible_keywords = cls.synonyms.getSearchWords(goods_info.name)
        possibles = []
        # 遍历同义词列表，进行数据库匹配
        for kw in possible_keywords.get('noun', goods_info.name):
            possibles.append(Good.query.filter(and_(Good.name.like("%{}%".format(kw)),
                                                    Good.business_type == 1 - goods_info.business_type),
                                               # 未被举报的，且状态是待
                                               Good.report_status == 0,
                                               Good.status == 1))

        # 近距离筛选
        if goods_info.os_location != APP_CONSTANTS['default_lost_loc']:
            possibles = cls.distance.filterNearbyGoods(goods_list=possibles, location=goods_info.os_location)
        return possibles


class NoModifiedHandler:
    next = None

    @classmethod
    def filter(cls, edit_info=None, goods_info=None, **kwargs):
        if edit_info and edit_info.get('modified'):
            # 更新以下推荐未读即可
            Recommend.renewOldRecommend(goods_info)
            db.session.commit()
        next_handler = cls.next
        if next_handler:
            next_handler.filter(edit_info=edit_info, goods_info=goods_info, **kwargs)


class ModifiedHandler(RecommendHandler):
    next = NoModifiedHandler

    @classmethod
    def filter(cls, edit_info=None, goods_info=None, **kwargs):
        if edit_info and edit_info.get('need_recommend'):
            Recommend.invalidatePrevRecommend(goods_info)
            super()._doAutoRecommendGoods(goods_info=goods_info, edit=True)
            return
        next_handler = cls.next
        if next_handler:
            next_handler.filter(edit_info=edit_info, goods_info=goods_info, **kwargs)


class ReleaseHandler(RecommendHandler):
    next = ModifiedHandler

    @classmethod
    def filter(cls, edit_info=None, goods_info=None, **kwargs):
        if not edit_info:
            super()._doAutoRecommendGoods(goods_info=goods_info, edit=False)
            return
        next_handler = cls.next
        if next_handler:
            next_handler.filter(edit_info=edit_info, goods_info=goods_info, **kwargs)
