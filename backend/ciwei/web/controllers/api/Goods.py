#!/usr/bin/python3.6.8
#Editor weichaoxu

# -*- coding:utf-8 -*-
from common.models.ciwei.Member import Member
from common.models.ciwei.Goods import Good
from common.models.ciwei.Thanks import Thank
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

    # 商品地址,同时保存有经纬度
    location=req["location"]
    model_goods.location="###".join(location.split(","))
    model_goods.owner_name=req['owner_name']
    model_goods.summary=req['summary']
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

    #如果是直接归还商品，则会带上寻物启事或者物主的id
    auther_id=req['auther_id'] if 'auther_id' in req else 0
    if auther_id:
        auther_info=Member.query.filter_by(id=auther_id).first()
        MemberService.addRecommendGoods(auther_info,goods_info.id)

    target_goods_id=req['target_goods_id'] if 'target_goods_id' in req else 0
    if target_goods_id:
        target_goods_info=Good.query.filter_by(id=target_goods_id).first()
        if target_goods_info:
            target_goods_info.status = 2
            # db.session.add(target_goods_info)
            db.session.commit()

    #创建或者修改完成时，对用户进行推荐
    MemberService.recommendGoods(goods_info)
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
    query=query.filter(Good.report_status!=2)
    query=query.filter(Good.report_status!=3)
    query=query.filter(Good.report_status!=5)

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
        if  str(member_info.id) not in goods_mark_id:
            goods_info.mark_id=goods_info.mark_id+"#"+str(member_info.id)
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
    if member_mark_id:
        member_mark_id_list = member_mark_id.split('#')
        if str(member_info.id) not in member_mark_id_list:
            member_info.mark_id =member_mark_id+ "#"+str(goods_info.id)
    else:
        member_info.mark_id = str(goods_info.id)

    member_info.updated_time = getCurrentDate()
    db.session.add(member_info)
    db.session.commit()

    resp['data']['show_location']=True
    resp['data']['status']=goods_info.status
    resp['data']['status_desc']=goods_info.status_desc
    db.session.add(goods_info)
    db.session.commit()

    return jsonify(resp)

@route_api.route('/goods/gotback')
def goodsGotback():
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
    goods_owner_id=goods_info.owner_id
    if goods_owner_id:
        goods_owner_id_list=goods_owner_id.split('#')
        if  str(member_info.id) not in goods_owner_id_list:
            goods_info.owner_id=goods_info.owner_id+"#"+str(member_info.id)
    else:
        goods_info.owner_id=str(member_info.id)
    #申领量加一
    goods_info.status=3
    goods_info.tap_count = goods_info.tap_count + 1
    goods_info.updated_time = getCurrentDate()
    db.session.add(goods_info)
    db.session.commit()

    #更新用户认领消息的id表
    member_gotback_id = member_info.gotback_id
    if member_gotback_id:
        member_info.gotback_id =member_gotback_id+ "#"+str(goods_info.id)
    else:
        member_info.gotback_id = str(goods_info.id)

    member_info.updated_time = getCurrentDate()
    db.session.add(member_info)
    db.session.commit()

    resp['data']['show_location']=True
    resp['data']['status']=goods_info.status
    resp['data']['status_desc']=goods_info.status_desc
    db.session.add(goods_info)
    db.session.commit()

    return jsonify(resp)

@route_api.route('/goods/info')
def goodsInfo():
    resp = {'code': 200, 'msg': 'operate successfully(get info)', 'data': {}}
    req = request.values

    #按id获取goods记录
    id = int(req['id']) if ('id' in req and req['id']) else 0
    goods_info=Good.query.filter_by(id=id).first()
    if not goods_info:
        resp['code']=-1
        resp['msg']='没有找到相关商品信息'
        return jsonify(resp)

    #获取已登陆用户的信息
    member_info=g.member_info
    #用户能否看到地址,如果是在mark列表或者发布者可以看到地址和电话
    show_location=False

    #查看详情的用户已认领了该物品,显示地址
    if member_info and member_info.mark_id:
        mark_goods_id = member_info.mark_id
        mark_id_list=mark_goods_id.split('#')
        if str(goods_info.id) in mark_id_list:
            show_location=True

    #用户查看了被系统推荐的物品,将推荐状态从0更新为1
    if member_info and member_info.recommend_id:
        recommend_id_list=MemberService.getRecommendDict(member_info.recommend_id,False)
        if id in recommend_id_list.keys() and recommend_id_list[id]==0:
            recommend_id_list[id]=1
        member_info.recommend_id=MemberService.joinRecommendDict(recommend_id_list)

    #获取物品发布者
    auther_info = Member.query.filter_by(id=goods_info.member_id).first()
    if not auther_info:
        resp['code'] = -1
        resp['msg'] = '没有找到相关发布者信息'
        return jsonify(resp)

    #如果作者查看详情,可以编辑和看到地址
    if member_info and (member_info.id == auther_info.id):
        is_auth = True
        show_location = True
    else:
        is_auth = False

    #处理地址
    #例：上海市徐汇区肇嘉浜路1111号###美罗城###31.192948153###121.439673735
    location_list=goods_info.location.split("###")
    location_list[2]=eval(location_list[2])
    location_list[3]=eval(location_list[3])
    #浏览量加一(同一次登陆会话看多少次应都只算一次浏览)
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
        "location":location_list,
        "business_type":goods_info.business_type,
        "mobile":goods_info.mobile,
        "status_desc": str(goods_info.status_desc),
        "status":goods_info.status,

        "auther_id":auther_info.id,
        "auther_name": auther_info.nickname,
        "avatar": auther_info.avatar,
        "is_auth":is_auth
    }

    resp['data']['show_location']=show_location
    # db.session.add(goods_info)
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
        resp['msg'] = '没有用户信息，无法完成举报！请授权登录'
        return jsonify(resp)

    id=req['id'] if 'id' in req else 0
    if id==0:
        resp['code'] = -1
        resp['msg']="数据获取失败"
        resp['req']=req
        return jsonify(resp)

    report_info=Report.query.filter_by(record_id=id).first()
    if report_info:
        resp['code'] = -1
        resp['msg'] = "该条信息已被举报过，管理员处理中"
        return jsonify(resp)

    record_type=int(req['record_type']) if 'record_type' in req else "nonono"
    if record_type==1:
        #物品信息违规
        record_info=Good.query.filter_by(id=id).with_for_update().first()
    elif record_type==0:
        # 答谢信息违规
        record_info=Thank.query.filter_by(id=id).with_for_update().first()
    else:
        resp['code'] = -1
        resp['msg'] = '获取信息错误'
        return jsonify(resp)

    if not record_info:
        resp['code']=-1
        resp['msg']='没有找到商品信息'
        return jsonify(resp)

    record_info.report_status = 1
    record_info.updated_time = getCurrentDate()
    #db.session.add(record_info)
    db.session.commit()

    model_report=Report()
    model_report.status=1
    model_report.member_id =record_info.member_id
    model_report.report_member_id = member_info.id
    model_report.record_id = id
    model_report.record_type = record_type
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

    #位置信息
    location=req['location'].split(",")
    goods_info.location="###".join(location)

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