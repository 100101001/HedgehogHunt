# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/4/28 下午7:48
@file: RecommendService.py
@desc: 
"""
import json

from application import db, app, APP_CONSTANTS, es
from common.cahce.core import redis_conn_lost, redis_conn_found
from common.libs.Helper import queryToDict

from common.libs.recommend.v2.DistanceService import DistanceService
from common.libs.recommend.v2.SynonymsService import SynonymsService
from common.models.ciwei.Recommend import Recommend
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
        goods_list = cls.__doFilterPossibleGoods(goods_info)
        # 记录需要发送订阅消息的lost_goods
        # 新增推荐记录
        need_notification = []
        for good in goods_list:
            good_id = good.get('id')
            target_member_id = good.get('member_id') if release_type == 1 else goods_info.member_id  # 获得寻物启示贴主id
            lost_goods_id = good_id if release_type == 1 else goods_info.id  # 如果发布的是失物招领，lost_id就是匹配上的物品列表的id
            found_goods_id = good_id if release_type == 0 else goods_info.id  # 如果发布的是寻物启事，found_id就是匹配上的物品列表的id
            new_recommend = cls.__addRecommendGoods(target_member_id=target_member_id,
                                                    found_goods_id=found_goods_id,
                                                    lost_goods_id=lost_goods_id,
                                                    rel_score=good.get('score', 1),
                                                    edit=edit)

            if new_recommend and release_type == 1:
                # 如果发布了失物招领，需要给新匹配上的寻物启示发匹配成功通知
                need_notification.append(good)
        db.session.commit()
        app.logger.info("推荐结束：物品ID {0}, 编辑推荐 {1}".format(goods_info.id, edit))
        if need_notification:
            # 有需要发送消息的，异步批量的发送订阅消息
            app.logger.info("发送订阅消息")
            SubscribeTasks.send_recommend_subscribe_in_batch.delay(lost_list=need_notification,
                                                                   found_goods=queryToDict(goods_info))

    @classmethod
    def __addRecommendGoods(cls, target_member_id=0, found_goods_id=0, lost_goods_id=0, rel_score=1, edit=False):
        """
        增加新的记录，进行防重
        归还和通知会加进推荐
        :param rel_score:
        :param edit:
        :param target_member_id:
        :param found_goods_id:
        :param lost_goods_id: 只是用于记录一下（在查看推荐记录时好看一下，匹配的动因）
        :return:是否是新的推荐
        """
        if not target_member_id or not found_goods_id:
            return False
        app.logger.info("本轮推荐结果： 拾物{0} 匹配上 失物{1}".format(found_goods_id, lost_goods_id))
        # 可能会有同一个拾物匹配上了不同的失物
        repeat_recommend = Recommend.query.filter_by(found_goods_id=found_goods_id,
                                                     target_member_id=target_member_id).first()
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
        # 是新的推荐
        return repeat_recommend is None

    @classmethod
    def __doFilterPossibleGoods(cls, goods_info=None):
        name = goods_info.name
        cls_dict = cls.synonyms.getWordClasses(name)
        if not cls_dict['noun']:
            app.logger.info("es document match")
            return cls.__doFilterPossibleGoods_ES(goods_info)
        else:
            app.logger.info("redis k-v match")
            return cls.__doFilterPossibleGoods_Redis(goods_info, cls_dict)

    @classmethod
    def __doFilterPossibleGoods_Redis(cls, goods_info=None, cls_dict=None):
        release_type = goods_info.business_type
        # 物品范围
        redis_conn = redis_conn_lost if release_type else redis_conn_found

        noun_keys = cls_dict['noun']
        noun_sets = set()
        for k in noun_keys:
            app.logger.warn(k)
            possible = redis_conn.hvals(k)  # ["{id, lng, lat, author_id}", "{}"]
            noun_sets = noun_sets.union(possible)

        author_id = goods_info.member_id
        possibles = []
        for item in noun_sets:
            data = json.loads(item)
            if data['member_id'] == author_id:
                continue
            data['score'] = 1
            possibles.append(data)

        if goods_info.os_location != APP_CONSTANTS['default_lost_loc']:  # 发布了寻物启事，且不记得东西丢哪了，就不筛了
            possibles = cls.distance.filterNearbyGoods(goods_list=possibles, found_location=goods_info.os_location)

        # 如果有权重，则计算加权分数
        adj_keys = cls_dict['adj']
        if adj_keys:
            part = len(adj_keys)
            total_score = part / 2 * (part + 1) + 1  # 只有1个形容词
            relatives = {}
            for k in adj_keys:
                relative = redis_conn.hvals(k)  # ["{id, lng, lat, author_id}", "{}"]
                rel_score = part / total_score
                for i in range(len(relative)):
                    data = json.loads(relative[i])
                    goods_id = data['id']
                    if goods_id not in relatives:
                        relatives[goods_id] = rel_score
                    else:
                        relatives[goods_id] += rel_score
                part -= 1

            for item in possibles:
                item['score'] += relatives.get(item['id'], 0)

        return possibles

    @classmethod
    def __doFilterPossibleGoods_ES(cls, goods_info=None):
        """
        当没有同义词的时候，选择ES做类似MYSQL上进行的检索
        :param goods_info:
        :return:
        """
        key_words = cls.synonyms.getSearchWords(input_word=goods_info.name)
        must_syms = key_words['noun']
        should_syms = key_words['adj']

        should = []
        for kw in should_syms:
            should.append({'match': {'name': kw}})

        must = [{'match_phrase': {'name': ''}},  # 会循环填充
                {'match': {'business_type': 1 - goods_info.business_type}},  # 互相匹配
                {'match': {'status': 1}}]  # 只配待认领和待寻回的：看会员操作情况，如果乱认领的很多那么就改成 1~2
        must_not = {'match': {'member_id': goods_info.member_id}}  # 不配自己发布的
        # 布尔查询
        body = {
            'query': {
                'bool': {
                    'must': must,
                    'must_not': must_not,
                    'should': should
                }
            }
        }

        possibles = []
        for noun in must_syms:  # must_syms中只有名词自己
            must[0]['match_phrase']['name'] = noun
            res = es.search(index=app.config['ES']['INDEX'], body=body)
            for item in res['hits']['hits']:
                data = item['_source']
                data['score'] = item['_score']
                possibles.append(data)

        if goods_info.os_location != APP_CONSTANTS['default_lost_loc']:
            possibles = cls.distance.filterNearbyGoods(goods_list=possibles, found_location=goods_info.os_location)
        return possibles


class NoModifiedHandler:
    next = None

    @classmethod
    def filter(cls, edit_info=None, goods_info=None, **kwargs):
        if edit_info and edit_info.get('modified'):
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
