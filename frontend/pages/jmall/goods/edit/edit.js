var app = getApp();
Page({
        data: {
            radio_checked: true,
            loadingHidden: true,
            tips_obj: {
                "goods_name": "商品名称",
                "original_price": "原价",
                "target_price": "出手价",
                "location": "地址",
                "stock": "库存",
                "summary": "描述",
            },

        },
        onLoad: function (options) {
            var info = app.globalData.info;
            this.onLoadSetData(info);
        },
        onShow: function () {
        },
        onLoadSetData: function (info) {
            var business_type = info.business_type;
            if (business_type === 1) {
                var items = [
                    {
                        name: "goods_name",
                        placeholder: "耳机",
                        label: "商品名称",
                        icons: "/images/icons/goods_name.png",
                        value: info.goods_name,

                    },
                    {
                        name: "original_price",
                        placeholder: "0.00",
                        label: "原价",
                        value: info.original_price,
                        icons: "/images/icons/original_price.png",
                        kb_type: "digit",
                    },
                    {
                        name: "target_price",
                        placeholder: "0.00",
                        label: "出手价",
                        value: info.target_price,
                        icons: "/images/icons/discount_price.png",
                        kb_type: "digit",
                    },
                    {
                        name: "stock",
                        placeholder: "1",
                        value: info.stock,
                        label: "库存",
                        kb_type: "number",
                        icons: "/images/icons/stock.png",
                    },
                    {
                        name: "location",
                        placeholder: "同济大学四平校区",
                        value: info.location,
                        label: "地址",
                        icons: "/images/icons/location.png",
                    }
                ];
                var tips_obj = {
                    "goods_name": "商品名称",
                    "target_price": "出价",
                    "location": "地址",
                    "stock": "数量",
                    "summary": "描述",
                };
            } else {
                var items = [
                    {
                        name: "goods_name",
                        placeholder: "耳机",
                        value: info.goods_name,
                        label: "商品名称",
                        icons: "/images/icons/goods_name.png",
                    },
                    {
                        name: "target_price",
                        placeholder: "0.00",
                        label: "出价",
                        value: info.target_price,
                        kb_type: "digit",
                        icons: "/images/icons/original_price.png",
                    },
                    {
                        name: "stock",
                        placeholder: "1",
                        value: info.stock,
                        label: "数量",
                        kb_type: "number",
                        icons: "/images/icons/stock.png",
                    },
                    {
                        name: "location",
                        placeholder: "同济大学四平校区",
                        value: info.location,
                        label: "地址",
                        icons: "/images/icons/location.png",
                    }
                ];
                var tips_obj = {
                    "goods_name": "商品名称",
                    "original_price": "原价",
                    "target_price": "出手价",
                    "location": "地址",
                    "stock": "库存",
                    "summary": "描述",
                };
            }
            var summary_placeholder = "添加描述：品牌型号，成色要求等...";
            var imglist = info.pics;
            var objectArray = app.globalData.objectArray;
            var name_array = [];
            for (var i in objectArray) {
                name_array.push(objectArray[i].name);
            }
            this.setData({
                imglist: imglist,
                count: imglist.length,
                pic_status: true,
                cat_id: info.cat_id,
                loadingHidden: true,
                business_type: info.business_type,
                items: items,
                summary_placeholder: summary_placeholder,
                show_qr_code: true,
                qr_code_list: info.qr_code_list,
                change_qrcode: false,
                objectArray: objectArray,
                array: name_array,
                summary_value: info.summary,
                tips_obj: tips_obj,
                show_type_radio: false,
                index: info.cat_id,
                //商品id
                goods_id: info.id,
                picker_tips: "",
            });
        },
        //预览图片
        previewImage: function (e) {
            var current = e.target.dataset.src;
            wx.previewImage({
                current: current, // 当前显示图片的http链接
                urls: this.data.imglist // 需要预览的图片http链接列表
            })
        },
        //选择图片方法
        chooseLoadPics: function (e) {
            var that = this; //获取上下文
            var imglist = that.data.imglist;
            //选择图片
            wx.chooseImage({
                count: 8 - imglist.length,
                sizeType: ['compressed'],
                sourceType: ['album', 'camera'],
                success: function (res) {
                    var tempFiles_ori = res.tempFiles;
                    var imglist = that.data.imglist;

                    imglist = app.addImages(tempFiles_ori, imglist);
                    //显示
                    that.setData({
                        imglist: imglist,
                    });
                    if (imglist.length >= 9) {
                        that.setData({
                            pic_status: false,
                        });
                    } else {
                        that.setData({
                            pic_status: true,
                        });
                    }
                }
            })
        },
        // 删除图片
        deleteImg: function (e) {
            let index = e.currentTarget.dataset.index;
            let imglist = this.data.imglist;
            if (imglist.length === 1) {
                app.alert({'content': "删除失败，至少要提交一张图片"});
            } else {
                imglist.splice(index, 1);
                this.setData({
                    imglist: imglist
                });
                if (imglist.length < 9) {
                    this.setData({
                        pic_status: true,
                    });
                }
            }
        },
        //表单提交
        formSubmit: function (e) {
            var data = e.detail.value;
            app.globalData.location = data['location'];
          var qr_code_list = this.data.qr_code_list;
          if (qr_code_list.length === 0) {
            app.alert({ 'content': "请添加用于联系的微信二维码" });
            return;
          }
            app.globalData.qr_code_list = this.data.qr_code_list;
            app.globalData.business_type = this.data.business_type;
            var tips_obj = this.data.tips_obj;
            var is_empty = app.judgeEmpty(data, tips_obj);
            if (is_empty) {
                return;
            }
            var business_type = this.data.business_type;
            data['business_type'] = business_type;
            if (business_type == 0) {
                data['original_price'] = 0
            }
            data['cat_id'] = this.data.cat_id;
            data['type_name'] = this.data.objectArray[this.data.cat_id].name;
            var img_list = this.data.imglist;
            if (img_list.length === 0) {
                app.alert({'content': "至少要提交一张图片"});
                return;
            }
            data['img_list'] = img_list;
            data['id'] = this.data.goods_id;
            var url = "/goods/edit";
            this.uploadData(data, url, img_list);
        },
        //上传文件
        uploadData: function (data, url, img_list) {
            var that = this;
            wx.request({
                url: app.buildUrl(url),
                method: 'POST',
                header: app.getRequestHeader(),
                data: data,
                success: function (res) {
                    var resp = res.data;
                    if (resp.code !== 200) {
                        app.alert({'content': resp.msg});
                        return
                    }
                    //获取商品的id,之后用于提交图片
                    var id = resp.id;
                    var img_list_status = resp.img_list_status;
                    that.updateQrCode(id, img_list, img_list_status);
                },
                fail: function (res) {
                    app.serverBusy();
                    return;
                },
                complete: function (res) {
                    that.setData({
                        loadingHidden: true
                    });
                },

            });
        },
        updateQrCode: function (id, img_list, img_list_status) {
            var that = this;
            if (this.data.change_qrcode) {
                this.setData({
                    loadingHidden: false,
                    upload_qrcode: true
                });
                var qr_code_list = this.data.qr_code_list;
                wx.uploadFile({
                    url: app.buildUrl("/member/add-qrcode"), //接口地址
                    filePath: qr_code_list[0],//文件路径
                    header: app.getRequestHeader(),
                    formData: {
                        'id': id,
                    },
                    name: 'file',//文件名，不要修改，Flask直接读取
                    success: function (res) {
                        // var resp = res.data;
                        // if (resp.code !== 200) {
                        //     app.alert({'content': resp.msg});
                        //     return;
                        // }
                        //app.globalData.qr_code_list = res.data.data.qr_code_list;
                        that.uploadImage(id, img_list, img_list_status);
                    },
                    fail: function (res) {
                        app.serverBusy();
                        return;
                    },
                    complete: function (res) {
                        that.setData({
                            loadingHidden: true,
                            upload_qrcode: false,
                        });
                    },
                })
            } else {
                that.uploadImage(id, img_list, img_list_status);
            }
        },
        uploadImage: function (id, img_list, img_list_status) {
            var that = this;
            var n = img_list.length;
            for (var i = 1; i <= n; i++) {
                if (n === i) {
                    var end_s = true;
                }
                this.setData({
                    i: i,
                    loadingHidden: false,
                });
                if (img_list_status[i - 1]) {
                    //图片存在，则更新
                    wx.request({
                        url: app.buildUrl('/goods/update-pics'),
                        method: 'POST',
                        header: app.getRequestHeader(),
                        data: {
                            id: id,
                            img_url: img_list[i - 1]
                        },
                        success: function (res) {
                            // var resp = res.data;
                            // if (resp.code !== 200) {
                            //     app.alert({'content': resp.msg});
                            //     return;
                            // }
                            if (end_s) {
                                that.endCreate(id);
                            }
                        },
                        fail: function (res) {
                            app.serverBusy();
                            return;
                        },
                        complete: function (res) {
                            that.setData({
                                loadingHidden: true
                            });
                        },
                    })
                } else {
                    //图片不存在存在，则重新上传
                    wx.uploadFile({
                        url: app.buildUrl('/goods/add-pics'), //接口地址
                        header: app.getRequestHeader(),
                        filePath: img_list[i - 1],//文件路径
                        formData: {'id': id},
                        name: 'file',//文件名，不要修改，Flask直接读取
                        success: function (res) {
                            // var resp = res.data;
                            // if (resp.code !== 200) {
                            //     app.alert({'content': resp.msg});
                            //     return;
                            // }
                            if (end_s) {
                                that.endCreate(id);
                            }
                        },
                        fail: function (res) {
                            app.serverBusy();
                            return;
                        },
                        complete: function (res) {
                            that.setData({
                                loadingHidden: true
                            });
                        },
                    })
                }
            }

        },
        endCreate: function (id) {
            var that = this;
            wx.request({
                url: app.buildUrl("/goods/end-create"),
                method: 'POST',
                header: app.getRequestHeader(),
                data: {id: id},
                success: function (res) {
                    var resp = res.data;
                    if (resp.code !== 200) {
                        app.alert({'content': resp.msg});
                        return
                    }
                    wx.showToast({
                        title: '提交成功',
                        icon: 'success',
                        duration: 2000
                    });
                    wx.switchTab({
                        url: '/pages/jmall/goods/index',
                    });
                },
                fail: function (res) {
                    app.serverBusy();
                    return;
                },
                complete: function (res) {
                    that.setData({
                        loadingHidden: true,
                    });
                },
            });
        },
        //选择器
        bindPickerChange: function (e) {
            var index = e.detail.value;
            this.setData({
                index: index,
                picker_tips: "",
                cat_id: index
            })
        }
        ,
        //预览二维码
        previewQrCodeImage: function (e) {
            var current = e.target.dataset.src;
            var qr_code_list = this.data.qr_code_list;
            wx.previewImage({
                current: current, // 当前显示图片的http链接
                urls: qr_code_list // 需要预览的图片http链接列表
            })
        }
        ,
        //选择二维码方法
        chooseQrcode: function (e) {
            var that = this; //获取上下文
            //选择图片
            var qr_code_list = this.data.qr_code_list;
            if (qr_code_list.length > 0) {
                wx.showModal({
                    title: '提示',
                    content: "如需更新，请删除原文件再上传",
                })
            } else {
                wx.chooseImage({
                    count: 1,
                    sizeType: ['compressed'],
                    sourceType: ['album'],
                    success: function (res) {
                        var tempFiles = res.tempFiles;
                        var qr_code_list = [];
                        qr_code_list.push(tempFiles[0].path);
                        console.log(tempFiles[0].path);
                        console.log(qr_code_list[0]);
                        //显示
                        that.setData({
                            qr_code_list: qr_code_list,
                            show_qr_code: true,
                            change_qrcode: true,
                        });
                    }
                })
            }
        }
        ,
        // 删除二维码
        deleteQrcode: function (e) {
            this.setData({
                qr_code_list: [],
                show_qr_code: false,
            });
        }
        ,
        formReset: function () {
            console.log('form发生了reset事件')
        }
        ,
    }
);