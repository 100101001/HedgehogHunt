# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2019/12/10 下午9:06
@file: Goods.py
@desc:
"""
import datetime

from flask import request, jsonify, g

from application import db, APP_CONSTANTS
from common.cahce.GoodsCasUtil import GoodsCasUtil
from common.libs.GoodsService import GoodsHandlers
from common.libs.Helper import param_getter
from common.libs.RecordService import RecordHandlers
from common.libs.UploadService import UploadService
from common.libs.UrlManager import UrlManager
from common.loggin.time import time_log
from common.models.ciwei.Goods import Good
from web.controllers.api import route_api

TOP_PRICE = APP_CONSTANTS['sp_product']['top']['price']


@route_api.route("/goods/top/order", methods=['POST', 'GET'])
@time_log
def topOrder():
    resp = {'code': -1, 'msg': '服务繁忙，请稍后重试', 'data': {}}
    req = request.values
    member_info = g.member_info
    if not member_info:
        resp['msg'] = "请先登录"
        return resp
    pay_sign_data = GoodsHandlers.get('lost').deal('init_top_pay', consumer=member_info,
                                                   price=req.get('price', TOP_PRICE), top_charge=TOP_PRICE)
    if not pay_sign_data:
        return resp
    resp['data'] = pay_sign_data
    resp['code'] = 200
    return resp


@route_api.route('/goods/top/order/notify', methods=['GET', 'POST'])
@time_log
def topOrderCallback():
    xml_data, header = GoodsHandlers.get('lost').deal('finish_top_pay', callback_body=request.data)
    return xml_data, header


@route_api.route("/goods/create", methods=['GET', 'POST'])
@time_log
def goodsCreate():
    """
    预发帖
    :return: 图片->是否在服务器上 , 前端再次上传真正需要上传的图片
    """
    resp = {'code': -1, 'msg': '', 'data': {}}
    # 检查登陆
    # 检查参数: goods_name, business_type
    req = request.values
    member_info = g.member_info
    if not member_info:
        resp['msg'] = "请先登录"
        return resp
    business_type = int(req.get('business_type', -1))
    if business_type not in (0, 1, 2):
        resp['msg'] = "发布失败"
        return resp
    model_goods = GoodsHandlers.get('release').deal('init', biz_typo=business_type, author_info=member_info,
                                                    release_info=req, is_scan_return='owner_name' not in req)

    resp['code'] = 200
    resp['data']['id'] = model_goods.id
    db.session.commit()
    img_list_status = UploadService.filterUpImages(req['img_list'])  # 图片列表发布时已判空
    resp['data']['img_list_status'] = img_list_status
    return resp


@route_api.route("/goods/edit", methods=['GET', 'POST'])
@time_log
def goodsEdit():
    """
    更新物品信息
    :return: 物品id,图片名->是否在服务器上
    """
    resp = {'code': -1, 'msg': '数据上传失败', 'data': {}}
    req = request.values

    # 检查登陆 检查参数
    member_info = g.member_info
    if not member_info:
        resp['msg'] = '请先登录'
        return resp
    goods_id, status = int(req.get('id', -1)), int(req.get('status', -1))
    if goods_id == -1 or status == -1:
        return resp
    op_res, op_out = GoodsHandlers.get('release').deal('init_edit', biz_typo=-1, status=status, goods_id=goods_id,
                                                       edit_info=req)
    if not op_res:
        resp['msg'] = op_out
        return resp

    # 通过链接发送之后的图片是逗号连起来的字符串
    resp['data'] = {
        'id': goods_id,
        'img_list_status': op_out
    }
    resp['code'] = 200
    return resp


@route_api.route("/goods/add-pics", methods=['GET', 'POST'])
@time_log
def goodsAddPics():
    """
    上传物品图片到服务器
    :return: 成功
    """
    resp = {'code': -1, 'msg': '图片上传失败', 'state': 'add pics success'}
    # 检查参数 检查已登陆
    req = request.values
    member_info = g.member_info
    if not member_info:
        resp['msg'] = '请先登录'
        return resp
    goods_id, image = int(req.get('id', -1)), request.files.get('file', None)
    if goods_id == -1 or not image:
        return resp
    goods_info = Good.query.filter_by(id=goods_id).with_for_update().first()
    if not goods_info:
        return resp
    # 保存文件到 /web/static/upload/日期 目录下 db 新增images
    upload_res = UploadService.uploadByFile(image)
    if upload_res['code'] != 200:
        return resp
    # 在id号物品的 pics 字段加入图片本地路径
    goods_info.addImage(pic=upload_res['data']['file_key'])
    db.session.commit()
    resp['code'] = 200
    return resp


@route_api.route("/goods/update-pics", methods=['GET', 'POST'])
@time_log
def goodsUpdatePics():
    """
    更新物品图片
    :return: 成功
    """
    resp = {'code': -1, 'msg': '上传数据失败'}
    req = request.values

    # 检查登陆
    # 检查参数：物品id,图片url
    member_info = g.member_info
    if not member_info:
        resp['msg'] = '请先登录'
        return jsonify(resp)
    goods_id, img_url = int(req.get('id', -1)), req.get('img_url')
    if goods_id == -1 or not img_url:
        return resp
    goods_info = Good.query.filter_by(id=goods_id).with_for_update().first()
    if not goods_info:
        return resp

    # 在id号物品的pics中加入去掉前缀 /web/static/upload的图片url
    pic_url = UploadService.getImageUrl(img_url)
    goods_info.addImage(pic=pic_url)
    db.session.commit()
    resp['code'] = 200
    return jsonify(resp)


@route_api.route("/goods/end-create", methods=['GET', 'POST'])
@time_log
def goodsEndCreate():
    """
    结束创建
    :return:
    """
    resp = {'code': -1, 'msg': '创建失败，稍后重试'}

    # 检查登陆
    # 检查参数：物品id
    req = request.values
    member_info = g.member_info
    if not member_info:
        resp['msg'] = '请先登录'
        return resp
    goods_id = int(req.get('id', -1))
    if goods_id == -1:
        return resp
    init_goods = Good.query.filter_by(id=goods_id).first()
    if not init_goods:
        return resp
    # 区分编辑和非编辑
    is_edit = int(req.get('edit', 0))
    biz_typo = -1 if is_edit else init_goods.business_type  # 编辑是公共handler处理
    op = 'finish_edit' if is_edit else 'created'  # 编辑的策略不同
    edit_info = {  # 编辑需要额外的推荐信息是否被修改的数据
        'need_recommend': int(req.get('keyword_modified', 0)),  # 原来推荐作废需要再次推荐
        'modified': int(req.get('modified', 0))  # 原来的推荐需要更新为未读推荐
    } if is_edit else None
    GoodsHandlers.get('release').deal(op, biz_typo=biz_typo, goods_info=init_goods, edit_info=edit_info,
                                      lost_id=int(req.get('target_goods_id', -1)), notify_id=req.get('notify_id', ''))
    resp['code'] = 200
    return resp


@route_api.route('/goods/status', methods=['GET', 'POST'])
@time_log
def goodsStatusCheck():
    """
    检查前端的视图的物品状态是否是正确的
    :return:
    """
    resp = {'code': -1, 'msg': '', 'data': {}}
    req = request.values
    goods_id, status = int(req.get('id', -1)), int(req.get('status', -1))
    if goods_id == -1 or status == -1:
        resp['msg'] = '操作失败，稍后重试'
        return resp

    if not GoodsCasUtil.exec(goods_id, status, status):
        # 已经进入详情页面了
        resp['msg'] = '操作冲突，请稍后重试'
        return resp

    resp['code'] = 200
    return resp


@route_api.route("/goods/search", methods=['GET', 'POST'])
@time_log
def goodsSearch():
    resp = {'code': -1, 'msg': '', 'data': {}}
    req = request.values
    business_type = int(req.get('business_type', -1))
    if business_type not in (0, 1):
        resp['msg'] = "获取失败"
        return jsonify(resp)
    status = int(req.get('status', -1))
    if status not in (0, 1, 2, 3, 4):
        resp['msg'] = '获取失败'
        return resp

    p = int(req.get('p', 1))
    goods_list = RecordHandlers.get('goods').search().deal(op_status=-1,
                                                           status=status,
                                                           biz_type=business_type,
                                                           owner_name=req.get('owner_name'),
                                                           goods_name=req.get('mix_kw'),
                                                           filter_address=req.get('filter_address'),
                                                           p=p)

    def status_desc(goods_status):
        if goods_status < 0:
            return '已删除'
        if business_type == 1:
            status_mapping = {
                '1': '待认领',
                '2': '预认领',
                '3': '已认领',
                '4': '已答谢',
                '5': '申诉中',
            }
        elif business_type == 0:
            status_mapping = {
                '1': '待寻回',
                '2': '预寻回',
                '3': '已寻回',
                '4': '已答谢'
            }
        else:  # 归还贴子
            status_mapping = {
                '0': '已拒绝',
                '1': '待确认',
                '2': '待取回',
                '3': '已取回',
                '4': '已答谢'
            }
        return status_mapping[str(goods_status)]

    data_goods_list = []
    if goods_list:
        # 所有发布者 id -> Member
        now = datetime.datetime.now()
        for item in goods_list:
            # 只返回符合用户期待的状态的物品
            # score = item.get('_score')
            item = item.get('_source')
            item_id = item.get('id')
            item_status = item.get('status')
            if not GoodsCasUtil.exec_wrap(item_id, [item_status, 'nil'], item_status):
                continue
            from application import app
            try:
                top_time = datetime.datetime.strptime(item.get('top_expire_time').split('.')[0].replace('T', ' '),
                                                      "%Y-%m-%d %H:%M:%S")
                tmp_data = {
                    "id": item_id,
                    "goods_name": item.get('name'),
                    "owner_name": item.get('owner_name'),
                    "updated_time": item.get('updated_time').replace('T', ' '),
                    "business_type": item.get('business_type'),
                    "summary": item.get('summary'),
                    "main_image": UrlManager.buildImageUrl(item.get('main_image')),
                    "auther_id": item.get('member_id'),
                    "auther_name": item.get('nickname'),
                    "avatar": item.get('avatar'),
                    "selected": False,
                    "status": int(item.get('status')),
                    "status_desc": status_desc(item.get('status')),  # 静态属性，返回状态码对应的文字
                    "top": top_time > now,
                    # "score": score,
                    # "top_expire": item.get('top_expire_time')
                }
                data_goods_list.append(tmp_data)
            except Exception:
                app.logger.error(item)

    # 失/拾 一页信息 是否已加载到底
    resp['code'] = 200
    resp['data']['list'] = data_goods_list
    resp['data']['has_more'] = len(goods_list) >= APP_CONSTANTS['page_size'] and p < APP_CONSTANTS[
        'max_pages_allowed']  # 由于深度分页的性能问题，限制页数(鼓励使用更好的搜索条件获取较少的数据量)
    return resp


@route_api.route('/goods/info')
@time_log
def goodsInfo():
    """
    查看详情,读者分为以下类别,对应不同操作
    1.进来认领
    2.进来编辑
    3.推荐来看
    :return:物品详情,是否显示地址
    """
    resp = {'code': -1, 'msg': '', 'data': {}}
    req = request.values

    # 检查参数：物品id,物品的发布者存在
    goods_id = int(req.get('id', -1))
    if goods_id == -1:
        resp['msg'] = '帖子不存在'
        return resp
    goods_info = Good.query.filter_by(id=goods_id).first()
    if not goods_info or goods_info.status < 0:
        resp['msg'] = '作者已删除'
        return resp
    if not GoodsCasUtil.exec_wrap(goods_id, [goods_info.status, 'nil'], goods_info.status):
        resp['msg'] = '操作冲突，请稍后重试'
        return resp
    if goods_info.report_status != 0:
        resp['msg'] = '帖子遭举报，已冻结待管理员处理。若无违规将解冻，否则将被系统自动屏蔽。'
        return resp
    # 浏览量
    handler = GoodsHandlers.get('info')(goods_info=goods_info, member_info=g.member_info,
                                        has_read=int(req.get('read', 1)))
    handler.deal('read')
    handler.deal('checked', is_recommend_src=int(req.get('op_status', 0)) == 2)
    # 获取数据
    info = handler.deal('info')
    db.session.commit()
    resp['code'] = 200
    resp['data'] = {
        'info': info,
        'show_location': info['show_location']
    }
    return resp


@route_api.route('/goods/pure/info', methods=['GET', 'POST'])
@time_log
def goodsInfoForThanks():
    """
    答谢时用于获取寻物链接的归还帖子数据
    :return:
    """
    resp = {'code': -1, 'msg': '', 'data': {}}
    req = request.values

    # 检查参数：物品id,物品的发布者存在
    goods_id = int(req.get('id', -1))
    if goods_id == -1:
        resp['msg'] = '答谢失败'
        return resp
    goods_info = Good.query.filter_by(id=goods_id, status=3).first()
    if not goods_info:
        resp['msg'] = '答谢失败'
        return resp
    goods_status = goods_info.status
    if not GoodsCasUtil.exec_wrap(goods_id, ['nil', goods_status], goods_status):
        # 虽然数据库还没更新，但内存的原子操作已经更新了 WR
        resp['msg'] = '操作冲突，请稍后重试'
        return resp
    resp['data']['info'] = {
        # 物品帖子数据信息
        "id": goods_info.id,
        "business_type": goods_info.business_type,  # 寻物启示 or 失物招领
        "goods_name": goods_info.name,  # 物品名
        "owner_name": goods_info.owner_name,  # 物主名
        "auther_id": goods_info.member_id,
        "auther_name": goods_info.nickname,
        "avatar": goods_info.avatar,
        "updated_time": str(goods_info.updated_time),  # 被编辑的时间 or 首次发布的时间
    }
    resp['code'] = 200
    return resp


@route_api.route('/goods/apply')
@time_log
def goodsApply():
    """
    申请认领，涉及物品状态变化
    :return: 物品的状态, 是否可以显示地址
    """
    resp = {'code': -1, 'msg': '', 'data': {}}
    req = request.values
    # 检查登陆 检查参数
    member_info = g.member_info
    if not member_info:
        resp['msg'] = '请先登录'
        return jsonify(resp)
    goods_id = int(req.get('id', -1))
    status = int(req.get('status', 0))
    if goods_id == -1 or status not in (1, 2):
        resp['msg'] = '认领失败'
        return jsonify(resp)
    op_res, op_msg = GoodsHandlers.get('found').deal('pre_mark', goods_id=goods_id, status=status,
                                                     member_id=member_info.id)
    resp['code'] = 200 if op_res else -1
    resp['msg'] = op_msg
    return resp


@route_api.route('/goods/cancel/apply')
@time_log
def goodsCancelApplyInBatch():
    """
    CAS
    取消认领，（如果涉及更改原物品的状态，对该操作加锁，并加入对原状态的预期）
    :return: 物品的状态, 是否可以显示地址
    """
    resp = {'code': -1, 'msg': '', 'data': {}}
    req = request.values
    # 检查登陆 检查参数
    member_info = g.member_info
    if not member_info:
        resp['msg'] = '请先登录'
        return resp
    found_ids = param_getter['ids'](req.get('ids', None))
    status = int(req.get('status', 0))
    if found_ids is None or status not in (2, 3, 4):
        resp['msg'] = '操作失败'
        return resp
    # 取消认领
    GoodsHandlers.get('found').deal('mistaken', goods_ids=found_ids, status=status, member_id=member_info.id)
    resp['code'] = 200
    return resp


@route_api.route('/goods/gotback')
@time_log
def goodsGotbackInBatch():
    """
    拿回失物
    :return:
    """
    resp = {'code': -1, 'msg': '', 'data': {}}
    req = request.values
    # 检查登陆 检查参数
    member_info = g.member_info
    if not member_info:
        resp['msg'] = '请先登录'
        return resp
    goods_ids = param_getter['ids'](req.get('ids', None))
    status = int(req.get('status', -1))
    if goods_ids is None or status != 2:
        resp['msg'] = '确认失败'
        return resp
    op_res, op_msg = GoodsHandlers.get('found').deal('gotback', goods_ids=goods_ids, status=status,
                                                     member_id=member_info.id)
    resp['code'] = 200 if op_res else -1
    resp['msg'] = op_msg
    return resp


@route_api.route('/goods/found/to/sys', methods=['GET', 'POST'])
@time_log
def goodsUnmarkToSysInBatch():
    """
    待认领的物品送给系统，默默地将符合状态的更新
    :return:
    """
    resp = {'code': -1, 'msg': '', 'data': {}}
    req = request.values
    goods_ids = param_getter['ids'](req.get('ids', None))
    status = int(req.get('status', -1))
    if goods_ids is None or status != 1:
        resp['msg'] = '操作失败'
        return resp
    GoodsHandlers.get('found').deal('to_sys', goods_ids=goods_ids, status=status)
    resp['code'] = 200
    return resp


@route_api.route('/goods/return/cancel')
@time_log
def returnGoodsDelInBatch():
    """
    归还者批量删除，待确认的归还贴
    :return:
    """
    resp = {'code': -1, 'msg': '', 'data': {}}
    req = request.values
    return_ids = param_getter['ids'](req.get('ids', None))
    status = int(req.get('status', -1))
    if return_ids is None or status != 1:
        resp['msg'] = '取消失败'
        return jsonify(resp)

    op_res, op_msg = GoodsHandlers.get('return').deal('cancel', status=status, return_ids=return_ids)
    resp['code'] = 200 if op_res else -1
    resp['msg'] = op_msg
    return jsonify(resp)


@route_api.route('/goods/return/to/found', methods=['GET', 'POST'])
@time_log
def returnGoodsToFoundInBatch():
    """
    CAS【lock】
    待确认的归还贴
    已拒绝的归还贴
    :return:
    """
    resp = {'code': -1, 'msg': '', 'data': {}}
    req = request.values

    return_ids = param_getter['ids'](req.get('id', None))
    status = int(req.get('status', -1))
    if return_ids is None or status not in (0, 1):
        resp['msg'] = "操作失败"
        return jsonify(resp)

    op_res, op_msg = GoodsHandlers.get('return').deal('open', status=status, return_ids=return_ids)
    resp['code'] = 200 if op_res else -1
    resp['msg'] = op_msg
    return jsonify(resp)


@route_api.route('/goods/return/reject')
@time_log
def returnGoodsRejectInBatch():
    """
    批量否认待确认的归还
    :return:
    """
    resp = {'code': -1, 'msg': '', 'data': {}}
    req = request.values
    return_ids = param_getter['ids'](req.get('ids', None))
    status = int(req.get('status', -1))
    if return_ids is None or status != 1:
        resp['msg'] = "操作失败"
        return jsonify(resp)

    # 检查登陆
    member_info = g.member_info
    if not member_info:
        resp['msg'] = "请先登录"
        return jsonify(resp)

    op_res, op_msg = GoodsHandlers.get('return').deal('reject', status=status, return_ids=return_ids)
    resp['code'] = 200 if op_res else -1
    resp['msg'] = op_msg
    return jsonify(resp)


@route_api.route('/goods/return/confirm')
@time_log
def returnGoodsConfirm():
    """
    确认必须进入查看
    进入归还贴，确认归还的是自己的
    :return:
    """
    resp = {'code': -1, 'msg': '', 'data': {}}
    req = request.values
    goods_id = int(req.get('id', -1))
    status = int(req.get('status', -1))
    if goods_id == -1 or status != 1:
        resp['msg'] = "操作失败"
        return resp
    member_info = g.member_info
    if not member_info:
        # 检查登陆
        resp['msg'] = "请先登录"
        return resp
    op_res, op_msg = GoodsHandlers.get('return').deal('confirm', return_id=goods_id, status=status,
                                                      confirmer_id=member_info.id)
    resp['code'] = 200 if op_res else -1
    resp['msg'] = op_msg
    return jsonify(resp)


@route_api.route('/goods/return/gotback', methods=['GET', 'POST'])
@time_log
def returnGoodsGotbackInBatch():
    """
    寻物启示状态只有作者能操作了
    归还帖状态也只有被归还者能操作
    在待取回的归还贴上操作biz_type==2
    在待取回的寻物贴上操作biz_type==2
    :return:
    """
    resp = {'code': -1, 'msg': '', 'data': {}}
    req = request.values

    # 检查登陆
    # 检查参数物品id, 物品的发布者存在
    member_info = g.member_info
    if not member_info:
        resp['msg'] = '请先登录'
        return jsonify(resp)
    goods_ids = param_getter['ids'](req.get('ids', None))
    business_type = int(req.get('biz_type', -1))
    status = int(req.get('status', -1))
    if goods_ids is None or business_type not in (0, 2) or status != 2:  # 2代表从归还贴/通知批量确认，0代表从寻物贴/详情批量确认
        resp['msg'] = '操作失败'
        return resp

    op_res, op_msg = GoodsHandlers.get('return').deal('gotback', goods_ids=goods_ids, member_id=member_info.id,
                                                      status=status, biz_type=business_type)
    resp['code'] = 200 if op_res else -1
    resp['msg'] = op_msg
    return resp


@route_api.route('/goods/link/lost/del', methods=['GET'])
@time_log
def returnLinkLostDelInBatch():
    """
    删除已取回/已答谢的归还通知 智能删除自己发布的寻物贴
    :return:
    """
    resp = {'code': -1, 'msg': '', 'data': {}}
    req = request.values
    return_ids, status = param_getter['ids'](req.get('ids', None)), int(req.get('status', 0))
    if return_ids is None or status not in (3, 4):
        resp['msg'] = "智能清除失败，请手动删除"
        return resp
    GoodsHandlers.get('return').deal('del_link', return_ids=return_ids, status=status)
    resp['code'] = 200
    return resp


@route_api.route('/goods/link/return/del', methods=['GET'])
@time_log
def returnLinkReturnDelInBatch():
    """
    删除已取回/已答谢的寻物贴时智能删除归还通知
    :return:
    """
    resp = {'code': -1, 'msg': '', 'data': {}}
    req = request.values
    lost_ids = param_getter['ids'](req.get('ids', None))
    if lost_ids is None:
        resp['msg'] = "智能清除失败，请手动删除"
        return resp
    GoodsHandlers.get('return').deal('del_link', lost_ids=lost_ids)
    resp['code'] = 200
    return resp


@route_api.route('/es/init', methods=['GET', 'POST'])
def esInit():
    mappings = {
        "properties": {
            "appeal_time": {
                "type": "date"
            },
            "avatar": {
                "type": "keyword",
                "index": "false"
            },
            "business_type": {
                "type": "byte"
            },
            "confirm_time": {
                "type": "date"
            },
            "created_time": {
                "type": "date"
            },
            "finish_time": {
                "type": "date"
            },
            "id": {
                "type": "long"
            },
            "lat": {
                "type": "float",
                "index": "false"
            },
            "lng": {
                "type": "float",
                "index": "false"
            },
            "loc": {
                "type": "text"
            },
            "os_location": {
                "type": "text"
            },
            "location": {
                "type": "keyword",
                "index": "false"
            },
            "main_image": {
                "type": "keyword",
                "index": "false"
            },
            "member_id": {
                "type": "long"
            },
            "openid": {
                "type": "keyword"
            },
            "author_mobile": {
              "type": "keyword",
              "index": "false"
            },
            "mobile": {
                "type": "keyword",
                "index": "false"
            },
            "name": {
                "type": "text"
            },
            "nickname": {
                "type": "keyword",
                "index": "false"
            },
            "owner_name": {
                "type": "text"
            },
            "pics": {
                "type": "keyword",
                "index": "false"
            },
            "qr_code_openid": {
                "type": "keyword"
            },
            "report_status": {
                "type": "byte"
            },
            "return_goods_id": {
                "type": "long"
            },
            "return_goods_openid": {
                "type": "keyword"
            },
            "status": {
                "type": "byte"
            },
            "summary": {
                "type": "text"
            },
            "thank_time": {
                "type": "date"
            },
            "top_expire_time": {
                "type": "date"
            },
            "updated_time": {
                "type": "date"
            },
            "view_count": {
                "type": "integer"
            },
            "user_id": {
                "type": "integer"
            }
        }
    }
    body = {
        "settings": {
            "number_of_shards": 3,
            "number_of_replicas": 1
        },
        "mappings": mappings
    }
    from application import es, app
    res = es.indices.create(index=app.config['ES']['INDEX'], body=body)
    return res