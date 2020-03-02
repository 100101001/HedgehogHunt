//index.js
//获取应用实例
var app = getApp();
var WxParse = require('../wxParse/wxParse.js');
var utils = require('../utils/util.js');

Page({
    data: {
        autoplay: true,
        interval: 3000,
        duration: 1000,
        swiperCurrent: 0,
        hideShopPopup: true,
        buyNumber: 1,
        buyNumMin: 1,
        buyNumMax: 1,
        canSubmit: false, //  选中时候是否允许加入购物车
        shopCarInfo: {},
        shopType: "addShopCar",//购物类型，加入购物车或立即购买，默认为加入购物车,
        id: 0,
        shopCarNum: 0,
        commentCount: 2,
        notInCart: [],
        infos: [],
        info: {},
        selected_id: 0
    },
    onLoad: function (e) {
        var that = this;
        that.setData({
            id: e.id
        });
    },
    onShow: function () {
        this.getInfo();
        this.getComments();
    },
    goShopCar: function () {
        if (!app.loginTip()) {
            return;
        }
        wx.navigateTo({
            url: "/mall/pages/cart/index"
        });
    },
    toAddShopCar: function () {
        if (!app.loginTip()) {
            return;
        }
        this.setData({
            shopType: "addShopCar"
        });
        this.bindGuiGeTap();
    },
    tobuy: function () {
        if (!app.loginTip()) {
            return;
        }
        this.setData({
            shopType: "tobuy"
        });
        this.bindGuiGeTap();
    },
    addShopCar: function () {
        if (!app.loginTip()) {
            return
        }
        if (this.data.shopCarNum >= 99) {
            app.alert({ 'content': "购物车已满，请清空购物车后重试" })
            this.setData({
                hideShopPopup: true
            })
            return
        }
        var that = this;
        var data = {
            "id": this.data.info.id,
            "number": this.data.buyNumber
        };
        var notInCart = that.data.notInCart
        var idx = notInCart.indexOf(this.data.info.id)
        wx.request({
            url: app.buildUrl("/cart/add"),
            header: app.getRequestHeader(),
            method: 'POST',
            data: data,
            success: function (res) {
                var resp = res.data;
                app.alert({ "content": resp.msg });
                that.setData({
                    hideShopPopup: true,
                    shopCarNum: idx >= 0 ? that.data.shopCarNum + 1 : that.data.shopCarNum
                });
                if (idx >= 0) {
                    notInCart.splice(idx, idx + 1)
                    that.setData({
                        notInCart: notInCart
                    })
                }
            }
        });
    },
    buyNow: function () {
        var data = {
            goods: [
                {
                    "id": this.data.info.id,
                    "price": this.data.info.price,
                    "number": this.data.buyNumber
                }
            ]
        };
        this.setData({
            hideShopPopup: true
        });
        wx.navigateTo({
            url: "/mall/pages/order/index?data=" + JSON.stringify(data)
        });
    },
    /**
     * 规格选择弹出框
     */
    bindGuiGeTap: function () {
        this.setData({
            hideShopPopup: false
        });
    },
    /**
     * 规格选择弹出框隐藏
     */
    closePopupTap: function () {
        this.setData({
            hideShopPopup: true
        })
    },
    numJianTap: function () {
        if (this.data.buyNumber <= this.data.buyNumMin) {
            return;
        }
        var currentNum = this.data.buyNumber;
        currentNum--;
        this.setData({
            buyNumber: currentNum
        });
    },
    numJiaTap: function () {
        if (this.data.buyNumber >= this.data.buyNumMax) {
            return;
        }
        var currentNum = this.data.buyNumber;
        currentNum++;
        this.setData({
            buyNumber: currentNum
        });
    },
    //事件处理函数
    swiperchange: function (e) {
        this.setData({
            swiperCurrent: e.detail.current
        })
    },
    getInfo: function () {
        var that = this;
        wx.request({
            url: app.buildUrl("/product/info"),
            header: app.getRequestHeader(),
            data: {
                id: that.data.id
            },
            success: function (res) {
                var resp = res.data;
                if (resp.code != 200) {
                    app.alert({ "content": resp.msg });
                    wx.navigateBack({})
                    return;
                }
                var selected_id = that.data.selected_id
                that.setData({
                    selected_id: selected_id == 0 ? 0 : selected_id,
                    info: resp.data.info[selected_id],
                    infos: resp.data.info,
                    buyNumMax: resp.data.info.stock,
                    shopCarNum: resp.data.cart_number,
                    notInCart: resp.data.not_in_cart,
                });

                WxParse.wxParse('article', 'html', resp.data.info[0].summary, that, 5);
            }
        });
    },
    getComments: function () {
        var that = this;
        wx.request({
            url: app.buildUrl("/product/comments"),
            header: app.getRequestHeader(),
            data: {
                id: that.data.id
            },
            success: function (res) {
                var resp = res.data;
                if (resp.code != 200) {
                    app.alert({ "content": resp.msg });
                    return;
                }

                that.setData({
                    commentList: resp.data.list,
                    commentCount: resp.data.count,
                });
            }
        });
    },
    onShareAppMessage: function () {
        var that = this;
        return {
            title: that.data.info.name,
            path: '/mall/pages/info?id=' + that.data.info.id,
            success: function (res) {
                // 转发成功
                wx.request({
                    url: app.buildUrl("/member/share"),
                    header: app.getRequestHeader(),
                    method: 'POST',
                    data: {
                        url: utils.getCurrentPageUrlWithArgs()
                    },
                    success: function (res) {

                    }
                });
            },
            fail: function (res) {
                // 转发失败
            }
        }
    },
    //点击导航
    onNavigateTap: function (event) {
        navigate.onNavigateTap(event, this)
    },
    //点击预览图片
    previewImage: function (e) {
        wx.previewImage({
            current: this.data.info.main_image, // 当前显示图片的http链接
            urls: [this.data.info.main_image] // 需要预览的图片http链接列表
        })
    },
    //切换商品规格
    setOption: function (e) {
        var idx = e.currentTarget.dataset.id
        var info = this.data.infos[idx]
        this.setData({
            info: info,
            selected_id: idx
        })
        WxParse.wxParse('article', 'html', info.summary, this, 5);
    }
});
