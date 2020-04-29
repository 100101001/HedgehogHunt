# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/4/29 下午9:34
@file: Appeal.py
@desc: 
"""
import datetime

from flask import request, g, jsonify

from application import db, queryToDict
from common.cahce.GoodsCasUtil import GoodsCasUtil
from common.libs import UserService, LogService
from common.libs.CryptService import Cipher
from common.libs.MemberService import MemberService
from common.libs.RecordService import RecordHandlers
from common.libs.UrlManager import UrlManager
from common.loggin.decorators import time_log
from common.models.ciwei.Appeal import Appeal
from common.models.ciwei.Goods import Good
from web.controllers.api import route_api


@route_api.route('/goods/appeal', methods=['GET', 'POST'])
@time_log
def goodsAppeal():
    resp = {'code': -1, 'msg': '', 'data': {}}
    req = request.values

    # 检查登陆
    # 检查参数物品id, 物品的发布者存在
    member_info = g.member_info
    if not member_info:
        resp['msg'] = '请先登录'
        return jsonify(resp)

    goods_id = int(req.get('id', -1))
    status = int(req.get('status', 0))
    if goods_id == -1 or status not in (3, 4):
        resp['msg'] = '申诉失败，请刷新后重试'
        return jsonify(resp)

    if not GoodsCasUtil.exec(goods_id, status, 5):
        resp['msg'] = '操作冲突，请稍后重试，如紧急可联系技术人员'
        return jsonify(resp)

    # 公开信息的状态操作加锁
    goods_info = Good.query.filter_by(id=goods_id, status=status).first()
    if goods_info is None:
        resp['msg'] = '申诉失败，请刷新后重试'
        return jsonify(resp)

    # 申诉事物
    MemberService.appealGoods(member_id=member_info.id, goods_id=goods_id)

    # 失物招领贴状态
    now = datetime.datetime.now()
    goods_info.status = 5
    goods_info.appeal_time = now
    db.session.add(goods_info)
    db.session.commit()
    resp['code'] = 200
    return jsonify(resp)


@route_api.route('/goods/appeal/search', methods=['GET', 'POST'])
@time_log
def goodsAppealRecordsSearch():
    resp = {'code': -1, 'msg': '', 'data': {}}
    req = request.values
    appeal_goods = RecordHandlers.get('goods').search().deal(7,
                                                             status=int(req.get('status', -1)),
                                                             p=int(req.get('p', 1)),
                                                             order_rule=Appeal.id.desc())
    appeals = []
    for item in appeal_goods:
        tmp_data = queryToDict(item.Appeal)
        goods = item.Good
        tmp_data['stuff'] = {
            'name': goods.name,
            'owner_name': goods.owner_name,
            'mobile': goods.mobile,
            'loc': goods.location.split("###")[1],
            'summary': goods.summary,
            'pics': [UrlManager.buildImageUrl(i) for i in goods.pics.split(',')]
        }
        tmp_data['contact'] = {
            'appealing': {  # 申诉者id和联络方式
                'member_id': item[-2].id,
                'nickname': item[-2].nickname,
                'avatar': item[-2].avatar,
                'mobile': Cipher.decrypt(item[-2].mobile)
            },
            'appealed': {
                'member_id': item[-1].id,
                'nickname': item[-1].nickname,
                'avatar': item[-3].avatar,
                'mobile': Cipher.decrypt(item[-1].mobile)
            }
        }
        appeals.append(tmp_data)
    resp['data']['list'] = appeals
    resp['code'] = 200
    return resp


@route_api.route('/appeal/set/status')
def goodsAppealStatusSet():
    resp = {'code': -1, 'msg': '操作失败', 'data': {}}
    req = request.values
    member_info = g.member_info
    if not member_info:
        resp['msg'] = '请先登录'
        return resp
    appeal_id = int(req.get('id', -1))
    status = int(req.get('status', -1))
    if appeal_id == -1 or status not in (1, 7):
        return resp

    user = UserService.getUserByMid(member_info.id)
    if not user or user.level > 1:
        resp['msg'] = '您没资格进行此项操作'
        return resp

    if status == 1:
        Appeal.query.filter_by(id=appeal_id, status=0).update(
            {'result': req.get('result'), 'status': 1, 'user_id': user.uid}, synchronize_session=False)
    else:
        # 管理员删除
        Appeal.query.filter_by(id=appeal_id, status=1).update({'deleted_by': user.uid}, synchronize_session=False)

    db.session.commit()
    resp['code'] = 200
    return resp


@route_api.route('/member/blocked/appeal', methods=['POST', 'GET'])
@time_log
def memberBlockedAppeal():
    """
    用户针对某条管理员拉黑自己的记录进行申诉
    :return:
    """
    resp = {'code': -1, 'msg': '', 'data': {}}
    req = request.values
    log_id = req.get('id', 0)
    reason = req.get('reason', '')
    if not log_id or not reason:
        resp['msg'] = '申诉失败'
        return resp
    MemberService.appealStatusChangeRecord(log_id=log_id, reason=reason)
    db.session.commit()
    resp['code'] = 200
    return resp


@route_api.route('/member/block/appeal/reject', methods=['POST', 'GET'])
@time_log
def memberBlockAppealTurnDown():
    """
    管理员驳回用户的封号申诉
    :return:
    """
    resp = {'code': -1, 'msg': '', 'data': {}}
    req = request.values

    member_info = g.member_info
    if not member_info:
        resp['msg'] = '请先登录'
        return resp
        # 将用户的status改为1
    log_id = int(req.get('id', 0))
    if not log_id:
        resp['msg'] = '操作失败'
        return resp

    user = UserService.getUserByMid(member_id=member_info.id)
    if not user:
        resp['msg'] = "您不是管理员，操作失败"
        return resp

    LogService.turnDownBlockAppeal(log_id=log_id)
    db.session.commit()
    resp['code'] = 200
    return resp


@route_api.route('/member/block/appeal/accept', methods=['POST', 'GET'])
@time_log
def memberBlockAppealAccept():
    """
    管理员同意用户的封号申诉
    :return:
    """
    resp = {'code': -1, 'msg': '', 'data': {}}
    req = request.values

    member_info = g.member_info
    if not member_info:
        resp['msg'] = '请先登录'
        return resp
        # 将用户的status改为1
    log_id = int(req.get('id', 0))
    if not log_id:
        resp['msg'] = '操作失败'
        return resp

    user = UserService.getUserByMid(member_id=member_info.id)
    if not user:
        resp['msg'] = "您不是管理员，操作失败"
        return resp
    op_res, op_msg = LogService.acceptBlockAppeal(log_id=log_id, user=user)
    db.session.commit()
    resp['code'] = 200 if op_res else -1
    resp['msg'] = op_msg
    return resp
