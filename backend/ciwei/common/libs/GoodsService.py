# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/4/17 下午5:08
@file: GoodsService.py
@desc: 
"""
import datetime

from sqlalchemy import func

from application import db, APP_CONSTANTS
from common.cahce import CacheQueryService, CacheOpService
from common.cahce.GoodsCasUtil import GoodsCasUtil
from common.libs.Helper import queryToDict
from common.libs.MemberService import MemberService
from common.libs.UploadService import UploadService
from common.libs.UrlManager import UrlManager
from common.models.ciwei.Goods import Good
from common.models.ciwei.Mark import Mark
from common.tasks.recommend.v2 import RecommendTasks
from common.tasks.sms import SmsTasks
from common.tasks.subscribe import SubscribeTasks


def releaseLost(author_info=None, release_info=None):
    """
    发布寻物启事
    :param author_info:
    :param release_info:
    :return:
    """
    model_goods = Good()
    # 作者信息
    model_goods.member_id = author_info.id
    model_goods.openid = author_info.openid  # 作者的身份标识，冗余设计，方便订阅消息等
    model_goods.nickname = author_info.nickname
    model_goods.avatar = author_info.avatar

    # 物品信息
    model_goods.name = release_info.get("goods_name", '')  # 物品名，前端发布已判空
    model_goods.location = release_info.get("location", '').replace(',', '###')  # 住址，前端发布已判空
    os_location = release_info.get('os_location', '')  # 丢失地址，不记得会留空
    model_goods.os_location = os_location.replace(',', '###') if os_location else APP_CONSTANTS['default_lost_loc']
    model_goods.owner_name = release_info.get('owner_name', '无')

    model_goods.summary = release_info.get('summary', '无')
    model_goods.business_type = 0
    model_goods.mobile = release_info.get('mobile', '无')
    # 寻物置顶
    now = datetime.datetime.now()
    model_goods.top_expire_time = now if not int(release_info.get('is_top', 0)) else \
        now + datetime.timedelta(days=int(release_info['days']))
    db.session.add(model_goods)
    db.session.flush()
    return model_goods


def releaseFound(author_info=None, release_info=None):
    """
    发布失物招领
    :param author_info:
    :param release_info:
    :return:
    """
    model_goods = Good()
    # 作者信息
    model_goods.member_id = author_info.id
    model_goods.openid = author_info.openid  # 作者的身份标识，冗余设计，方便订阅消息等
    model_goods.nickname = author_info.nickname
    model_goods.avatar = author_info.avatar
    model_goods.name = release_info["goods_name"]  # 物品名，前端发布已判空
    # 物品信息
    model_goods.os_location = release_info.get("os_location", '').replace(',', '###')  # 发现位置
    location = release_info.get('location', '')  # 放置位置
    model_goods.location = location.replace(',', '###') if location else model_goods.os_location  # 如果放置位置留空说明和发现位置一样
    model_goods.owner_name = release_info.get('owner_name', '无')

    model_goods.summary = release_info.get('summary', '无')
    model_goods.business_type = 1
    model_goods.mobile = release_info.get('mobile', '无')
    db.session.add(model_goods)
    db.session.flush()
    return model_goods


def releaseReturn(author_info=None, release_info=None, is_scan_return=False):
    """
    发布归还贴，寻物归还和扫码归还
    :param author_info:
    :param release_info:
    :param is_scan_return:
    :return:
    """
    model_goods = Good()
    # 作者信息
    model_goods.member_id = author_info.id
    model_goods.openid = author_info.openid  # 作者的身份标识，冗余设计，方便订阅消息等
    model_goods.nickname = author_info.nickname
    model_goods.avatar = author_info.avatar
    model_goods.name = release_info["goods_name"]  # 物品名，前端发布已判空
    # 物品信息
    model_goods.os_location = release_info.get('os_location', '').replace(',', '###')  # 发现位置
    model_goods.location = release_info.get('location', '').replace(',', '###')  # 放置位置
    model_goods.owner_name = "鲟回码主" if is_scan_return else release_info.get('owner_name', '无')
    model_goods.summary = release_info.get('summary', '无')
    model_goods.business_type = 2
    model_goods.mobile = release_info.get('mobile', '无')
    db.session.add(model_goods)
    db.session.flush()
    return model_goods


def returnToLostSuccess(return_goods=None, lost_goods=None, author=None):
    """
    寻物归还结束发帖
    :param author:
    :param return_goods:
    :param lost_goods: 
    :return: 
    """
    if not return_goods or not lost_goods or not author:
        return
    lost_id = lost_goods.id
    return_goods.status = 1
    return_goods.return_goods_id = lost_id
    return_goods.return_goods_openid = lost_goods.openid  # 用于被归还的用户快速查找归还通知
    # 寻物贴链接归还贴，状态置为预先寻回
    return_id = return_goods.id
    lost_goods.return_goods_id = return_id
    lost_goods.return_goods_openid = return_goods.openid  # 用于判断是归还用户查看了帖子详情
    now = datetime.datetime.now()
    lost_goods.confirm_time = now  # 指的是归还时间
    lost_goods.status = 2
    db.session.add(lost_goods)
    db.session.add(return_goods)
    MemberService.updateCredits(member_info=author)

    info = {'goods_name': return_goods.name,
            'returner': return_goods.nickname,
            'return_date': return_goods.created_time.strftime(
                "%Y-%m-%d %H:%M:%S"),
            'rcv_openid': lost_goods.openid}
    # 新归还帖
    # MADE
    db.session.commit()
    # 异步发送订阅消息
    SubscribeTasks.send_return_subscribe.delay(return_info=info)


def scanReturnSuccess(scan_goods=None, notify_id='', author=None):
    """
    扫码归还结束发帖
    ES同步和发送短信
    :param author:
    :param scan_goods:
    :param notify_id:
    :return:
    """
    # 链接归还的对象，直接就是对方的物品(如若不是可举报)
    if not scan_goods or not scan_goods or not author:
        return
    scan_goods.qr_code_openid = notify_id
    db.session.add(scan_goods)
    MemberService.updateCredits(member_info=author)
    # MADE
    db.session.commit()
    # 通知
    params = {
        'location': scan_goods.location,
        'goods_name': scan_goods.name,
        'rcv_openid': notify_id,
        'trig_openid': scan_goods.openid,
        'trig_member_id': scan_goods.member_id
    }
    SmsTasks.notifyQrcodeOwner.delay(params=params)


def releaseGoodsSuccess(goods_info=None, edit_info=None, author=None):
    """
    普通帖子结束发帖（可能是编辑）
    :param author:
    :param goods_info:
    :param edit_info:
    :return:
    """
    # goods 状态的变更
    is_edit = edit_info is not None
    if not is_edit:
        goods_info.status = 1
    db.session.add(goods_info)
    if not is_edit:
        MemberService.updateCredits(member_info=author)

    # MADE
    db.session.commit()
    RecommendTasks.autoRecommendGoods.delay(edit_info=edit_info, goods_info=queryToDict(goods_info))


def editGoods(goods_id=0, edit_info=None):
    """
    编辑信息
    :param goods_id:
    :param edit_info:
    :return:
    """
    goods_info = Good.query.filter_by(id=goods_id).first()
    if not goods_info:
        return None
    goods_info.pics = ""
    goods_info.main_image = ""
    goods_info.name = edit_info['goods_name']
    goods_info.owner_name = edit_info['owner_name']
    goods_info.summary = edit_info['summary']
    location = edit_info['location'].split(",")

    goods_info.location = "###".join(location)
    goods_info.business_type = edit_info['business_type']
    goods_info.mobile = edit_info['mobile']
    # 修改成置顶贴子
    if int(edit_info.get('is_top', 0)):
        goods_info.top_expire_time = datetime.datetime.now() + datetime.timedelta(days=int(edit_info['days']))
    goods_info.updated_time = datetime.datetime.now()

    img_list = edit_info['img_list']
    img_list_status = UploadService.filterUpImages(img_list)

    def __needImageUpload():
        for s in img_list_status:
            if not s:
                return True
        return False

    goods_info.status = 7 if __needImageUpload() else 1  # 暂时设置为不可见
    db.session.add(goods_info)
    db.session.commit()
    return img_list_status


def getNoMarksAfterDelPremark(found_ids=None, member_id=0):
    """
    取消认领后,可能没有人人领
    :param: found_ids
    :return:
    """
    no_marks = []
    for found_id in found_ids:
        marks = CacheQueryService.getMarkCache(goods_id=found_id)  # found_id 对应认领的member_id的集合
        if marks:
            # 缓存命中
            no_mark = len(marks) == 2 and str(member_id) in marks
        else:
            # 缓存不命中
            cnt = db.session.query(func.count(Mark.id)).filter(Mark.goods_id == found_id, Mark.status != 7).scalar()
            no_mark = cnt == 0
        if no_mark and GoodsCasUtil.exec(found_id, 2, 1):
            # 这里不会出问题，因为认领那里，进入后设置成了 7，缓存和数据库都提交后，才会被设置成2。
            no_marks.append(found_id)
    return no_marks


def getGoodsReadCount(goods_info=None):
    """
    返回阅读量（一天新增和本身）
    :param goods_info:
    :return:
    """
    read_cnt = CacheQueryService.getGoodsIncrReadCache(goods_id=goods_info.id)
    return goods_info.view_count + read_cnt


def setGoodsReadCount(has_read=1, goods_id=0):
    """
    设置当天新增阅读量
    :param has_read:
    :param goods_id:
    :return:
    """
    if not has_read:
        CacheOpService.setGoodsIncrReadCache(goods_id=goods_id)


def syncUpdatedReadCountInRedisToDb():
    """
    清除阅读量缓存，同步到DB
    :return:
    """
    CacheOpService.syncAndClearGoodsIncrReadCache()


def setRecommendRead(is_recommend_src=False, has_read=False, member_info=None, goods_id=0):
    """
    推荐来看的未读过的
    :param member_info:
    :param is_recommend_src:
    :param has_read:
    :param goods_id:
    :return:
    """
    if is_recommend_src and not has_read and member_info:
        # 从推荐记录进入详情,代表用户一定已经登陆了,只是以防万一
        MemberService.setRecommendStatus(member_id=member_info.id, goods_id=goods_id, new_status=1, old_status=0)


def getLostGoodsInfo(goods_info=None, member_info=None):
    """
    获取寻物信息
    :param goods_info:
    :param member_info:
    :return:
    """
    is_auth = False
    show_location = False
    if member_info:
        show_location = is_auth = member_info.id == goods_info.member_id
    data = makeGoodsCommonInfoData(goods_info=goods_info, show_location=show_location, is_auth=is_auth)
    is_top = goods_info.top_expire_time > datetime.datetime.now()
    data['top'] = is_top
    goods_status = goods_info.status
    if goods_status > 1 and member_info:
        is_returner = goods_info.return_goods_openid == member_info.openid
        # 需要判断予寻回的帖子是否已经确认过归还，已取回，对方有没有删除帖子
        op_time = goods_info.confirm_time if goods_status == 2 else goods_info.finish_time
        return_goods_id = goods_info.return_goods_id
        return_status = Good.query.filter_by(id=return_goods_id).with_entities(Good.status).first()
        more_data = {'is_returner': is_returner,
                     'return_goods_id': return_goods_id,  # 用来链接两贴
                     'is_confirmed': return_status[0] == 2,  # 根据是否已经确认过归还贴对寻物启示发布者和归还者进行提示
                     'is_origin_deleted': return_status[0] == 7,  # 根据此提示可以删除本贴
                     'op_time': op_time.strftime("%Y-%m-%d %H:%M")  # 根据此提示操作时间
                     }
        data.update(more_data)
    return data


def getFoundGoodsInfo(goods_info=None, member_info=None):
    """
    获取失物招领信息
    :param goods_info:
    :param member_info:
    :return:
    """
    is_auth = False
    show_location = False
    if member_info:
        is_auth = member_info.id == goods_info.member_id
        show_location = MemberService.hasMarkGoods(member_id=member_info.id, goods_id=goods_info.id) or is_auth
    data = makeGoodsCommonInfoData(goods_info=goods_info, show_location=show_location, is_auth=is_auth)
    goods_status = goods_info.status
    if not is_auth and goods_status in (3, 4):
        data.update({'is_owner': member_info and goods_info.owner_id == member_info.id})
    elif is_auth and goods_status in (2, 3, 4):
        # 作者查看对方操作的时间
        if goods_status == 2:
            op_time = goods_info.confirm_time
        elif goods_status == 3:
            op_time = goods_info.finish_time
        else:
            op_time = goods_info.thank_time
        data.update({'op_time': op_time.strftime("%Y-%m-%d %H:%M")})
    if goods_status == 5:
        # 申诉的时间
        data.update({'op_time': goods_info.appeal_time.strftime("%Y-%m-%d %H:%M")})
    return data


def getReturnGoodsInfo(goods_info=None, member_info=None):
    """
    只能在我的发布和归还通知看到，所以一定登陆了
    :param goods_info:
    :param member_info:
    :return:
    """
    is_auth = member_info.id == goods_info.member_id
    data = makeGoodsCommonInfoData(goods_info=goods_info, show_location=True, is_auth=is_auth)
    lost_goods_id = goods_info.return_goods_id
    goods_status = goods_info.status
    if goods_status == 1:
        more_data = {'return_goods_id': lost_goods_id}
        data.update(more_data)
    elif goods_status == 2:
        more_data = {'return_goods_id': lost_goods_id,
                     'op_time': goods_info.confirm_time.strftime("%Y-%m-%d %H:%M")}
        data.update(more_data)
    elif goods_status > 2:
        lost_goods_status = Good.query.filter_by(id=lost_goods_id).with_entities(Good.status).first()
        is_origin_del = lost_goods_status[0] == 7
        more_data = {'return_goods_id': lost_goods_id,
                     'is_origin_deleted': is_origin_del,  # 寻物已删
                     # 通知也删了，不再会有感谢
                     'is_no_thanks': not goods_info.return_goods_openid and is_origin_del,
                     'op_time': goods_info.finish_time.strftime("%Y-%m-%d %H:%M")}
        data.update(more_data)
    return data


def makeGoodsCommonInfoData(goods_info=None, show_location=False, is_auth=False):
    """
    获取不同business_type的帖子的共同信息
    :param goods_info:
    :param show_location:
    :param is_auth:
    :return:
    """
    # 例：上海市徐汇区肇嘉浜路1111号###美罗城###31.192948153###121.439673735
    location_list = goods_info.location.split("###")
    location_list[2] = eval(location_list[2])
    location_list[3] = eval(location_list[3])
    os_location_list = goods_info.os_location.split("###")
    os_location_list[2] = eval(os_location_list[2])
    os_location_list[3] = eval(os_location_list[3])
    goods_status = goods_info.status
    data = {
        # 物品帖子数据信息
        "id": goods_info.id,
        "business_type": goods_info.business_type,  # 寻物启示 or 失物招领
        "goods_name": goods_info.name,  # 物品名
        "owner_name": goods_info.owner_name,  # 物主名
        "summary": goods_info.summary,  # 简述
        "main_image": UrlManager.buildImageUrl(goods_info.main_image),
        "pics": [UrlManager.buildImageUrl(i) for i in goods_info.pics.split(",")],
        "location": location_list if show_location else APP_CONSTANTS['default_loc'],
        "os_location": os_location_list if show_location else APP_CONSTANTS['default_loc'],
        "mobile": goods_info.mobile,
        # 物品帖子作者信息
        "is_auth": is_auth,  # 是否查看自己发布的帖子(不能进行状态操作，可以编辑)
        "auther_id": goods_info.member_id,
        "auther_name": goods_info.nickname,
        "avatar": goods_info.avatar,
        # 为用户浏览和操作设计的信息
        "status_desc": str(goods_info.status_desc),
        "status": goods_status,
        "view_count": getGoodsReadCount(goods_info),  # 浏览量
        "updated_time": str(goods_info.updated_time),  # 被编辑的时间 or 首次发布的时间
        'show_location': show_location
    }
    return data
