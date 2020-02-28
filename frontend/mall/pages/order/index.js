//获取应用实例
var app = getApp();

Page({
    data: {
        goods_list: [],
        default_address: null,
        yun_price: "0.00",
        pay_price: "0.00",
        total_price: "0.00",
        params: null,
        express_address_id: 0,
        has_qrcode: app.globalData.has_qrcode
    },
    onLoad: function (e) {
        var that = this;
        that.setData({
            params: JSON.parse(e.data)
        });
    },
    onShow: function () {
        var that = this;
        this.getOrderInfo();
    },
    createOrder: function (e) {
        // 第一次可能没拿到
        if (!this.data.has_qrcode) {
            wx.request({
                method: 'post',
                url: app.buildUrl('/qrcode/wx'),
                header: app.getRequestHeader(1),
                success: res => {
                    if (res.data.code === 200) {
                        app.globalData.has_qrcode = true
                        this.setData({
                            has_qrcode: true
                        })
                    }
                }
            })
        }
        if (this.data.default_address.id == undefined) {
            app.alert({
                'title': '温馨提示',
                'content': '请增加收货地址！'
            })
            return
        }
        wx.showLoading();
        var that = this;
        var data = {
            type: this.data.params.type,
            goods: JSON.stringify(this.data.params.goods),
            express_address_id: that.data.default_address.id
        };
        wx.request({
            url: app.buildUrl("/order/create"),
            header: app.getRequestHeader(),
            method: 'POST',
            data: data,
            success: function (res) {
                wx.hideLoading();
                var resp = res.data;
                if (resp.code != 200) {
                    app.alert({ "content": resp.msg });
                    return;
                }
                wx.redirectTo({
                    url: "/mall/pages/my/order_list"
                });
            },
            fail: function (resp) {
                wx.hideLoading()
                app.serverBusy()
            }
        });

    },
    addressSet: function () {
        wx.navigateTo({
            url: "/mall/pages/my/addressSet?id=0"
        });
    },
    selectAddress: function () {
        wx.navigateTo({
            url: "/mall/pages/my/addressList"
        });
    },
    getOrderInfo: function () {
        if (!app.globalData.has_qrcode) {
            wx.request({
                method: 'post',
                url: app.buildUrl('/qrcode/wx'),
                header: app.getRequestHeader(1),
                success: res => {
                    if (res.data.code === 200) {
                        app.globalData.has_qrcode = true
                        this.setData({
                            has_qrcode: true
                        })
                    }
                }
            })
        }
        var that = this;
        var data = {
            type: this.data.params.type,
            goods: JSON.stringify(this.data.params.goods)
        };
        wx.request({
            url: app.buildUrl("/order/info"),
            header: app.getRequestHeader(),
            method: 'POST',
            data: data,
            success: function (res) {
                var resp = res.data;
                if (resp.code != 200) {
                    app.alert({ "content": resp.msg });
                    return;
                }

                that.setData({
                    goods_list: resp.data.goods_list,
                    default_address: resp.data.default_address,
                    yun_price: resp.data.yun_price,
                    pay_price: resp.data.pay_price,
                    total_price: resp.data.total_price,
                });

                if (that.data.default_address) {
                    that.setData({
                        express_address_id: that.data.default_address.id
                    });
                }
            }
        });
    }

});
