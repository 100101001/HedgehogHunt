//index.js
//获取应用实例
var app = getApp();

Page({
    data: {
        autoplay: true,
        interval: 3000,
        duration: 1000,
        swiperCurrent: 0,
      loadingHidden: true,

      info: {
        "auther_name": "韦朝旭",
        "avatar": "https://wx.qlogo.cn/mmopen/vi_32/Q0j4TwGTfTJLMa7CuCcoXicK6SpMA9E0IHxPgLYibKFbeCkUo3IicyyDr8ssosTEaaptIL2Xjic6LXEC2OmjwmXMmQ/132",
        "business_type": 1,//捡到东西还是丢了东西，捡到是1，丢了是0
        "goods_name": "钱包",
        "onwer_name":"韦朝旭",
        "id": 23,//发布的记录的id
        "is_auth": false,//当前用户是否是消息的发布者
        "location": "图书馆",
        "main_image": "https://jmall.opencs.cn/static/upload/20191030/81f2f83ff3ea43e797a3cf6144e9afba.jpg",//主图
        "pics": [
          "https://jmall.opencs.cn/static/upload/20191030/81f2f83ff3ea43e797a3cf6144e9afba.jpg"
        ],//组图
        "summary": "\u5168\u65b0\uff0c\u57fa\u672c\u6ca1\u5199\u5b57",//详情介绍
        "updated_time": "2019-10-30 12:20:40",//更新时间
        "view_count": 39,//浏览量
      }

    },
    onShareAppMessage: function (Options) {
        var business_type = this.data.info.business_type;
        if (business_type == 1) {
            var type_name = "出闲置" + this.data.info.goods_name;
            var end = "。你需要吗？快来看看吧";
        } else {
            var type_name = "求购" + this.data.info.goods_name;
            var end = "。你有吗？快来看看吧";
        }
        var is_auth = this.data.info.is_auth;
        if (is_auth) {
            var start = "我在济人济市"
        } else {
            var start = "有人在济人济市"
        }
        var title_msg = start + type_name + end;
        return {
            title: title_msg,
            path: '/pages/jmall/index/index?goods_id=' + this.data.info.id,
            success: function (res) {
                wx.request({
                    url: app.buildUrl('/member/share'),
                    success: function (res) {
                        wx.showToast({
                            title: '分享成功！',
                            icon: 'success',
                            content: '积分+5',
                            duration: 3000
                        })
                    },
                    fail: function (res) {
                        wx.showToast({
                            title: '分享失败！',
                            duration: 3000
                        })
                    }
                })
            }
        }
    },
    onLoad: function (options) {
        var goods_id =23;
        var check_report = app.globalData.check_report;
        this.setData({
            check_report: check_report
        });
        var that = this;
        that.setData({
            show_qr_code: false,
        });
        if (check_report) {
            this.getReportInfo(goods_id);
        } else {
            //this.getGoodsInfo(goods_id);
        }
    },
    onShow:function(){
      var regFlag = app.globalData.regFlag;
      this.setData({
        regFlag: regFlag
      });
   
    },
    login: function (e) {
      app.login(e);
      var regFlag = app.globalData.regFlag;
      this.setData({
        regFlag: regFlag
      });
    },
    getReportInfo: function (id) {
        var that = this;
        that.setData({
            loadingHidden: false
        });
        wx.request({
            url: app.buildUrl("/report/info"),
            header: app.getRequestHeader(),
            data: {
                id: id
            },
            success: function (res) {
                var resp = res.data;
                if (resp.code !== 200) {
                    app.alert({'content': resp.msg});
                    return;
                }
                that.setData({
                    info: resp.data.info,
                    report_auth_info: resp.data.report_auth_info,
                    report_id: resp.data.report_id
                });
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
    },
    getGoodsInfo: function (id) {
        var that = this;
        that.setData({
            loadingHidden: false
        });
        wx.request({
            url: app.buildUrl("/goods/info"),
            header: app.getRequestHeader(),
            data: {
                id: id,
            },
            success: function (res) {
                var resp = res.data;
                if (resp.code !== 200) {
                    app.alert({'content': resp.msg});
                    return;
                }
                that.setData({
                    info: resp.data.info
                });
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
    },
    //事件处理函数
    swiperchange: function (e) {
        this.setData({
            swiperCurrent: e.detail.current
        })
    },
    toReport: function (e) {
      var regFlag=app.globalData.regFlag;
      if (!regFlag) {
        app.alert({
          "content": "没有授权登录，不能举报！请授权登录"
        });
        return;
      }
        var id = e.currentTarget.dataset.id;
        var that = this;
        wx.showModal({
            title: "违规举报",
            content: "为维护平台环境，欢迎举报色情及诈骗、恶意广告等违规信息！同时，恶意举报将会被封号，请谨慎操作，确认举报？",
            success: function (res) {
                if (res.confirm) {//点击确定,获取操作用户id以及商品id,从用户token里面获取id
                    wx.showLoading({title: '信息提交中..'});
                    wx.request({
                        url: app.buildUrl("/goods/report"),
                        header: app.getRequestHeader(),
                        data: {
                            id: id,
                        },
                        success: function (res) {
                            var resp = res.data;
                            if (resp.code !== 200) {
                                app.alert({'content': resp.msg});
                                return
                            }
                            wx.hideLoading();
                            wx.showToast({title: '举报成功，感谢反馈！', icon: 'success', duration: 2000});
                        },
                        fail: function (res) {
                            wx.hideLoading();
                            wx.showToast({title: '系统繁忙，反馈失败，还是感谢！', duration: 2000});
                            app.serverBusy();
                            return;
                        }
                    });
                    wx.navigateBack();
                }
            }
        });
    },
    goHome: function (e) {
        wx.switchTab({
            url: "../goods/index",
        })
    },
    goRelease: function (e) {
        wx.switchTab({
            url: "../release/index",
        })
    },
    showQrCode: function () {
      var regFlag = app.globalData.regFlag;
      if (regFlag){
        var show_qr_code = !this.data.show_qr_code;
        this.setData({
            show_qr_code: show_qr_code
        })}
        else{
          app.alert({
            "content":"为了防止冒领，授权登陆实名认证之后才能查看地址！"
          });
        }
    },
    //预览图片
    previewImage: function (e) {
        var current = e.target.dataset.src;
        wx.previewImage({
            current: current, // 当前显示图片的http链接
            urls: this.data.info.qr_code_list,
        })
    },
  previewItemImage: function (e) {
    var index = e.currentTarget.dataset.index;
    console.log(index);
    wx.previewImage({
      current: this.data.info.pics[index], // 当前显示图片的http链接
      urls: this.data.info.pics // 需要预览的图片http链接列表
    })
  },
    toEdit: function (event) {
        var info = this.data.info;
        app.globalData.info = info;
        wx.navigateTo({
            url: 'edit/edit',
        })
    },
    toBlockMember: function (e) {
        //选择操作的用户id
        var that = this;
        var select_member_id = e.currentTarget.dataset.id;
        var auth_id = this.data.info.member_id;
        var report_member_id = this.data.report_auth_info.member_id;
        var goods_id = this.data.info.id;
        var report_id = this.data.report_id;
        wx.showModal({
            title: '操作提示',
            content: '确认拉黑？',
            success: function (res) {
                wx.request({
                    url: app.buildUrl("/report/block"),
                    header: app.getRequestHeader(),
                    data: {
                        select_member_id: select_member_id,
                        goods_id: goods_id,
                        report_id: report_id,
                        auth_id: auth_id,
                        report_member_id: report_member_id
                    },
                    success: function (res) {
                        wx.hideLoading();
                        wx.showToast({title: '拉黑用户成功！', icon: 'success', duration: 2000});
                        wx.switchTab({
                            url: '../record/index',
                        })
                    },
                    fail: function (res) {
                        wx.hideLoading();
                        wx.showToast({title: '系统繁忙，拉黑失败！', duration: 2000});
                    }
                });
            }
        });
    },
    noRule: function (e) {
        var id = this.data.info.id;
        var report_id = this.data.report_id;
        wx.request({
            url: app.buildUrl("/report/no-rule"),
            header: app.getRequestHeader(),
            data: {
                id: id,
                report_id: report_id
            },
            success: function (res) {
                wx.hideLoading();
                wx.showToast({title: '解放商品成功！', icon: 'success', duration: 2000});
                wx.switchTab({
                    url: '../record/index',
                })
            },
            fail: function (res) {
                wx.hideLoading();
                wx.showToast({title: '系统繁忙，解放失败！', duration: 2000});
            }
        });
    },
});