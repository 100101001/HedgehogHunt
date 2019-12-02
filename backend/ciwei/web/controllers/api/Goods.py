#!/usr/bin/python3.6.8
#Editor weichaoxu

# -*- coding:utf-8 -*-
from common.models.ciwei.Member import Member
from common.models.ciwei.Goods import Good
from common.models.ciwei.Report import Report
from common.libs.Helper import getUuid
from decimal import Decimal
from common.libs.UploadService import UploadService
from web.controllers.api import route_api
from flask import request,jsonify,g
from application import app,db
from common.libs.Helper import getCurrentDate
from common.libs.UrlManager import UrlManager
from sqlalchemy import or_
from common.libs.Helper import selectFilterObj,getDictFilterField
from common.libs.MemberService import MemberService



@route_api.route("/goods/create", methods=['GET', 'POST'])
def createGoods():
    resp = {'code': 200, 'msg': 'create goods data successfully(goods/add)', 'data': {}}
    req = request.values

    member_info = g.member_info
    if not member_info:
        resp['code'] = -1
        resp['msg'] = "没有用户信息，无法发布，请授权登陆！"
        return jsonify(resp)


    name = req["goods_name"] if 'goods_name' in req else ''
    if not name:
        resp['code'] = -1
        resp['msg'] = "上传数据失败"
        return jsonify(resp)

    model_goods=Good()
    model_goods.member_id=member_info.id
    model_goods.name=name
    model_goods.target_price=Decimal(req['target_price']).quantize(Decimal('0.00')) if  'target_price' in req else 0.00
    business_type=req['business_type'] if 'business_type' in req else 5
    if business_type==5:
        resp['code'] = -1
        resp['msg'] = "交易类型错误"
        resp['data'] = req
        return jsonify(resp)
        # 修改用户的地址
    model_goods.owner_name=req['owner_name']
    model_goods.summary=req['summary']
    model_goods.location=req['location']
    model_goods.business_type=business_type
    model_goods.status=7#创建未完成
    model_goods.mobile=req['mobile']
    model_goods.updated_time=model_goods.created_time=getCurrentDate()
    db.session.add(model_goods)
    db.session.commit()
    goods_info = model_goods

    # 发布成功，用户积分涨5
    MemberService.updateCredits(member_info)
    #返回商品记录的id，用于后续添加图片
    resp['id']=goods_info.id
    #判断图片是否已经存在于网上
    img_list=req['img_list']
    img_list_status=UploadService.filterUpImages(img_list)
    resp['img_list_status'] = img_list_status
    return jsonify(resp)

@route_api.route("/goods/add-pics", methods=['GET', 'POST'])
def addGoodsPics():
    resp = {'code':200,'msg':'操作成功','state': 'add pics success'}
    #获取商品id
    req = request.values

    member_info = g.member_info
    if not member_info:
        resp['code'] = -1
        resp['msg'] = '用户信息异常'
        return jsonify(resp)

    id=req['id'] if 'id' in req else 0
    if id==0:
        resp['msg']="cant't get id"
        resp['req']=req
        return jsonify(resp)

    images_target = request.files
    image = images_target['file'] if 'file' in images_target else None

    if image is None:
        resp['code'] = -1
        resp['msg'] = '图片上传失败'
        return jsonify(resp)

    ret = UploadService.uploadByFile(image)
    if ret['code'] != 200:
        resp['code']=-1
        resp['msg']='图片上传失败'
        return jsonify(resp)

    #将返回的本地链接加到列表，并且保存为字符串
    pic_url=ret['data']['file_key']
    goods_info=Good.query.filter_by(id=id).with_for_update().first()
    if not goods_info:
        resp['code'] = -1
        resp['msg'] = '没有找到相关商品信息'
        return jsonify(resp)

    if not goods_info.pics:
        pics_list=[]

    else:
        pics_list=goods_info.pics.split(",")

    pics_list.append(pic_url)
    goods_info.main_image=pics_list[0]
    goods_info.pics=",".join(pics_list)
    db.session.add(goods_info)
    db.session.commit()
    return jsonify(resp)

@route_api.route("/goods/end-create", methods=['GET', 'POST'])
def endCreate():
    resp = {'code': 200, 'msg': '操作成功', 'state': 'add pics success'}
    member_info = g.member_info
    if not member_info:
        resp['code'] = -1
        resp['msg'] = '用户信息异常'
        return jsonify(resp)

    resp = {'code':200,'msg': 'create goods success','data':{}}
    #获取商品id
    req = request.values
    id=req['id'] if 'id' in req else 0
    if id==0:
        resp['msg']="数据传输失败"
        resp['req']=req
        return jsonify(resp)

    goods_info=Good.query.filter_by(id=id).with_for_update().first()
    if not goods_info:
        resp['code'] = -1
        resp['msg'] = '没有找到相关商品信息'
        return jsonify(resp)

    if goods_info.status==7:
        goods_info.status=1
    goods_info.updated_time=getCurrentDate()
    db.session.add(goods_info)
    db.session.commit()

    return jsonify(resp)

@route_api.route("/goods/search",methods=['GET','POST'])
def goodsSearch():
    resp={'code':200,'msg':'search successfully(search)','data':{}}
    req=request.values

    p=int(req['p']) if ('p' in req and req['p']) else 1
    if p<1:
        p=1

    page_size=10
    offset=(p-1)*page_size

    status = int(req['status']) if ('status' in req and req['status']) else 0
    query=Good.query.filter(Good.status!=7)

    business_type = int(req['business_type']) if 'business_type' in req else 'nono'
    if business_type == 0 or business_type == 1:
        query =query.filter_by(business_type=business_type)

    if status==0:
        resp['code'] = -1
        resp['msg'] = '商品状态码错误'
        return jsonify(resp)
    if status==-1:
        query=query.filter(Good.status!=4)
        query=query.filter(Good.status!=5)
        query=query.filter(Good.status!=6)
    else:
        query=query.filter_by(status=status)

    owner_name=req['owner_name'] if 'owner_name' in req else ''
    if owner_name:
        rule = or_(Good.owner_name.ilike("%{0}%".format(owner_name)))
        query = query.filter(rule)

    mix_kw = str(req['mix_kw']) if 'mix_kw' in req else ''
    if mix_kw:
        fil_str = "%{0}%".format(mix_kw[0])
        for i in mix_kw[1:]:
            fil_str = fil_str + "%{0}%".format(i)
        rule=or_(Good.name.ilike("%{0}%".format(fil_str)),Good.member_id.ilike("%{0}%".format(mix_kw)))
        query=query.filter(rule)

    #用地址筛选
    filter_address=str(req['filter_address']) if 'filter_address' in req else ''
    if filter_address:
        fil_str="%{0}%".format(filter_address[0])
        for i in filter_address[1:]:
            fil_str =fil_str+ "%{0}%".format(i)
        rule = or_(Good.location.ilike(fil_str))
        query = query.filter(rule)

    # #将对应的用户信息取出来，组合之后返回
    goods_list=query.order_by(Good.id.desc(),Good.view_count.desc()).offset(offset).limit(10).all()
    data_goods_list = []
    if goods_list:
        #获取用户的信息
        member_ids= selectFilterObj(goods_list, "member_id")
        member_map = getDictFilterField(Member, Member.id, "id", member_ids)

        for item in goods_list:
            tmp_member_info = member_map[item.member_id]
            tmp_data = {
                "id": item.id,
                "goods_name":item.name,
                "owner_name":item.owner_name,
                "updated_time":str(item.updated_time),
                "business_type":item.business_type,
                "summary":item.summary,
                "main_image":UrlManager.buildImageUrl(item.main_image),
                "auther_name":tmp_member_info.nickname,
                "avatar":tmp_member_info.avatar,
                "selected":False,
                "status_desc":str(item.status_desc),#静态属性，返回状态码对应的文字
            }
            data_goods_list.append(tmp_data)

    resp['data']['list']=data_goods_list
    resp['data']['has_more']=0 if len(data_goods_list)<page_size else 1
    resp['business_type']=business_type
    return jsonify(resp)

@route_api.route('/goods/applicate')
def goodsApplicate():
    resp = {'code': 200, 'msg': 'operate successfully(get info)', 'data': {}}
    req = request.values

    id = int(req['id']) if ('id' in req and req['id']) else 0
    goods_info=Good.query.filter_by(id=id).first()
    if not goods_info:
        resp['code']=-1
        resp['msg']='没有找到相关商品信息'
        return jsonify(resp)

    auther_info=Member.query.filter_by(id=goods_info.member_id).first()
    if not auther_info:
        resp['code'] = -1
        resp['msg'] = '没有找到相关发布者信息'
        return jsonify(resp)

    member_info=g.member_info
    #用户能否看到地址,如果是在mark列表或者发布者可以看到地址和电话
    goods_mark_id=goods_info.mark_id
    if goods_mark_id:
        goods_mark_id_list=goods_mark_id.split('#')
        goods_mark_id_list.append(str(member_info.id))
        goods_info.mark_id="#".join(goods_mark_id_list)
    else:
        goods_info.mark_id=str(member_info.id)
    #申领量加一
    goods_info.status=2
    goods_info.tap_count = goods_info.tap_count + 1
    goods_info.updated_time = getCurrentDate()
    db.session.add(goods_info)
    db.session.commit()

    #更新用户认领消息的id表
    member_mark_id = member_info.mark_id
    if goods_mark_id:
        member_mark_id_list = member_mark_id.split('#')
        member_mark_id_list.append(str(goods_info.id))
        member_info.mark_id = "#".join(member_mark_id_list)
    else:
        member_info.mark_id = str(goods_info.id)

    member_info.updated_time = getCurrentDate()
    db.session.add(member_info)
    db.session.commit()

    resp['data']['show_location']=True
    db.session.add(goods_info)
    db.session.commit()

    return jsonify(resp)

@route_api.route('/goods/info')
def goodsInfo():
    resp = {'code': 200, 'msg': 'operate successfully(get info)', 'data': {}}
    req = request.values

    id = int(req['id']) if ('id' in req and req['id']) else 0
    goods_info=Good.query.filter_by(id=id).first()
    if not goods_info:
        resp['code']=-1
        resp['msg']='没有找到相关商品信息'
        return jsonify(resp)

    member_info=g.member_info
    #用户能否看到地址,如果是在mark列表或者发布者可以看到地址和电话
    show_location=False
    mark_id=goods_info.mark_id
    if mark_id:
        mark_id_list=mark_id.split('#')
        if member_info.id in mark_id_list:
            show_location=True

    auther_info = Member.query.filter_by(id=goods_info.member_id).first()
    if not auther_info:
        resp['code'] = -1
        resp['msg'] = '没有找到相关发布者信息'
        return jsonify(resp)

    if member_info and (member_info.id == auther_info.id):
        is_auth = True
        show_location = True
    else:
        is_auth = False

    #浏览量加一
    goods_info.view_count = goods_info.view_count + 1
    resp['data']['info']={
        "id":goods_info.id,
        "goods_name":goods_info.name,
        "owner_name":goods_info.owner_name,
        "summary":goods_info.summary,
        "view_count":goods_info.view_count,
        "main_image":UrlManager.buildImageUrl(goods_info.main_image),
        "target_price":str(goods_info.target_price),
        "pics":[UrlManager.buildImageUrl(i) for i in goods_info.pics.split(",")],
        "updated_time": str(goods_info.updated_time),
        "location":goods_info.location,
        "business_type":goods_info.business_type,
        "mobile":goods_info.mobile,
        "status_desc": str(goods_info.status_desc),

        "auther_name": auther_info.nickname,
        "avatar": auther_info.avatar,
        "is_auth":is_auth
    }

    resp['data']['show_location']=show_location
    db.session.add(goods_info)
    db.session.commit()

    return jsonify(resp)

@route_api.route("/goods/report", methods=['GET', 'POST'])
def goodsReport():
    resp = {'code': 200, 'msg': '举报成功', 'data': {}}
    #获取商品id
    req = request.values

    member_info = g.member_info
    if not member_info:
        resp['code'] = -1
        resp['msg'] = '没有用户信息，无法完成举报！请到 “发布”中授权登录'
        return jsonify(resp)

    id=req['id'] if 'id' in req else 0
    if id==0:
        resp['msg']="数据获取失败"
        resp['req']=req
        return jsonify(resp)

    goods_info=Good.query.filter_by(id=id).with_for_update().first()
    if not goods_info or goods_info.status!=1:
        resp['code']=-1
        resp['msg']='没有找到商品信息'
        return jsonify(resp)

    goods_info.status = 3
    goods_info.updated_time = getCurrentDate()
    db.session.add(goods_info)
    db.session.commit()

    auther_info=Member.query.filter_by(id=goods_info.member_id).first()
    if not auther_info:
        resp['code'] = -1
        resp['msg'] = '没有找到相关发布者信息'
        return jsonify(resp)

    model_report=Report()
    model_report.status=3
    model_report.member_id =auther_info.id
    model_report.report_member_id = member_info.id
    model_report.goods_id = id
    model_report.updated_time = model_report.created_time=getCurrentDate()

    MemberService.updateCredits(member_info)
    db.session.add(model_report)
    db.session.commit()

    return jsonify(resp)

#编辑信息
@route_api.route("/goods/edit", methods=['GET', 'POST'])
def editGoods():
    resp = {'code': 200, 'msg': 'edit goods data successfully(goods/add)', 'data': {}}
    req = request.values

    member_info = g.member_info
    if not member_info:
        resp['code'] = -1
        resp['msg'] = '用户信息异常'
        return jsonify(resp)

    id=req['id'] if 'id' in req else 0
    if id==0:
        resp['code']=-1
        resp['msg']="数据上传失败"
        resp['data']=req
        return jsonify(resp)

    goods_info=Good.query.filter_by(id=id).first()
    if not goods_info:
        resp['code'] = -1
        resp['msg'] = "没有该条商品记录"
        resp['data'] = req
        return jsonify(resp)

    #清空图片列表，为后续的插入图片做准备
    #虽然是清空，但是不是使用列表，而是使用空字符串
    goods_info.pics=""
    goods_info.main_image=""

    business_type = req['business_type'] if 'business_type' in req else 5
    if business_type == 5:
        resp['code'] = -1
        resp['msg'] = "no business_type"
        resp['data'] = req
        return jsonify(resp)

    name = req["goods_name"] if 'goods_name' in req else ''
    if not name:
        resp['code'] = -1
        resp['msg'] = "上传数据失败"
        return jsonify(resp)

    goods_info.target_price = Decimal(req['target_price']).quantize(Decimal('0.00')) if 'target_price' in req else 0.00
    goods_info.name=name
    goods_info.owner_name=req['owner_name']
    goods_info.summary=req['summary']
    goods_info.location=req['location']
    goods_info.business_type=business_type
    goods_info.mobile=req['mobile']
    goods_info.updated_time=getCurrentDate()
    db.session.add(goods_info)
    db.session.commit()

    #通过链接发送之后的图片是逗号连起来的字符串
    img_list=req['img_list']
    img_list_status=UploadService.filterUpImages(img_list)
    resp['img_list_status']=img_list_status
    resp['id']=id
    return jsonify(resp)

@route_api.route("/goods/update-pics", methods=['GET', 'POST'])
def updatePics():
    resp = {'code': 200, 'msg': 'edit goods data successfully(goods/add)', 'data': {}}
    req = request.values

    member_info = g.member_info
    if not member_info:
        resp['code'] = -1
        resp['msg'] = '用户信息异常'
        return jsonify(resp)

    id = req['id'] if 'id' in req else 0
    if id == 0:
        resp['code'] = -1
        resp['msg'] = "can't get id"
        resp['data'] = req
        return jsonify(resp)

    img_url=req['img_url'] if 'img_url' in req else ''
    if not img_url:
        resp['code'] = -1
        resp['msg'] = "no img_url"
        resp['data'] = req
        return jsonify(resp)
    pic_url = UploadService.getImageUrl(img_url)

    goods_info = Good.query.filter_by(id=id).with_for_update().first()
    if not goods_info:
        resp['code'] = -1
        resp['msg'] = "没有该条记录"
        resp['data'] = req
        return jsonify(resp)

    if not goods_info.pics:
        pics_list=[]
    else:
        pics_list=goods_info.pics.split(",")

    pics_list.append(pic_url)
    goods_info.main_image=pics_list[0]
    goods_info.pics=",".join(pics_list)
    goods_info.updated_time= getCurrentDate()

    db.session.add(goods_info)
    db.session.commit()

    return jsonify(resp)