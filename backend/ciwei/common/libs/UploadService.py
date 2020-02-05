#!/usr/bin/python3.6.8

# -*- coding:utf-8 -*-
from werkzeug.utils import secure_filename
from application import app,db
from common.libs.Helper import getCurrentDate
import os,stat,uuid
from common.models.ciwei.Image import Image

class UploadService():
    @staticmethod
    def uploadByFile(file):
        """
        1.把文件保存到 web/static/upload/日期目录下
        2.db新增图片
        :param file:图片文件
        :return: 图片在服务器上的路径
        """
        config_upload = app.config['UPLOAD']
        resp={'code':200,'msg':'upload image success','data':{}}

        # 检查文件是图片
        # 保存文件到web/static/upload/日期目录下,文件名uuid
        # db 新增图片
        filename=secure_filename(file.filename)
        ext=filename.split('.')[-1]
        if ext not in config_upload['ext']:
            resp['msg']='not allowed ext file'+":::"+filename
            resp['code']=-1
            return resp

        root_path=app.root_path+config_upload['prefix_path']
        file_dir=getCurrentDate("%Y%m%d")
        save_dir=root_path+file_dir

        if not os.path.exists(save_dir):
            os.mkdir(save_dir)
            #赋予操作者文件夹的777权限
            os.chmod(save_dir, stat.S_IRWXU | stat.S_IRGRP | stat.S_IRWXO)

        file_name=str(uuid.uuid4()).replace("-","")+'.'+ext
        file.save("{0}/{1}".format(save_dir,file_name))

        model_image=Image()
        model_image.file_key=file_dir+"/"+file_name
        model_image.created_time=getCurrentDate()

        db.session.add(model_image)
        db.session.commit()

        resp['data']={
            'file_key':file_dir+'/'+file_name,
        }
        return resp

    @staticmethod
    def filterUpImages(img_list_raw):

        # 网络会转换成字符串传输
        img_list=img_list_raw.split(",")
        app_config = app.config
        image_root = app_config['APP']['domain'] + app_config['UPLOAD']['prefix_url']

        img_list_status = []
        for i in img_list:
            if image_root in i:
                img_list_status.append(1)
            else:
                img_list_status.append(0)

        return img_list_status

    @staticmethod
    def getImageUrl(img_path):
        app_config = app.config
        image_root = app_config['APP']['domain'] + app_config['UPLOAD']['prefix_url']

        return img_path.replace(image_root,"")
