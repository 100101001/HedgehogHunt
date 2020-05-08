# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/4/17 下午5:08
@file: GoodsService.py
@desc: 
"""
import datetime

from application import db, APP_CONSTANTS, app
from common.cahce.GoodsCasUtil import GoodsCasUtil
from common.cahce.core import CacheQueryService, CacheOpService
from common.libs.Helper import queryToDict
from common.libs.MemberService import MemberService
from common.libs.UploadService import UploadService
from common.libs.UrlManager import UrlManager
from common.libs.mall.PayService import PayService
from common.libs.mall.WechatService import WeChatService
from common.models.ciwei.Goods import Good
from common.models.ciwei.GoodsTopOrder import GoodsTopOrder
from common.models.ciwei.Mark import Mark
from common.models.ciwei.Recommend import Recommend
from common.models.ciwei.Thanks import Thank
from common.models.ciwei.logs.thirdservice.GoodsTopOrderCallbackData import GoodsTopOrderCallbackData
from common.tasks.recommend.v2 import RecommendTasks
from common.tasks.sms import SmsTasks
from common.tasks.subscribe import SubscribeTasks


def syncUpdatedReadCountInRedisToDb():
    """
    清除阅读量缓存，同步到DB
    :return:
    """
    CacheOpService.syncAndClearGoodsIncrReadCache()


class CommonGoodsHandler:
    __strategy_map = {'init_edit': '_initEditGoods',
                      'finish_edit': '_finishEditGoods',
                      'created': '_releaseOpenGoodsOk'}

    @classmethod
    def deal(cls, op, **kwargs):
        strategy = cls.__strategy_map.get(op)
        handler = getattr(cls, strategy, None)
        if handler:
            return handler(**kwargs)

    @classmethod
    def _initEditGoods(cls, goods_id=0, status=0, edit_info=None, **kwargs):
        """
        编辑信息
        :param goods_id:
        :param edit_info:
        :return:
        """

        if not GoodsCasUtil.exec(goods_id, status, -status):
            return False, "操作冲突，请稍后重试"

        goods_info = Good.getById(goods_id)
        if not goods_info:
            return False, '编辑失败'

        img_list = edit_info['img_list']
        img_list_status = UploadService.filterUpImages(img_list)

        goods_info.edit(edit_info=edit_info)
        db.session.commit()
        return True, img_list_status

    @classmethod
    def _finishEditGoods(cls, goods_info=None, edit_info=None, **kwargs):
        """
        结束编辑
        :param goods_info:
        :param edit_info:
        :param kwargs:
        :return:
        """
        cur_status = goods_info.status
        GoodsCasUtil.exec(goods_info.id, -cur_status, cur_status)  # 恢复init_edit时更改的状态标识
        # edit_info 传入推荐标识是否被改动
        RecommendTasks.autoRecommendGoods.delay(edit_info=edit_info, goods_info=queryToDict(goods_info))

    @classmethod
    def _releaseOpenGoodsOk(cls, goods_info=None, **kwargs):
        """
        公开的帖子结束发帖
        :param goods_info:
        :return:
        """
        # goods 状态的变更
        goods_info.status = 1
        db.session.add(goods_info)
        MemberService.updateCredits(member_id=goods_info.member_id)
        db.session.commit()

    @classmethod
    def _getCommonInfo(cls, goods_info=None, show_location=False, is_auth=False):
        """
        获取不同business_type的帖子的共同信息
        :param goods_info:
        :param show_location:
        :param is_auth:
        :return:
        """

        def __getReadCount():
            """
            返回阅读量（一天新增和本身）
            :return:
            """
            read_cnt = CacheQueryService.getGoodsIncrReadCache(goods_id=goods_info.id)
            return goods_info.view_count + read_cnt

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
            "location": location_list,
            "os_location": os_location_list,
            "mobile": goods_info.mobile,
            # 物品帖子作者信息
            "is_auth": is_auth,  # 是否查看自己发布的帖子(不能进行状态操作，可以编辑)
            "auther_id": goods_info.member_id,
            "auther_name": goods_info.nickname,
            "avatar": goods_info.avatar,
            # 为用户浏览和操作设计的信息
            "status_desc": str(goods_info.status_desc),
            "status": goods_status,
            "view_count": __getReadCount(),  # 浏览量
            "updated_time": str(goods_info.updated_time),  # 被编辑的时间 or 首次发布的时间
            'show_location': show_location
        }
        return data


    @classmethod
    def _getThanksInfo(cls, goods_id=0, lost_member=None):
        if goods_id:
            thank_info = CacheQueryService.getThankCache(goods_id)
            if not thank_info:
                thank_info = Thank.getByGoodsId(goods_id)
                CacheOpService.setThankInfoCache(thank_info)
            return {'summary': thank_info.summary, 'price': str(thank_info.thank_price),
                    'nickname': thank_info.nickname, 'avatar': thank_info.avatar}
        else:
            return {'summary': '谢谢你', 'price': '0',
                    'nickname': lost_member.nickname if lost_member else '鲟回', 'avatar': lost_member.avatar if lost_member else '/images/more/un_reg_user.png'}


    @classmethod
    def _preMarkGoods(cls, member_id=0, goods_id=0, business_type=1):
        """
        预认领
        :param business_type:
        :param member_id:
        :param goods_id:
        :return:
        """
        if not member_id or not goods_id:
            return
        Mark.pre(member_id=member_id, goods_id=goods_id, business_type=business_type)

    @classmethod
    def _cancelPremark(cls, goods_ids=None, member_id=0):
        """
        :return: 外面修改Goods状态还要用的mark_key
        """
        Mark.mistaken(goods_ids=goods_ids, member_id=member_id)

    @classmethod
    def _markedGoods(cls, member_id=0, goods_ids=None):
        """
        确认取回物品
        :param member_id:
        :param goods_ids:
        :return:
        """
        Mark.done(goods_ids=goods_ids, member_id=member_id)


class LostGoodsHandler(CommonGoodsHandler):
    __strategy_map = {'init_top_pay': '_initTopPay',
                      'finish_top_pay': '_finishTopPay',
                      'init': '_initLostRelease',
                      'created': '_finishLostRelease',
                      'info': '_getLostInfo'}

    wechat = WeChatService(merchant_key=app.config['OPENCS_APP']['mch_key'])

    @classmethod
    def deal(cls, op, **kwargs):
        strategy = cls.__strategy_map.get(op)
        handler = getattr(cls, strategy, None)
        if handler:
            return handler(**kwargs)

    @classmethod
    def _initTopPay(cls, consumer=None, price='', top_charge=''):
        model_order = GoodsTopOrder(consumer=consumer, price=price, top_charge=top_charge)
        # 微信下单
        pay_data = {
            'appid': app.config['OPENCS_APP']['appid'],
            'mch_id': app.config['OPENCS_APP']['mch_id'],
            'nonce_str': cls.wechat.get_nonce_str(),
            'body': '鲟回-置顶',
            'out_trade_no': model_order.order_sn,
            'total_fee': int(model_order.price * 100),
            'notify_url': app.config['APP']['domain'] + "/api/goods/top/order/notify",
            'time_expire': (datetime.datetime.now() + datetime.timedelta(minutes=5)).strftime("%Y%m%d%H%M%S"),
            'trade_type': 'JSAPI',
            'openid': model_order.openid
        }
        pay_sign_data = cls.wechat.get_pay_info(pay_data=pay_data)
        if not pay_sign_data:
            return None
        model_order.status = 0
        db.session.commit()
        return pay_sign_data

    @classmethod
    def _finishTopPay(cls, callback_body=None):
        result_data = {
            'return_code': 'SUCCESS',
            'return_msg': 'OK'
        }
        header = {'Content-Type': 'application/xml'}
        callback_data = cls.wechat.xml_to_dict(callback_body)
        app.logger.info(callback_data)

        # 检查签名
        sign = callback_data.pop('sign')
        gene_sign = cls.wechat.create_sign(callback_data)
        if sign != gene_sign:
            result_data['return_code'] = result_data['return_msg'] = 'FAIL'
            return cls.wechat.dict_to_xml(result_data), header
        if callback_data['result_code'] != 'SUCCESS':
            result_data['return_code'] = result_data['return_msg'] = 'FAIL'
            return cls.wechat.dict_to_xml(result_data), header
        # 检查订单金额
        pay_order_info = GoodsTopOrder.getByOrderSn(callback_data['out_trade_no'])
        if not pay_order_info:
            result_data['return_code'] = result_data['return_msg'] = 'FAIL'
            return cls.wechat.dict_to_xml(result_data), header
        if int(pay_order_info.price * 100) != int(callback_data['total_fee']):
            result_data['return_code'] = result_data['return_msg'] = 'FAIL'
            return cls.wechat.dict_to_xml(result_data), header

        # 更新订单的支付/物流状态, 记录日志
        # 订单状态已回调更新过直接返回
        if pay_order_info.status == 1:
            return cls.wechat.dict_to_xml(result_data), header
        # 订单状态未回调更新过
        cls.__topOrderSuccess(order_info=pay_order_info,
                              params={"pay_sn": callback_data['transaction_id'],
                                      "paid_time": callback_data['time_end']})
        cls.__addTopPayCallbackData(order_id=pay_order_info.id, data=callback_body)
        db.session.commit()
        return cls.wechat.dict_to_xml(result_data), header

    @classmethod
    def __addTopPayCallbackData(cls, order_id=0, data=''):
        """
        微信支付回调记录
        :param order_id:
        :param data:
        :return:
        """
        # 新增
        PayService.addCallbackData(GoodsTopOrderCallbackData, 'top_order_id', order_id, data=data)

    @classmethod
    def __topOrderSuccess(cls, order_info=None, params=None):
        """
        支付成功后,更新订单状态
        :param order_info:
        :param params:
        :return: 数据库操作成功
        """
        PayService.orderPaid(order_info=order_info, params=params)

    @classmethod
    def _initLostRelease(cls, author_info=None, release_info=None, **kwargs):
        """
        发布寻物启事
        :param author_info:
        :param release_info:
        :return:
        """
        os_location = release_info.get('os_location')
        if not os_location:
            os_location = APP_CONSTANTS['default_lost_loc']
        now = datetime.datetime.now()
        top_expire = now if not int(release_info.get('is_top', 0)) else \
            now + datetime.timedelta(days=int(release_info['days']))
        model_goods = Good(author_info=author_info, business_type=0,
                           mobile=release_info.get('mobile', '无'),
                           name=release_info.get('goods_name'),
                           owner_name=release_info.get('owner_name', '无'),
                           summary=release_info.get('summary', '无'),
                           os_location=os_location,
                           location=release_info.get('location', ''),
                           top_expire=top_expire)
        db.session.flush()
        return model_goods

    @classmethod
    def _finishLostRelease(cls, goods_info=None, **kwargs):
        super()._releaseOpenGoodsOk(goods_info=goods_info)

    @classmethod
    def _getLostInfo(cls, goods_info=None, member_info=None, **kwargs):
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
        data = super()._getCommonInfo(goods_info=goods_info, show_location=show_location, is_auth=is_auth)
        is_top = goods_info.top_expire_time > datetime.datetime.now()
        data['top'] = is_top
        goods_status = goods_info.status
        if goods_status > 1 and member_info:
            is_returner = goods_info.return_goods_openid == member_info.openid
            data.update({'is_returner': is_returner})
            if is_returner or is_auth:
                # 需要判断予寻回的帖子是否已经确认过归还，已取回，对方有没有删除帖子
                op_time = goods_info.confirm_time if goods_status == 2 else goods_info.finish_time
                return_goods_id = goods_info.return_goods_id
                return_status = Good.query.filter_by(id=return_goods_id).with_entities(Good.status).first()
                more_data = {'return_goods_id': return_goods_id,  # 用来链接两贴
                             'is_confirmed': return_status[0] == 2,  # 根据是否已经确认过归还贴对寻物启示发布者和归还者进行提示
                             'is_origin_deleted': return_status[0] < 0,  # 根据此提示可以删除本贴
                             'op_time': op_time.strftime("%Y-%m-%d %H:%M")  # 根据此提示操作时间
                             }
                data.update(more_data)
                if goods_status == 4:
                    thanks = super()._getThanksInfo(goods_info.return_goods_id, lost_member=member_info)
                    data.update({'thank_info': thanks})
        return data


class ReturnGoodsHandler(CommonGoodsHandler):
    __strategy_map = {'init': '_initReturnRelease',
                      'created': '_finishReturnRelease',
                      'info': '_getReturnInfo',
                      'cancel': '_delReturns',
                      'open': '_openReturn',
                      'reject': '_rejectReturn',
                      'confirm': '_confirmReturn',
                      'gotback': '_gotbackReturn',
                      'del_link': '_delLink'}

    @classmethod
    def deal(cls, op, **kwargs):
        strategy = cls.__strategy_map.get(op)
        handler = getattr(cls, strategy, None)
        if handler:
            return handler(**kwargs)

    @classmethod
    def _initReturnRelease(cls, author_info=None, release_info=None, is_scan_return=False, **kwargs):
        """
        发布归还贴，寻物归还和扫码归还
        :param author_info:
        :param release_info:
        :param is_scan_return:
        :return:
        """
        owner_name = "鲟回码主" if is_scan_return else release_info.get('owner_name', '无')
        model_goods = Good(author_info=author_info, business_type=2,
                           mobile=release_info.get('mobile', '无'),
                           name=release_info.get('goods_name'),
                           owner_name=owner_name,
                           summary=release_info.get('summary', '无'),
                           os_location=release_info.get('os_location', APP_CONSTANTS['default_lost_loc']),
                           location=release_info.get('location', APP_CONSTANTS['default_lost_loc']))
        db.session.flush()
        return model_goods

    @classmethod
    def _finishReturnRelease(cls, lost_id=-1, notify_id='', goods_info=None, **kwargs):
        def __returnToLostOk(return_goods=None):
            """
            寻物归还结束发帖
            :param return_goods:
            :return:
            """
            if not return_goods or not lost_goods:
                return
            Good.link(return_goods=return_goods, lost_goods=lost_goods)
            MemberService.updateCredits(member_id=return_goods.member_id)
            info = {'goods_name': return_goods.name,
                    'returner': return_goods.nickname,
                    'return_date': return_goods.created_time.strftime(
                        "%Y-%m-%d %H:%M:%S"),
                    'rcv_openid': lost_goods.openid}
            # 异步发送订阅消息
            SubscribeTasks.send_return_subscribe.delay(return_info=info)
            db.session.commit()

        def __scanReturnOk(scan_goods=None):
            """
            扫码归还结束发帖
            ES同步和发送短信
            :param scan_goods:
            :param notify_id:
            :return:
            """
            # 链接归还的对象，直接就是对方的物品(如若不是可举报)
            if not scan_goods or not notify_id:
                return
            scan_goods.qr_code_openid = notify_id
            db.session.add(scan_goods)
            MemberService.updateCredits(member_id=scan_goods.member_id)
            # 通知
            params = {
                'location': scan_goods.location,
                'goods_name': scan_goods.name,
                'trig_rcv': {
                    'rcv_openid': notify_id,
                    'trig_openid': scan_goods.openid,
                    'trig_member_id': scan_goods.member_id
                }
            }
            SmsTasks.notifyQrcodeOwner.delay(params=params)
            db.session.commit()

        if lost_id != -1:
            # 寻物归还
            lost_goods = Good.getById(lost_id)
            if lost_goods and lost_goods.status == 1 and GoodsCasUtil.exec_wrap(lost_id, ['nil', 1], 2):
                __returnToLostOk(return_goods=goods_info)
            else:
                goods_info.business_type = 1
                super()._releaseOpenGoodsOk(goods_info=goods_info)
        elif notify_id:
            # 扫码归还
            __scanReturnOk(scan_goods=goods_info)

    @classmethod
    def _getReturnInfo(cls, goods_info=None, member_info=None, **kwargs):
        """
        只能在我的发布和归还通知看到，所以一定登陆了
        :param goods_info:
        :param member_info:
        :return:
        """
        is_auth = member_info.id == goods_info.member_id
        data = super()._getCommonInfo(goods_info=goods_info, show_location=True, is_auth=is_auth)
        lost_goods_id = goods_info.return_goods_id
        goods_status = goods_info.status
        if goods_status == 1:
            more_data = {'return_goods_id': lost_goods_id}
            data.update(more_data)
        elif goods_status == 2:
            more_data = {'return_goods_id': lost_goods_id,
                         'op_time': goods_info.confirm_time.strftime("%Y-%m-%d %H:%M")}
            data.update(more_data)
        elif goods_status in (3, 4):
            lost_goods_status = Good.query.filter_by(id=lost_goods_id).with_entities(Good.status).first()
            is_origin_del = lost_goods_status[0] < 0
            op_time = goods_info.finish_time if goods_status == 3 else goods_info.thank_time
            more_data = {'return_goods_id': lost_goods_id,
                         'is_origin_deleted': is_origin_del,  # 寻物已删
                         # 通知也删了，不再会有感谢
                         'is_no_thanks': not goods_info.return_goods_openid and is_origin_del,
                         'op_time': op_time.strftime("%Y-%m-%d %H:%M")}
            data.update(more_data)
            if goods_status == 4:
                thanks = super()._getThanksInfo(goods_info.id)
                data.update({'thank_info': thanks})
        return data

    @classmethod
    def _delReturns(cls, return_ids=None, status=0, **kwargs):
        lost_ids = Good.getLinkId(return_ids)
        if not GoodsCasUtil.judgePair(return_ids, status, -status, lost_ids, 2, 1):
            return False, '操作冲突，请稍后重试'
        # 寻物启示
        Good.batch_update(Good.id.in_(lost_ids), Good.status == 2,
                          val={'status': 1, 'return_goods_id': 0, 'return_goods_openid': ''}, rds=1)
        # 归还贴
        Good.batch_update(Good.id.in_(return_ids), Good.status == status,
                          val={'status': -Good.status, 'return_goods_id': 0, 'return_goods_openid': ''})
        db.session.commit()
        return True, ''

    @classmethod
    def _openReturn(cls, return_ids=None, status=None, **kwargs):
        if status == 0:
            # 公开已拒绝的归还贴（只有作者能操作）
            GoodsCasUtil.set(return_ids, exp_val=0, new_val=1)
            Good.batch_update(Good.id.in_(return_ids), Good.status == status,
                              val={'status': 1, 'business_type': 1, 'top_expire_time': datetime.datetime.now()}, rds=1)
        elif status == 1:
            # 其实（再待确认的归还记录，和寻物详情）
            # 公开待确认的归还贴
            lost_ids = Good.getLinkId(return_ids)
            # 原子公开
            if not GoodsCasUtil.judgePair(return_ids, status, 1, lost_ids, 2, 1):
                return False, '操作冲突，请稍后重试'
            # 寻物启
            Good.batch_update(Good.id.in_(lost_ids), Good.status == 2,
                              val={'status': 1, 'return_goods_id': 0, 'return_goods_openid': ''}, rds=1)
            Good.batch_update(Good.id.in_(return_ids), Good.status == status,
                              val={'status': 1, 'business_type': 1, 'top_expire_time': datetime.datetime.now(),
                                   'return_goods_id': 0, 'return_goods_openid': ''}, rds=1)
        db.session.commit()
        return True, ''

    @classmethod
    def _rejectReturn(cls, return_ids=None, status=0, **kwargs):

        lost_ids = Good.getLinkId(return_ids)
        # 原子拒绝
        if not GoodsCasUtil.judgePair(return_ids, status, 0, lost_ids, 2, 1):
            return False, '操作冲突，请稍后重试'

        # 寻物启示和归还贴
        Good.batch_update(Good.id.in_(lost_ids), Good.status == 2,
                          val={'status': 1, 'return_goods_id': 0, 'return_goods_openid': ''}, rds=1)
        Good.batch_update(Good.id.in_(return_ids), Good.status == status,
                          val={'status': 0, 'return_goods_id': 0, 'return_goods_openid': ''})
        db.session.commit()
        return True, ''

    @classmethod
    def _confirmReturn(cls, return_id=0, status=0, confirmer_id=0, **kwargs):
        # 原子确认
        if not GoodsCasUtil.exec(return_id, status, 2):
            return False, '操作冲突，请稍后重试'

        # 归还
        Good.batch_update(Good.id == return_id, Good.status == status,
                          val={'status': 2, 'confirm_time': datetime.datetime.now()})
        super()._preMarkGoods(member_id=confirmer_id, goods_id=return_id, business_type=2)
        db.session.commit()
        return True, ''

    @classmethod
    def _gotbackReturn(cls, goods_ids=None, member_id=0, status=0, biz_type=2, **kwargs):
        now = datetime.datetime.now()
        # 在待取回的归还贴中(批量)操作确认
        pair_goods_ids = Good.getLinkId(goods_ids)
        if not GoodsCasUtil.judgePair(goods_ids, status, 3, pair_goods_ids, status, 3):
            return False, '操作冲突，请稍后重试'

        lost_updated = {'status': 3, 'finish_time': now}
        return_updated = {'status': 3, 'owner_id': member_id, 'finish_time': now}
        if biz_type == 2:
            return_ids = goods_ids
            lost_ids = pair_goods_ids
        else:
            lost_ids = goods_ids
            return_ids = pair_goods_ids
        # 寻物启事
        Good.batch_update(Good.id.in_(lost_ids), Good.status == 2, val=lost_updated)
        # 归还
        Good.batch_update(Good.id.in_(return_ids), Good.status == 2, val=return_updated)
        # 标记认领记录
        super()._markedGoods(member_id=member_id, goods_ids=return_ids)
        # 异步发送订阅消息
        SubscribeTasks.send_return_finish_msg_in_batch.delay(gotback_returns=[item[0] for item in return_ids])
        db.session.commit()
        return True, ''

    @classmethod
    def _delLink(cls, return_ids=None, lost_ids=None, status=None, **kwargs):
        if return_ids:
            # 删除归还对应的丢失
            lost_ids = Good.getLinkId(return_ids)
            GoodsCasUtil.set(lost_ids, exp_val=status, new_val=-status)
            Good.batch_update(Good.id.in_(lost_ids), Good.status == status, val={'status': -status})
        elif lost_ids:
            # 删除丢失对应的归还
            return_ids = Good.getLinkId(lost_ids)
            Good.batch_update(Good.id.in_(return_ids), val={'return_goods_openid': ''})
        db.session.commit()


class FoundGoodsHandler(CommonGoodsHandler):
    __strategy_map = {
        'init': '_initFoundRelease',
        'created': '_finishFoundRelease',
        'info': '_getFoundInfo',
        'to_sys': '_sendFoundToSys',
        'pre_mark': '_preMarkFound',
        'mistaken': '_mistakenPreMarkFound',
        'gotback': '_gotbackFound'
    }

    @classmethod
    def deal(cls, op, **kwargs):
        strategy = cls.__strategy_map.get(op)
        handler = getattr(cls, strategy, None)
        if handler:
            return handler(**kwargs)

    @classmethod
    def _initFoundRelease(cls, author_info=None, release_info=None, **kwargs):
        """
        发布失物招领
        :param author_info:
        :param release_info:
        :return:
        """
        os_location = release_info.get("os_location", '')
        location = release_info.get('location', '')  # 放置位置
        if not location:
            location = os_location
        model_goods = Good(author_info=author_info, business_type=1,
                           mobile=release_info.get('mobile', '无'),
                           name=release_info.get('goods_name'),
                           owner_name=release_info.get('owner_name', '无'),
                           summary=release_info.get('summary', '无'),
                           os_location=os_location,
                           location=location)
        db.session.flush()
        return model_goods

    @classmethod
    def _finishFoundRelease(cls, goods_info=None, **kwargs):
        super()._releaseOpenGoodsOk(goods_info=goods_info)

    @classmethod
    def _getFoundInfo(cls, goods_info=None, member_info=None, **kwargs):
        """
        获取失物招领信息
        :param goods_info:
        :param member_info:
        :return:
        """

        def __getMarks(goods_id=0):
            """
            是否预认领/认领了该物品(详情可否见放置地址)
            :param member_id:
            :param goods_id:
            :return:
            """
            if not goods_id:
                return False
            # 缓存中获取goods_id 对应的 member_id 集合
            mark_member_ids = CacheQueryService.getMarkCache(goods_id=goods_id)
            if not mark_member_ids:
                # 缓存不命中, 从数据库获取一个物品的所有认领人的id
                marks = Mark.getAllOn(goods_id=goods_id)
                mark_member_ids = CacheOpService.setMarkCache(goods_id=goods_id, marks=marks)
            return mark_member_ids

        def __hasMarks(member_id=0, marks=None):
            return bool(str(member_id) in marks)

        is_auth = False
        show_location = False
        all_marks = __getMarks(goods_id=goods_info.id)
        over_marks = len(all_marks) > 2
        if member_info:
            is_auth = member_info.id == goods_info.member_id
            show_location = __hasMarks(member_id=member_info.id, marks=all_marks) or is_auth
        data = super()._getCommonInfo(goods_info=goods_info, show_location=show_location, is_auth=is_auth)
        data.update({'is_owner': member_info and goods_info.owner_id == member_info.id,
                     'over_marks': over_marks})
        goods_status = goods_info.status
        if is_auth and goods_status in (2, 3, 4):
            # 作者查看对方操作的时间
            if goods_status == 2:
                op_time = goods_info.confirm_time
            elif goods_status == 3:
                op_time = goods_info.finish_time
            else:
                op_time = goods_info.thank_time
            data.update({'op_time': op_time.strftime("%Y-%m-%d %H:%M")})
        if goods_status == 4:
            thanks = super()._getThanksInfo(goods_info.id)
            data.update({'thank_info': thanks})
        if goods_status == 5:
            # 申诉的时间
            data.update({'op_time': goods_info.appeal_time.strftime("%Y-%m-%d %H:%M")})
        return data

    @classmethod
    def _sendFoundToSys(cls, goods_ids=None, status=1, **kwargs):
        # CAS并发保护
        ok_goods_id = GoodsCasUtil.filter(goods_ids, exp_val=status, new_val=-status)
        updated = {'member_id': APP_CONSTANTS['sys_author']['member_id'],
                   'openid': APP_CONSTANTS['sys_author']['openid'],
                   'nickname': APP_CONSTANTS['sys_author']['nickname'],
                   'avatar': APP_CONSTANTS['sys_author']['avatar']}
        Good.batch_update(Good.status == status, Good.id.in_(ok_goods_id), val=updated)
        db.session.commit()
        # CAS并发保护
        GoodsCasUtil.set(ok_goods_id, exp_val=-status, new_val=status)

    @classmethod
    def _preMarkFound(cls, goods_id=0, status=0, member_id=0, now=datetime.datetime.now(), **kwargs):
        if not GoodsCasUtil.exec(goods_id, status, -status):
            # 取消认领会 2——> 1，所以设置 -status
            return False, '操作冲突，请稍后重试'
        # 预认领事务
        super()._preMarkGoods(member_id=member_id, goods_id=goods_id, business_type=1)
        if status == 1:
            Good.batch_update(Good.id == goods_id, Good.status == status, val={'status': 2, 'confirm_time': now},
                              rds=-1)
        db.session.commit()
        # 认领缓存
        CacheOpService.addPreMarkCache(goods_id=goods_id, member_id=member_id)
        # CAS 解锁
        GoodsCasUtil.exec(goods_id, -status, 2)
        return True, ''

    @classmethod
    def _mistakenPreMarkFound(cls, goods_ids=None, status=0, member_id=0, **kwargs):

        def __getNoMarksAfterDelPremark():
            """
            取消认领后,可能没有人人领
            :return:
            """
            no_marks = []
            for found_id in goods_ids:
                marks = CacheQueryService.getMarkCache(goods_id=found_id)  # found_id 对应认领的member_id的集合
                if marks:
                    # 缓存命中
                    no_mark = len(marks) == 2 and str(member_id) in marks
                else:
                    # 缓存不命中
                    no_mark = Mark.isNoMarkOn(goods_id=found_id)
                if no_mark and GoodsCasUtil.exec(found_id, 2, 1):
                    # 这里不会出问题，因为认领那里，进入后设置成了负的，缓存和数据库都提交后，才会被设置成2。
                    no_marks.append(found_id)
            return no_marks

        super()._cancelPremark(goods_ids=goods_ids, member_id=member_id)
        if status == 2:
            # 对于于认领的物品，状态可能发生变更
            no_marks = __getNoMarksAfterDelPremark()
            if len(no_marks) > 0:
                Good.batch_update(Good.id.in_(no_marks), Good.status == status, val={'status': 1}, rds=1)
        db.session.commit()
        CacheOpService.removePreMarkCache(found_ids=goods_ids, member_id=member_id)

    @classmethod
    def _gotbackFound(cls, goods_ids=None, status=0, member_id=0, **kwargs):
        cas_res = GoodsCasUtil.judge(goods_ids, exp_val=status, new_val=3)
        if not cas_res:
            return False, '操作冲突，请稍后重试'

        # 失物招领贴的认领事务
        Good.batch_update(Good.id.in_(goods_ids), Good.status == status,
                          val={'status': 3, 'owner_id': member_id, 'finish_time': datetime.datetime.now()})
        # 不加锁是因为，不影响goods的认领计数，且是一个人的操作
        super()._markedGoods(member_id=member_id, goods_ids=goods_ids)
        db.session.commit()
        # 异步发送消息
        SubscribeTasks.send_found_finish_msg_in_batch.delay(gotback_founds=goods_ids)
        return True, ''


class GoodsReleaseHandler:
    __strategy_map = {
        -1: CommonGoodsHandler,  # 编辑是不论类型的
        0: LostGoodsHandler,
        1: FoundGoodsHandler,
        2: ReturnGoodsHandler
    }

    @classmethod
    def deal(cls, op, biz_typo=0, **kwargs):
        releaser = cls.__strategy_map.get(biz_typo)
        handler = getattr(releaser, 'deal', None)
        if handler:
            return handler(op, **kwargs)


class GoodsInfoHandler:
    __strategy_map = {
        'info': '_getInfo',
        'read': '_setRead',
        'checked': '_setRecommendChecked'
    }

    def __init__(self, goods_info=None, member_info=None, has_read=True):
        self.goods_info = goods_info
        self.has_read = has_read
        self.member_info = member_info

    def deal(self, op, **kwargs):
        strategy = self.__strategy_map.get(op)
        handler = getattr(self, strategy, None)
        if handler:
            return handler(**kwargs)

    def _getInfo(self, **kwargs):
        return GoodsReleaseHandler.deal('info', biz_typo=self.goods_info.business_type, goods_info=self.goods_info,
                                        member_info=self.member_info)

    def _setRead(self):
        """
        设置当天新增阅读量
        :return:
        """
        if not self.has_read:
            CacheOpService.setGoodsIncrReadCache(goods_id=self.goods_info.id)

    def _setRecommendChecked(self, is_recommend_src=False):
        """
        推荐来看的未读过的
        :param is_recommend_src:
        :return:
        """
        if is_recommend_src and not self.has_read and self.member_info:
            # 从推荐记录进入详情,代表用户一定已经登陆了,只是以防万一
            Recommend.checked(member_id=self.member_info.id, goods_id=self.goods_info.id)


class GoodsHandlers:
    """
    这里只包含直接提供其他外调服务（DDD操作）的类
    """
    __handlers = {'return': ReturnGoodsHandler,
                  'found': FoundGoodsHandler,
                  'lost': LostGoodsHandler,
                  'release': GoodsReleaseHandler,
                  'info': GoodsInfoHandler}

    @classmethod
    def get(cls, biz_type):
        return cls.__handlers.get(biz_type)
