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
from common.cahce import redis_conn_db_1
from common.libs.Helper import getCurrentDate
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
    def updateCredits(member_info):
        # 发布成功，用户积分涨5
        member_info.credits += 5
        member_info.updated_time = getCurrentDate()
        db.session.add(member_info)
        db.session.commit()
        return True

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
            return
        repeat_mark = Mark.query.filter_by(member_id=member_id, goods_id=goods_id).first()
        mark_key = 'mark_' + str(goods_id)
        if repeat_mark:
            if repeat_mark.status == 7:
                # 将被删除的记录状态初始化
                redis_conn_db_1.sadd(mark_key, member_id)
                redis_conn_db_1.expire(mark_key, 3600)
                repeat_mark.status = 0
                db.session.add(repeat_mark)
            return repeat_mark.status == 0
        redis_conn_db_1.sadd(mark_key, member_id)
        redis_conn_db_1.expire(mark_key, 3600)
        pre_mark = Mark()
        pre_mark.goods_id = goods_id
        pre_mark.member_id = member_id
        db.session.add(pre_mark)
        return True

    @staticmethod
    def cancelPreMarkGoods(member_id=0, goods_id=0):
        """
        对预认领的帖子，取消预先认领
        :param member_id:
        :param goods_id:
        :return:
        """
        if not member_id or not goods_id:
            return
        all_mark_query = Mark.query.filter(Mark.goods_id == goods_id, Mark.status != 7)
        all_marks = all_mark_query.all()
        pre_mark = all_mark_query.filter_by(member_id=member_id).first()
        if pre_mark and pre_mark.status == 0:
            # 前端会控制只对予认领的显示取消认领，这里判断status==0只是以防万一
            pre_mark.status = 7
            db.session.add(pre_mark)
            # 表示最后一个预认领的人取消了，帖子状态需要变成待认领
            return len(all_marks) == 1
        # 这种情况基本不会发生（一个予认领贴一定会有有效的认领记录），只是以防万一
        return len(all_marks) == 0

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
        mark_key = "mark_" + str(goods_id)
        mark_member_ids = redis_conn_db_1.smembers(mark_key)
        if not mark_member_ids:
            # 从数据库获取一个物品的所有认领人的id
            marks = Mark.query.filter(Mark.goods_id == goods_id,
                                      Mark.status != 7).all()
            if marks:
                mark_member_ids = set(i.member_id for i in marks)
                for m_id in mark_member_ids:
                    redis_conn_db_1.sadd(mark_key, m_id)
            else:
                # 用不存在的用户ID做集合占位符
                redis_conn_db_1.sadd(mark_key, -1)
        redis_conn_db_1.expire(mark_key, 3600)
        return bool(str(member_id) in mark_member_ids)

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
