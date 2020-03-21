var app = getApp();



const getQrcodeFromWechat = function() {
    wx.request({
        method: 'post',
        url: app.buildUrl('/qrcode/wx'),
        header: app.getRequestHeader(),
        success: function (res) {
            var resp = res.data
            app.globalData.has_qrcode = true
            app.globalData.qr_code_list = [resp.data.qr_code_url]
        },
        fail: function (res) {
            app.serverBusy()
        }
    })
}

Page({
    data: {
        order_list: [],
        statusType: ["待付款", "待发货", "待确认", "待评价", "已完成", "已关闭"],
        status: ["-8", "-7", "-6", "-5", "1", "0"],
        currentType: 0,
        tabClass: ["", "", "", "", "", ""],
        isGettingQrcode: false
    },
    statusTap: function (e) {
        var curType = e.currentTarget.dataset.index;
        this.setData({
            currentType: curType
        });
        this.getPayOrder();
    },
    orderDetail: function (e) {
        wx.navigateTo({
            url: "/mall/pages/my/order_info?order_sn=" + e.currentTarget.dataset.id
        })
    },
    onLoad: function (options) {
        // 生命周期函数--监听页面加载
    },
    onShow: function () {
        if(this.data.isGettingQrcode){
            this.getPayOrderAndshowGettingQrcode()
        }else{
            this.getPayOrder();
        }
    },
    orderCancel: function (e) {
        this.orderOps(e.currentTarget.dataset.id, "cancel", "确定取消订单？");
    },
    getPayOrderAndshowGettingQrcode: function(){
        this.getPayOrder()
        wx.showLoading({
            title: '获取闪寻码中',
            mask: true
        })
        var that = this
        setTimeout(function(){
            wx.hideLoading()
            wx.showToast({
                title: '获取成功',
                icon: 'success',
                mask: true,
                duration: 800,
                success: function () {
                    setTimeout(function () {
                        app.alert({
                            'title': '温馨提示',
                            'content': '可返回入口界面，在【我的】->【个人信息】查看您的专属闪寻码'
                        })
                    }, 800)
                }
            })
            that.setData({
                isGettingQrcode: false
            })
        }, 500)
    },
    getPayOrder: function () {
        var that = this;
        wx.request({
            url: app.buildUrl("/my/order"),
            header: app.getRequestHeader(),
            data: {
                status: that.data.status[that.data.currentType]
            },
            success: function (res) {
                var resp = res.data;
                if (resp.code != 200) {
                    app.alert({ "content": resp.msg });
                    return;
                }

                that.setData({
                    order_list: resp.data.pay_order_list
                });
            }
        });
    },
    toPay: function (e) {
        // app.alert({
        //     'title': '温馨提示',
        //     'content': '模块正在开发中,敬请期待!'
        // })
        // return
        var that = this;
        wx.request({
            url: app.buildUrl("/order/pay"),
            header: app.getRequestHeader(),
            method: 'POST',
            data: {
                order_sn: e.currentTarget.dataset.id
            },
            success: function (res) {
                var resp = res.data;
                if (resp.code != 200) {
                    app.alert({ "content": resp.msg });
                    return;
                }
                var pay_info = resp.data.pay_info;
                wx.requestPayment({
                    'timeStamp': pay_info.timeStamp,
                    'nonceStr': pay_info.nonceStr,
                    'package': pay_info.package,
                    'signType': 'MD5',
                    'paySign': pay_info.paySign,
                    'success': function (res) {
                        //支付成功
                        if (res.errMsg == "requestPayment:ok" && !app.globalData.has_qrcode) {
                            that.setData({
                                isGettingQrcode: true
                            })
                            getQrcodeFromWechat()
                        }
                    },
                    'fail': function (res) {
                    }
                });
            }
        });
    },
    orderConfirm: function (e) {
        this.orderOps(e.currentTarget.dataset.id, "confirm", "确定收到？");
    },
    orderComment: function (e) {
        wx.navigateTo({
            url: "/mall/pages/my/comment?order_sn=" + e.currentTarget.dataset.id
        });
    },
    orderOps: function (order_sn, act, msg) {
        var that = this;
        var params = {
            "content": msg,
            "cb_confirm": function () {
                wx.request({
                    url: app.buildUrl("/order/ops"),
                    header: app.getRequestHeader(),
                    method: 'POST',
                    data: {
                        order_sn: order_sn,
                        act: act
                    },
                    success: function (res) {
                        var resp = res.data;
                        app.alert({ "content": resp.msg });
                        if (resp.code == 200) {
                            that.getPayOrder();
                        }
                    }
                });
            }
        };
        app.tip(params);
    }
});
