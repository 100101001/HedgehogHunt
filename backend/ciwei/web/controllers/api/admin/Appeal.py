# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/4/29 下午9:34
@file: Appeal.py
@desc: 
"""

from flask import request, g

from application import db, APP_CONSTANTS
from common.admin.AppealService import AppealHandlers
from common.libs.CryptService import Cipher
from common.libs.Helper import queryToDict
from common.libs.UrlManager import UrlManager
from common.loggin.time import time_log
from common.models.ciwei.Appeal import Appeal
from common.models.ciwei.logs.change.MemberStatusChangeLog import MemberStatusChangeLog
from web.controllers.api import route_api


@route_api.route('/goods/appeal', methods=['GET', 'POST'])
@time_log
def goodsAppealCreate():
    """
    用户发起申诉
    :return:
    """
    resp = {'code': -1, 'msg': '', 'data': {}}
    req = request.values

    # 检查登陆
    # 检查参数物品id, 物品的发布者存在
    member_info = g.member_info
    if not member_info:
        resp['msg'] = '请先登录'
        return resp

    goods_id = int(req.get('id', -1))
    status = int(req.get('status', 0))
    if goods_id == -1 or status not in (3, 4):
        resp['msg'] = '申诉失败，请刷新后重试'
        return resp

    # 申诉事物
    op_res, op_msg = AppealHandlers.get('goods').deal('init', member_id=member_info.id,
                                     goods_id=goods_id, status=status)
    db.session.commit()
    resp['code'] = 200 if op_res else -1
    resp['msg'] = op_msg
    return resp


@route_api.route('/goods/appeal/search', methods=['GET', 'POST'])
@time_log
def goodsAppealsSearch():
    """
    管理员获取申诉记录
    :return:
    """
    resp = {'code': -1, 'msg': '', 'data': {}}
    req = request.values
    appeal_goods = AppealHandlers.get('goods').deal('search',
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
    resp['data'] = {
        'list': appeals,
        'has_more': len(appeals) >= APP_CONSTANTS['page_size']
    }
    resp['code'] = 200
    return resp


@route_api.route('/goods/appeal/dealt')
def goodsAppealDealt():
    """
    管理员处理申诉
    :return:
    """
    resp = {'code': -1, 'msg': '操作失败', 'data': {}}
    req = request.values
    member_info = g.member_info
    if not member_info:
        resp['msg'] = '请先登录'
        return resp
    appeal_id = int(req.get('id', -1))
    op_res, op_msg = AppealHandlers.get('goods').deal('dealt',
                                                      # 管理员
                                                      member_id=member_info.id, level=1,
                                                      # 申诉信息
                                                      appeal_id=appeal_id, result=req.get('result'))
    db.session.commit()
    resp['code'] = 200 if op_res else -1
    resp['msg'] = op_msg
    return resp


@route_api.route('/goods/appeal/delete')
def goodsAppealDelete():
    resp = {'code': -1, 'msg': '操作失败', 'data': {}}
    req = request.values
    member_info = g.member_info
    if not member_info:
        resp['msg'] = '请先登录'
        return resp
    appeal_id = int(req.get('id', -1))
    op_res, op_msg = AppealHandlers.get('goods').deal('delete',
                                                      # 管理员
                                                      member_id=member_info.id, level=1,
                                                      # 申诉信息
                                                      appeal_id=appeal_id)
    db.session.commit()
    resp['code'] = 200 if op_res else -1
    resp['msg'] = op_msg
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
    log_id = req.get('id')
    reason = req.get('reason')
    if not log_id or not reason:
        resp['msg'] = '申诉失败'
        return resp
    AppealHandlers.get('block').deal('init',
                                     log_id=log_id, reason=reason)
    db.session.commit()
    resp['code'] = 200
    return resp


@route_api.route('/member/blocked/record')
@time_log
def memberBlockedRecords():
    """
    用户获取管理员操作自己用户状态的记录，以便进行申诉
    管理员查看封锁记录以便进行驳回，接受
    :return:
    """
    resp = {'code': -1, 'msg': '', 'data': {'list': []}}
    req = request.values
    member_id = int(req.get('id', 0))
    if not member_id:
        resp['msg'] = '获取失败'
        return resp
    stuff_type = int(req.get('stuff_type', 0))
    if stuff_type not in APP_CONSTANTS['stuff_type'].values():
        resp['msg'] = '获取失败'
        return resp

    logs = AppealHandlers.get('block').deal('search',
                                            member_id=member_id,
                                            stuff_type=stuff_type,
                                            p=int(req.get('p')),
                                            order_rule=MemberStatusChangeLog.id.desc())

    def detailTransformer(stuff_typo=0):
        if stuff_typo == APP_CONSTANTS['stuff_type']['goods']:
            def transform(good):
                return {
                    'summary': good.summary,
                    'pics': [UrlManager.buildImageUrl(pic) for pic in good.pics.split(',')],
                    'name': good.name,
                    'loc': good.location.split('###')[1],
                    'owner_name': good.owner_name,
                    'mobile': good.mobile
                }

            return transform
        else:
            def transform(thank):
                return {
                    'thanked_mid': thank.target_member_id,
                    'summary': thank.summary,
                    'reward': str(thank.thank_price)
                }

            return transform

    transformer = detailTransformer(stuff_type)
    data_list = []
    for item in logs:
        tmp = queryToDict(item.MemberStatusChangeLog)
        tmp['stuff'] = transformer(item[1])  # 可以用 item.Good, item.Thank。为了统一用下标
        data_list.append(tmp)
    resp['data'] = {
        'list': data_list,
        'has_more': len(data_list) >= APP_CONSTANTS['page_size']
    }
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

    op_res, op_msg = AppealHandlers.get('block').deal('reject', log_id=log_id,
                                                      # 管理员权限
                                                      member_id=member_info.id)
    db.session.commit()
    resp['code'] = 200 if op_res else -1
    resp['msg'] = op_msg
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

    op_res, op_msg = AppealHandlers.get('block').deal('accept', log_id=log_id,
                                                      member_id=member_info.id)
    db.session.commit()
    resp['code'] = 200 if op_res else -1
    resp['msg'] = op_msg
    return resp


@route_api.route('/member/restore')
@time_log
def memberRestore():
    """
    恢复用户
    :return: 成功
    """
    resp = {'code': -1, 'msg': '', 'data': {}}
    req = request.values

    member_info = g.member_info
    if not member_info:
        resp['msg'] = '请先登录'
        return resp
    # 将用户的status改为1
    restore_id = int(req.get('id', 0))
    if not restore_id:
        resp['msg'] = '操作失败'
        return resp

    op_res, op_msg = AppealHandlers.get('block').deal('restore',
                                     member_id=member_info.id,
                                     restore_member_id=restore_id)

    resp['code'] = 200 if op_res else -1
    resp['msg'] = op_msg
    return resp
