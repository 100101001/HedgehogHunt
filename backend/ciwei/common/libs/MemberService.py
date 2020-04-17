# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/3/10 下午11:03
@file: MemberService.py
@desc:
"""

import hashlib
import json
import random
import string

import requests

from application import app, db
from common.cahce import redis_conn_db_1, CacheKeyGetter, CacheOpService, CacheQueryService
from common.libs.Helper import getCurrentDate, queryToDict
from common.models.ciwei.Appeal import Appeal
from common.models.ciwei.Goods import Good
from common.models.ciwei.Mark import Mark
from common.models.ciwei.Member import Member
from common.models.ciwei.Recommend import Recommend


class MemberService:

    @staticmethod
    def geneAuthCode(member_info=None):
        m = hashlib.md5()
        str = "%s-%s" % (member_info.id, member_info.salt)
        m.update(str.encode('utf-8'))
        return m.hexdigest

    # 生成秘钥
    @staticmethod
    def geneSalt(length=16):
        keylist = [random.choice((string.ascii_letters + string.digits)) for _ in range(length)]
        return "".join(keylist)

    @staticmethod
    def getWeChatOpenId(code, get_session_key=False):
        appid = app.config['OPENCS_APP']['appid']
        appkey = app.config['OPENCS_APP']['appkey']
        url = 'https://api.weixin.qq.com/sns/jscode2session?appid={0}&secret={1}&' \
              'js_code={2}&grant_type=authorization_code'.format(appid, appkey, code)

        r = requests.get(url, headers={'Connection': 'close'})
        res = json.loads(r.text)

        openid = None
        session_key = None
        if 'openid' in res:
            openid = res['openid']
        if 'session_key' in res:
            session_key = res['session_key']

        if get_session_key:
            return openid, session_key
        else:
            return openid

    @staticmethod
    def updateCredits(member_id):
        # 发布成功，用户积分涨5
        member_info = Member.query.filter_by(id=member_id).first()
        member_info.credits += 5
        CacheOpService.setMemberCache(member_info=member_info)
        db.session.add(member_info)


    @staticmethod
    def blockMember(select_member_id):
        # 发布成功，用户积分涨5
        # 违规用户状态设置为0.则无法再正常使用
        select_member_info = Member.query.filter_by(id=select_member_id).first()
        select_member_info.status = 0

        # 该用户下正常的账户
        goods_list = Good.query.filter(Good.member_id == select_member_id, Good.status == 1).all()
        for item in goods_list:
            item.status = 8
            item.updated_time = getCurrentDate()
            db.session.add(item)
            db.session.commit()

        select_member_info.updated_time = getCurrentDate()
        db.session.add(select_member_info)
        db.session.commit()
        return True

    @staticmethod
    def restoreMember(select_member_id):
        # 违规用户状态设置为0.则无法再正常使用
        select_member_info = Member.query.filter_by(id=select_member_id).first()
        select_member_info.status = 1

        # 该用户下正常的账户
        goods_list = Good.query.filter(Good.member_id == select_member_id, Good.status == 8).all()
        for item in goods_list:
            item.status = 1
            item.updated_time = getCurrentDate()
            db.session.add(item)
            db.session.commit()

        select_member_info.updated_time = getCurrentDate()
        db.session.add(select_member_info)
        db.session.commit()

        return True

    @staticmethod
    def setRecommendStatus(member_id=0, goods_id=0, new_status=1, old_status=0):
        # 假设第一点，一个用户不会发出大于一条的类似帖子，如果发了
        # 假设第二点，用户知道自己正在找的东西，还删除了推荐记录，所以会将所有相关的都置无效（无论因为哪一条推给了用户）
        Recommend.query.filter_by(found_goods_id=goods_id, target_member_id=member_id, status=old_status). \
            update({'status': new_status}, synchronize_session=False)

    @staticmethod
    def preMarkGoods(member_id=0, goods_id=0):
        """
        预认领
        :param member_id:
        :param goods_id:
        :return:
        """
        if not member_id or not goods_id:
            return False
        repeat_mark = Mark.query.filter_by(member_id=member_id, goods_id=goods_id).first()
        if repeat_mark:
            if repeat_mark.status == 7:
                # 将被删除的记录状态初始化
                repeat_mark.status = 0
                db.session.add(repeat_mark)
            return repeat_mark.status == 0
        pre_mark = Mark()
        pre_mark.goods_id = goods_id
        pre_mark.member_id = member_id
        db.session.add(pre_mark)
        return True

    @staticmethod
    def hasMarkGoods(member_id=0, goods_id=0):
        """
        是否预认领/认领了该物品(详情可否见放置地址)
        :param member_id:
        :param goods_id:
        :return:
        """
        if not member_id or not goods_id:
            return False
        # 缓存中获取goods_id 对应的 member_id 集合
        mark_member_ids = CacheQueryService.getMarkCache(goods_id=goods_id)
        if not mark_member_ids:
            # 缓存不命中, 从数据库获取一个物品的所有认领人的id
            marks = Mark.query.filter(Mark.goods_id == goods_id,
                                      Mark.status != 7).all()
            mark_member_ids = CacheOpService.setMarkCache(goods_id=goods_id, marks=marks)
        return bool(str(member_id) in mark_member_ids)

    @staticmethod
    def cancelPremark(found_ids=None, member_id=0):
        """
        :param found_ids:
        :param member_id:
        :return: 外面修改Goods状态还要用的mark_key
        """
        Mark.query.filter(Mark.member_id == member_id,
                          Mark.goods_id.in_(found_ids),
                          Mark.status == 0).update({'status': 7}, synchronize_session=False)

    @staticmethod
    def appealGoods(member_id=0, goods_id=0):
        """
        新的待处理Appeal
        :param member_id:
        :param goods_id:
        :return:
        """
        if not member_id or not goods_id:
            return False
        appeal = Appeal.query.filter_by(member_id=member_id, goods_id=goods_id).first()
        if appeal is None:
            appeal = Appeal()
            appeal.member_id = member_id
            appeal.goods_id = goods_id
        else:
            appeal.status = 0
        db.session.add(appeal)
