#!/usr/bin/python3.6.8
#Editor weichaoxu

# -*- coding:utf-8 -*-
from web.controllers.api import route_api
from flask import request,jsonify,g
from common.libs.UrlManager import UrlManager
from common.libs.UploadService import UploadService

@route_api.route("/upload/image",methods=['GET','POST'])
def uploadImage():
    resp={'code':200,'state':'success'}
    images_target=request.files
    image=images_target['file'] if 'file' in images_target else None

    if image is None:
        resp['code']=-1
        resp['msg']='图片上传失败'
        resp['state']='上传失败'
        return jsonify(resp)

    ret=UploadService.uploadByFile(image)
    if ret['code']!=200:
        resp['code'] = -1
        resp['msg'] = '图片上传失败'
        resp['state']="上传失败"+ret['msg']
        return jsonify(resp)

    resp['url']=UrlManager.buildImageUrl(ret['data']['file_key'])

    return jsonify(resp)
