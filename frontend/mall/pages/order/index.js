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
    /***
     * onLoad 加载订单详情页
     * @param e 下单产品列表和下单来源
     */
    onLoad: function (e) {
        var that = this;
        that.setData({
            params: JSON.parse(e.data)
        });
    },
    /***
     * onShow 订单详情页显示
     * 如果用户没有二维码且订单项中没有二维码则需随单加购二维码（不同意则终止核对下单流程）
     * 否则正常加载订单详细信息，用户进行核对下单
     */
    onShow: function () {
        if (app.globalData.has_qrcode) {
            this.getOrderInfo();
        } else {
            //判断商品列表中有无二维码
            let goods = this.data.params['goods']
            let index = goods.findIndex(item => item.id === app.globalData.qrcodeProductId)
            if (index === -1) {
                this.requireOrderQrcode();
            } else {
                this.getOrderInfo();
            }
        }
    },
    /***
     * toCreateOrder 确认下单的入口
     * 判断收货地址如果没有的话，提示用户操作增加
     * 否则，继续进行订单创建
     */
    toCreateOrder: function(e){
        if (!this.data.default_address) {
            app.alert({
                'title': '温馨提示',
                'content': '请增加收货地址！'
            })
            return
        }
        this.createOrder(e)
    },
    /***
     * createOrder 根据订单列表创建订单
     */
    createOrder: function () {
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
    /***
     * requireOrderQrcode 征得用户同意后随单加购二维码，否则不能下单
     */
    requireOrderQrcode: function () {
        let qrcodePrice = app.globalData.qrcodePrice
        let that = this
        app.alert({
            title: '温馨提示',
            content: '您还没有闪寻码无法下单，是否加' + qrcodePrice + '元随单购买？',
            showCancel: true,
            cb_confirm: function () {
                //加入订单款项
                let params = that.data.params
                params['goods'].push({
                    "id": app.globalData.qrcodeProductId,
                    "price": qrcodePrice,
                    "number": 1
                })
                that.setData({
                    params: params
                })
                that.getOrderInfo()
            },
            cb_cancel: function () {
                //回退
                wx.navigateBack()
            }
        })
    },
    /***
     * getOrderInfo 根据订单列表的产品ID，获取详细的产品信息，并计算出支付价格
     */
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
