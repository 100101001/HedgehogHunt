// pages/jmall/my/controls/feedback/index.js
var app = getApp();
Page({
    data: {
        text_placeholder: "使用过程中遇到的问题，程序UI的设计优化，功能的增减，使用的体验，以及鼓励和认可，都欢迎反馈，让我们一起把平台越做越好`",
        imglist: [],
        count: 1,
        pic_status: true,
        loadingHidden:true,

    },
    onLoad: function (options) {
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
                    imglist: imglist
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
        console.log(index);
        let imglist = this.data.imglist;
        imglist.splice(index, 1);
        this.setData({
            imglist: imglist
        });
        if (imglist.length < 9) {
            this.setData({
                pic_status: true,
            });
        }
    },
    formSubmit: function (e) {
        var data = e.detail.value;
        console.log(data);
        var img_list = this.data.imglist;
        var url = "/feedback/create";
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
                that.uploadImage(id, img_list);
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
    uploadImage: function (id, img_list) {
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
            //图片不存在，则重新上传
            wx.uploadFile({
                url: app.buildUrl('/feedback/add-pics'), //接口地址
                header: app.getRequestHeader(),
                filePath: img_list[i - 1],//文件路径
                formData: {'id': id},
                name: 'file',//文件名，不要修改，Flask直接读取
                success: function (res) {
                    // var resp = JSON.parse(res.data);
                    //     if (resp.code !== 200) {
                    //         app.alert({'content': resp.msg});
                    //         return;
                    //     }
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
    },
    endCreate: function (id) {
            var that = this;
            wx.request({
                url: app.buildUrl("/feedback/end-create"),
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
                        title: '提交成功,感谢反馈！',
                        icon: 'success',
                        duration: 2000
                    });
                    that.setData({
                        loadingHidden: true,
                    });
                    wx.navigateBack();
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
});