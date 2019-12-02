#!/usr/bin/python3.6.8
#Editor weichaoxu

# -*- coding:utf-8 -*-
from common.models.ciwei.Member import Member
from common.models.ciwei.Goods import Good
from common.models.ciwei.User import User
from common.models.ciwei.Feedback import Feedback
from common.libs.Helper import getUuid
from common.libs.UploadService import UploadService
from web.controllers.api import route_api
from flask import request,jsonify,g
from application import app,db
from common.libs.Helper import getCurrentDate
from common.libs.UrlManager import UrlManager
from sqlalchemy import or_
from common.libs.Helper import selectFilterObj,getDictFilterField
from common.libs.MemberService import MemberService

@route_api.route("/feedback/create", methods=['GET', 'POST'])
def createFeedback():
    resp = {'code': 200, 'msg': 'create feedback data successfully(goods/add)', 'data': {}}
    req = request.values

    member_info = g.member_info
    if not member_info:
        resp['code'] = -1
        resp['msg'] = "用户信息异常"
        return jsonify(resp)

    summary = req["summary"] if 'summary' in req else ''
    if not summary:
        resp['code'] = -1
        resp['msg'] = "数据上传失败"
        resp['data'] = req
        return jsonify(resp)

    model_feedback=Feedback()
    model_feedback.summary=summary
    #判断uuid是否唯一，是否已经被使用过
    uuid_now=getUuid()
    record=Feedback.query.filter_by(uu_id=uuid_now).first()
    if record:
        resp['code'] = -1
        resp['msg'] = "系统繁忙，请稍候重试"
        # resp['msg'] = "tow same uuid"
        resp['data'] = req
        return jsonify(resp)
    #若不重复，则赋值
    model_feedback.uu_id = uuid_now
    model_feedback.created_time=model_feedback.updated_time=getCurrentDate()
    model_feedback.member_id=member_info.id
    model_feedback.status=2
    db.session.add(model_feedback)
    db.session.commit()

    #按刚才的uuid查找刚才的记录
    record_just_now=Feedback.query.filter_by(uu_id=uuid_now).first()
    resp['uuid'] = uuid_now
    if not record_just_now:
        resp['code'] = -1
        resp['msg'] = "没有找到记录"
        # resp['msg'] = "can't find record"
        resp['data'] = req
        return jsonify(resp)

    # 反馈成功，用户积分涨5
    MemberService.updateCredits(member_info)
    resp['id']=record_just_now.id
    return jsonify(resp)

@route_api.route("/feedback/add-pics", methods=['GET', 'POST'])
def addFeedbackPics():
    resp = {'state': 'add pics success'}

    #获取商品id
    req = request.values

    member_info = g.member_info
    if not member_info:
        resp['code'] = -1
        resp['msg'] = "用户信息异常"
        return jsonify(resp)

    id=req['id'] if 'id' in req else 0
    if id==0:
        resp['msg']="cant't get id"
        resp['req']=req
        return jsonify(resp)

    images_target = request.files
    image = images_target['file'] if 'file' in images_target else None
    if image is None:
        resp['code']=-1
        resp['msg']='图片上传失败！'
        resp['state'] = '上传失败'
        return jsonify(resp)

    ret = UploadService.uploadByFile(image)
    if ret['code'] != 200:
        resp['code'] = -1
        resp['msg'] = '图片上传失败！'
        resp['state'] = "上传失败" + ret['msg']
        return jsonify(resp)

    #将返回的本地链接加到列表，并且保存为字符串
    pic_url=ret['data']['file_key']
    feedback_info=Feedback.query.filter_by(id=id).with_for_update().first()
    if not feedback_info:
        resp['code'] = -1
        resp['msg'] = '没有相关反馈记录'
        return jsonify(resp)

    if not feedback_info.pics:
        pics_list=[]
    else:
        pics_list=feedback_info.pics.split(",")

    pics_list.append(pic_url)
    feedback_info.main_image=pics_list[0]
    feedback_info.pics=",".join(pics_list)
    db.session.add(feedback_info)
    db.session.commit()
    return jsonify(resp)

@route_api.route("/feedback/end-create", methods=['GET', 'POST'])
def endFeedbackCreate():
    resp = {'code':200,'msg': 'create goods success','data':{}}
    #获取反馈id
    req = request.values

    member_info = g.member_info
    if not member_info:
        resp['code'] = -1
        resp['msg'] = "用户信息异常"
        return jsonify(resp)

    id=req['id'] if 'id' in req else 0
    if id==0:
        resp['msg']="cant't get id"
        resp['req']=req
        return jsonify(resp)

    feedback_info=Feedback.query.filter_by(id=id).with_for_update().first()
    if not feedback_info:
        resp['code'] = -1
        resp['msg'] = '没有相关反馈记录'
        return jsonify(resp)
    feedback_info.status=1
    feedback_info.updated_time=getCurrentDate()
    db.session.add(feedback_info)
    db.session.commit()

    return jsonify(resp)

#查询所有举报信息
@route_api.route("/feedback/search",methods=['GET','POST'])
def feedbacksSearch():
    resp={'code':200,'msg':'search record successfully(search)','data':{}}
    req=request.values

    member_info = g.member_info
    if not member_info:
        resp['code'] = -1
        resp['msg'] = "用户信息异常"
        return jsonify(resp)

    p=int(req['p']) if ('p' in req and req['p']) else 1
    if p<1:
        p=1
    page_size=10
    offset=(p-1)*page_size

    status=int(req['status']) if 'status' in req else "nonono"
    if status=="nonono":
        resp['code'] = -1
        resp['msg'] = '状态参数传递出错'
        return jsonify(resp)
    query=Feedback.query.filter_by(status=status)
    feedback_list = query.order_by(Feedback.updated_time.desc()).offset(offset).limit(10).all()
    data_feedback_list = []
    if feedback_list:
        for item in feedback_list:
            tmp_data = {
                "id": item.id,
                "created_time": str(item.created_time),
                "updated_time": str(item.updated_time),
                "main_image": UrlManager.buildImageUrl(item.main_image),
                "status": item.status,
                "summary":item.summary,
            }
            # 如果已经被处理过
            data_feedback_list.append(tmp_data)

    resp['data']['list']=data_feedback_list
    resp['data']['has_more']=0 if len(data_feedback_list)<page_size else 1
    return jsonify(resp)

#查看举报详情
@route_api.route('/feedback/info')
def feedbackInfo():
    resp = {'code': 200, 'msg': 'operate successfully(get info)', 'data': {}}
    req = request.values

    member_info = g.member_info
    if not member_info:
        resp['code'] = -1
        resp['msg'] = "用户信息异常"
        return jsonify(resp)

    id = int(req['id']) if ('id' in req and req['id']) else 0

    feedback_info=Feedback.query.filter_by(id=id).first()
    if not feedback_info:
        resp['code']=-1
        resp['msg']='没有找到反馈信息'
        return jsonify(resp)

    auther_info=Member.query.filter_by(id=feedback_info.member_id).first()
    if not auther_info:
        resp['code'] = -1
        resp['msg'] = '没有找到发布者信息'
        return jsonify(resp)

    resp['data']['info']={
        "summary":feedback_info.summary,
        "pics": [UrlManager.buildImageUrl(i) for i in feedback_info.pics.split(",")],
        "created_time": str(feedback_info.created_time),
        "updated_time": str(feedback_info.updated_time),
        #用户信息
        "member_id":auther_info.id,
        "auther_name": auther_info.nickname,
        "avatar": auther_info.avatar,
        "feedback_id":feedback_info.id
    }

    #1是还没读，0是已经看过了
    if feedback_info.status==1:
        feedback_info.status=0

    db.session.add(feedback_info)
    db.session.commit()
    return jsonify(resp)


# 拉黑发布者或者举报者
@route_api.route('/feedback/block')
def feedbackBlock():
    resp = {'code': 200, 'msg': 'operate successfully(get info)', 'data': {}}
    req = request.values

    member_info = g.member_info
    if not member_info:
        resp['code'] = -1
        resp['msg'] = "用户信息异常"
        return jsonify(resp)

    select_member_id = int(req['select_member_id']) if ('select_member_id' in req and req['select_member_id']) else 0
    feedback_id = int(req['feedback_id']) if ('feedback_id' in req and req['feedback_id']) else 0
    # 获取管理员信息
    member_info = g.member_info
    if not auther_info:
        resp['code'] = -1
        resp['msg'] = '用户信息正常'
        return jsonify(resp)

    user_info = User.query.filter_by(member_id=member_info.id).first()
    if not user_info:
        resp['code'] = -1
        resp['msg'] = "没有管理员信息"
        resp['data'] = str(member_info.id) + "+" + member_info.name
        return jsonify(resp)

    feedback_info=Feedback.query.filter_by(id=feedback_id).first()
    if not feedback_info:
        resp['code'] = -1
        resp['msg'] = "没有反馈信息"
        return jsonify(resp)

    # 将报告信息及商品信息保存
    feedback_info.user_id = user_info.uid
    feedback_info.updated_time = getCurrentDate()
    db.session.add(feedback_info)
    db.session.commit()

    select_member_info = Member.query.filter_by(id=select_member_id).first()
    if not select_member_info:
        resp['code'] = -1
        resp['msg'] = "没有用户信息"
        return jsonify(resp)

    select_member_info.status = 0
    select_member_info.updated_time = getCurrentDate()

    # 该用户下正常的账户
    goods_list = Good.query.filter(Good.member_id == select_member_id, Good.status == 1).all()
    for item in goods_list:
        item.status = 8
        item.updated_time = getCurrentDate()
        db.session.add(item)
        db.session.commit()

    db.session.add(select_member_info)
    db.session.commit()

    return jsonify(resp)