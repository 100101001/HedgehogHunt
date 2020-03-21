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
        createOrderDisabled: false,
        dataReady: false
    },
    onLoad: function (e) {
        var that = this;
        that.setData({
            params: JSON.parse(e.data)
        });
    },
    onShow: function () {
        if (app.globalData.has_qrcode) {
            this.getOrderInfo();
        } else {
            //判断商品列表中有无二维码
            let goods = this.data.params['goods']
            let index = goods.findIndex(item => item.id === app.globalData.qrcodeProductId)
            if (index === -1) {
                this.requireQrcode();
            } else {
                this.getOrderInfo();
            }
        }
    },
    createOrder: function (e) {
        if (this.data.default_address.id == undefined) {
            app.alert({
                'title': '温馨提示',
                'content': '请增加收货地址！'
            })
            return
        }
        this.setData({
            createOrderDisabled: true
        })
        wx.showLoading({
            mask:true,
            title: '正在下单'
        });
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
                app.serverBusy()
                that.setData({
                    createOrderDisabled: false
                })
            },
            complete: function (res) {
                wx.hideLoading()
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
    requireQrcode: function(){
        if (!app.globalData.has_qrcode) {
            let qrcodePrice = app.globalData.qrcodePrice
            let that = this
            app.alert({
                'title':'温馨提示',
                'content':'您还没有闪寻码无法下单，是否加'+qrcodePrice+'元随单购买？',
                'cb_confirm': function(){
                    //加入订单款项
                    let params = that.data.params
                    params['goods'].push({
                        "id": app.globalData.qrcodeProductId,
                        "price": qrcodePrice,
                        "number": 1
                    })
                    that.setData({
                        params : params
                    })
                    that.getOrderInfo()
                },
                'cb_cancel': function () {
                    //回退
                    wx.redirectTo({
                        'url' : '/mall/pages/cart/index'
                    })
                }
            })
        }
    },
    getOrderInfo: function () {
        var that = this
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
                    dataReady: true
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
