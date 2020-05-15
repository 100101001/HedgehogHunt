# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/4/24 下午6:43
@file: Adv.py
@desc:
"""
from common.models.ciwei.Member import Member
from common.models.ciwei.Adv import Adv
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



@route_api.route("/adv/create", methods=['GET', 'POST'])
def createAdvs():
    resp = {'code': 200, 'msg': '', 'data': {}}
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

    model_adv=Adv()
    model_adv.member_id=member_info.id
    model_adv.name=name
    model_adv.target_price=Decimal(req['target_price']).quantize(Decimal('0.00'))
    model_adv.location = req['location']

    #求购时设置原始价格为0
    model_adv.stock=req['stock']
    model_adv.summary=req['summary']
    model_adv.status=2
    model_adv.updated_time=model_adv.created_time=getCurrentDate()

    #判断uuid是否唯一，是否已经被使用过
    uuid_now=getUuid('ciwei_adv')

    record=Adv.query.filter_by(uu_id=uuid_now).first()
    if record:
        resp['code'] = -1
        resp['msg'] = "系统繁忙，请稍候重试"
        return jsonify(resp)
    #若不重复，则赋值
    model_adv.uu_id = uuid_now
    db.session.add(model_adv)
    db.session.commit()

    #按刚才的uuid查找刚才的记录
    record_just_now=Adv.query.filter_by(uu_id=uuid_now).first()
    resp['uuid'] = uuid_now
    if not record_just_now:
        resp['code'] = -1
        resp['msg'] = "系统繁忙，请稍候重试"
        resp['data'] = req
        return jsonify(resp)

    #返回商品记录的id，用于后续添加图片
    resp['id']=record_just_now.id
    #判断图片是否已经存在于网上
    img_list=req['img_list']
    img_list_status=UploadService.filterUpImages(img_list)
    resp['img_list_status'] = img_list_status
    return jsonify(resp)

@route_api.route("/adv/add-pics", methods=['GET', 'POST'])
def addAdvsPics():
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
    advs_info=Adv.query.filter_by(id=id).with_for_update().first()
    if not advs_info:
        resp['code'] = -1
        resp['msg'] = '没有找到相关商品信息'
        return jsonify(resp)

    if not advs_info.pics:
        pics_list=[]

    else:
        pics_list=advs_info.pics.split(",")

    pics_list.append(pic_url)
    advs_info.main_image=pics_list[0]
    advs_info.pics=",".join(pics_list)
    db.session.add(advs_info)
    db.session.commit()
    return jsonify(resp)

@route_api.route("/adv/end-create", methods=['GET', 'POST'])
def endAdvCreate():
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

    advs_info=Adv.query.filter_by(id=id).with_for_update().first()
    if not advs_info:
        resp['code'] = -1
        resp['msg'] = '没有找到相关商品信息'
        return jsonify(resp)

    advs_info.status=1
    advs_info.updated_time=getCurrentDate()
    db.session.add(advs_info)
    db.session.commit()

    return jsonify(resp)


@route_api.route("/adv/search",methods=['GET','POST'])
def advsSearch():
    resp={'code':200,'msg':'search successfully(search)','data':{}}
    req=request.values
    query=Adv.query.filter_by(status=1)

    #将对应的用户信息取出来，组合之后返回
    advs_list=query.order_by(Adv.id.desc())
    data_advs_list = []
    if advs_list:
        for item in advs_list:
            tmp_data = {
                "id": item.id,
                "main_image":UrlManager.buildImageUrl(item.main_image),
            }
            data_advs_list.append(tmp_data)

    resp['data']['list']=data_advs_list
    return jsonify(resp)

@route_api.route('/adv/info')
def advsInfo():
    resp = {'code': 200, 'msg': 'operate successfully(get info)', 'data': {}}
    req = request.values

    id = int(req['id']) if ('id' in req and req['id']) else 0
    advs_info=Adv.query.filter_by(id=id).first()
    if not advs_info or advs_info.status!=1:
        resp['code']=-1
        resp['msg']='没有找到相关商品信息'
        return jsonify(resp)
    member_info=g.member_info

    auther_info=Member.query.filter_by(id=advs_info.member_id).first()
    #浏览量加一
    advs_info.view_count = advs_info.view_count + 1
    resp['data']['info']={
        "id":advs_info.id,
        "goods_name":advs_info.name,
        "summary":advs_info.summary,
        "view_count":advs_info.view_count,
        "main_image":UrlManager.buildImageUrl(advs_info.main_image),
        "target_price":str(advs_info.target_price),
        "stock":advs_info.stock,
        "pics":[UrlManager.buildImageUrl(i) for i in advs_info.pics.split(",")],
        "updated_time": str(advs_info.updated_time),
        "location":advs_info.location,
        "qr_code_list":[UrlManager.buildImageUrl(advs_info.qr_code)],

        "auther_name": auther_info.nickname,
        "avatar": auther_info.avatar,
    }

    db.session.add(advs_info)
    db.session.commit()
    return jsonify(resp)

#编辑信息
@route_api.route("/adv/edit", methods=['GET', 'POST'])
def editAdvs():
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

    advs_info=Adv.query.filter_by(id=id).first()
    if not advs_info:
        resp['code'] = -1
        resp['msg'] = "没有该条商品记录"
        resp['data'] = req
        return jsonify(resp)

    #清空图片列表，为后续的插入图片做准备
    #虽然是清空，但是不是使用列表，而是使用空字符串
    advs_info.pics=""
    advs_info.main_image=""
    advs_info.target_price = Decimal(req['target_price']).quantize(Decimal('0.00'))
    advs_info.name = req['goods_name']
    advs_info.stock = req['stock']
    advs_info.summary = req['summary']
    advs_info.location = req['location']
    advs_info.status = 2
    advs_info.updated_time = getCurrentDate()

    db.session.add(advs_info)
    db.session.commit()

    #通过链接发送之后的图片是逗号连起来的字符串
    img_list=req['img_list']
    img_list_status=UploadService.filterUpImages(img_list)
    resp['img_list_status']=img_list_status
    resp['id']=id

    return jsonify(resp)

@route_api.route("/adv/update-pics", methods=['GET', 'POST'])
def updateAdvPics():
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

    advs_info = Adv.query.filter_by(id=id).with_for_update().first()
    if not advs_info:
        resp['code'] = -1
        resp['msg'] = "没有该条记录"
        resp['data'] = req
        return jsonify(resp)

    if not advs_info.pics:
        pics_list=[]
    else:
        pics_list=advs_info.pics.split(",")

    pics_list.append(pic_url)
    advs_info.main_image=pics_list[0]
    advs_info.pics=",".join(pics_list)
    advs_info.updated_time= getCurrentDate()

    db.session.add(advs_info)
    db.session.commit()

    return jsonify(resp)

@route_api.route("/adv/add-qrcode", methods=['GET', 'POST'])
def addAdvQrcode():
    resp = {'code':200,'state': 'add qrcode success','data':{}}

    req = request.values
    id = req['id'] if 'id' in req else 0
    if id == 0:
        resp['code'] = -1
        resp['msg'] = "can't get id"
        resp['data'] = req
        return jsonify(resp)

    advs_info = Adv.query.filter_by(id=id).with_for_update().first()

    member_info = g.member_info
    if not member_info:
        resp['code'] = -1
        resp['msg'] = "用户信息异常"
        return jsonify(resp)
    #是否修改了二维码
    images_target = request.files
    image = images_target['file'] if 'file' in images_target else None

    if image is None:
        resp['code'] = -1
        resp['msg'] = "图片上传失败"
        resp['state'] = '上传失败'
        return jsonify(resp)

    ret = UploadService.uploadByFile(image)
    if ret['code'] != 200:
        resp['code'] = -1
        resp['msg'] = "图片上传失败"
        resp['state'] = "上传失败" + ret['msg']
        return jsonify(resp)

    #将返回的本地链接加到列表，并且保存为字符串
    pic_url=ret['data']['file_key']
    advs_info.qr_code = pic_url
    advs_info.updated_time=getCurrentDate()
    db.session.add(advs_info)
    db.session.commit()
    resp['msg'] = "change qr_code successfully"
    return jsonify(resp)

@route_api.route("/adv/delete",methods=['GET','POST'])
def advDelete():
    resp={'code':200,'msg':'search record successfully(search)','data':{}}
    req=request.values

    member_info = g.member_info
    if not member_info:
        resp['code'] = -1
        resp['msg'] = "没有相关用户信息"
        return jsonify(resp)

    id=req['id'] if 'id' in req else 0
    advs_info = Adv.query.filter_by(id=id).first()
    if not advs_info:
        resp['code'] = -1
        resp['msg'] = '没有找到该条记录'
        return jsonify(resp)
    advs_info.updated_time=getCurrentDate()

    if advs_info.status==1:
        advs_info.status=0

    db.session.add(advs_info)
    db.session.commit()
    return jsonify(resp)