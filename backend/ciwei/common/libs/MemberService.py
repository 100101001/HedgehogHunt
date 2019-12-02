#!/usr/bin/python3.6.8
#Editor weichaoxu

# -*- coding:utf-8 -*-


#使用hash以及base64来对密码进行加密
import hashlib,base64
import random,string
from application import app,db
import requests,json
from common.libs.Helper import getCurrentDate
from common.models.ciwei.Member import Member
from common.models.ciwei.Goods import Good

class MemberService():

    @staticmethod
    def geneAuthCode(member_info=None):
        m=hashlib.md5()
        str="%s-%s"%(member_info.id,member_info.salt)
        m.update(str.encode('utf-8'))
        return m.hexdigest

    #生成秘钥
    @staticmethod
    def geneSalt(length=16):
        keylist=[random.choice((string.ascii_letters+string.digits)) for i in range(length)]
        return ("".join(keylist))

    @staticmethod
    def getWeChatOpenId(code):
        appid = app.config['OPENCS_APP']['appid']
        appkey = app.config['OPENCS_APP']['appkey']
        url = 'https://api.weixin.qq.com/sns/jscode2session?appid={0}&secret={1}&' \
              'js_code={2}&grant_type=authorization_code'.format(appid, appkey, code)

        r = requests.get(url)
        res = json.loads(r.text)

        openid=None
        if 'openid' in res:
            openid = res['openid']
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

        select_member_info.updated_time=getCurrentDate()
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
