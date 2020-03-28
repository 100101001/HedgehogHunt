const app = getApp();

/**
 * getQrcodeFromWechat
 * 获取二维码
 */
const getQrcodeFromWechat = function(cb_success=()=>{}) {
    wx.request({
        method: 'post',
        url: app.buildUrl('/qrcode/wx'),
        header: app.getRequestHeader(),
        success: function (res) {
            let resp = res.data
            if(resp['code']!==200){
                return
            }
            app.globalData.has_qrcode = true
            cb_success()
        },
        fail: function (res) {
            app.serverBusy()
        }
    })
}


const smsBuySuccessCommonCallback = function (msg) {
    wx.showToast({
        title: msg,
        duration: 600,
        success:()=>{
            setTimeout(()=>{
                wx.navigateBack()
            }, 600)
        }
    })
}

/**
 * smsBuyFailCommonCallback
 * 购买短信套餐包和短信服务并支付后，如果操作失败通用的操作提示
 */
const smsBuyFailCommonCallback = function () {
    app.serverBusy(()=>{
        app.alert({
            title: "跳转提示",
            content: '系统生病了，联系技术人员帮您购买',
            cb_confirm: ()=>{
                wx.navigateTo({
                    url: '/pages/Mine/connect/index'
                })
            }
        })
    })
}

/**
 * 为用户增加一个短信套餐包
 * @param buy_times
 * @param cb_success
 */
const addSmsPkg = function (cb_success=()=>{}) {
    wx.request({
        url: app.buildUrl('/member/sms/pkg/add'),
        header: app.getRequestHeader(),
        success: res => {
            let resp = res.data
            if (resp['code'] !== 200) {
                smsBuyFailCommonCallback()
                return
            }
            cb_success()
        },
        fail: res => {
            smsBuyFailCommonCallback()
        }
    })
}

/**
 * changeMemberSmsTimes
 * 会员增加通知次数（改变）
 * @param buy_times
 * @param cb_success
 */
const changeMemberSmsTimes = function (buy_times, cb_success=()=>{}) {
    wx.request({
        url: app.buildUrl('/member/sms/change'),
        header: app.getRequestHeader(),
        data: {
            times: buy_times
        },
        success: res => {
            let resp = res.data
            if (resp['code'] !== 200) {
                smsBuyFailCommonCallback()
                return
            }
            cb_success()
        },
        fail: res => {
            smsBuyFailCommonCallback()
        }
    })
}

/**
 * hasQrcode 设置用户是否有二维码
 * @param cb_success
 */
const hasQrcode = function (cb_success=()=>{}) {
    wx.request({
        url: app.buildUrl("/member/has-qrcode"),
        header: app.getRequestHeader(),
        success: res => {
            let resp = res.data
            if (resp['code'] !== 200) {
                return
            }
            cb_success(resp['data']['has_qr_code'])
        }
    })
}

/**
 * orderPay 订单缴费
 * @param order_sn 订单流水号
 * @param cb_success 回调函数
 */
const orderPay = function (order_sn, cb_success=()=>{}) {
    wx.request({
        url: app.buildUrl("/order/pay"),
        header: app.getRequestHeader(),
        method: 'POST',
        data: {
            order_sn: order_sn
        },
        success: function (res) {
            let resp = res.data;
            if (resp['code'] != 200) {
                app.alert({content: resp['msg']});
                return
            }
            let pay_info = resp['data']['pay_info'];
            wx.requestPayment({
                timeStamp: pay_info.timeStamp,
                nonceStr: pay_info.nonceStr,
                package: pay_info.package,
                signType: 'MD5',
                paySign: pay_info.paySign,
                success: function (res) {
                    //支付成功
                    cb_success()
                },
                fail: function (res) {
                }
            })
        }
    })
}

/**
 * 用户余额扣除
 * @param unit 余额变化
 * @param cb_success 回调函数
 */
const changeUserBalance = function (unit = 0, cb_success = () => {}) {
    wx.showLoading({
        title: "扣除余额中"
    })
    wx.request({
        url: app.buildUrl("/member/balance/change"),
        header: app.getRequestHeader(),
        data: {
            unit: unit,
            note: "在线购物"
        },
        success: res => {
            cb_success()
        },
        complete: res => {
            wx.hideLoading()
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
        isGettingQrcode: false,
        loadingMore: true
    },
    /**
     * statusTap 切换状态时，重新加载对应的订单列表
     * @param e
     */
    statusTap: function (e) {
        this.setData({
            currentType: e.currentTarget.dataset.index
        });
        this.setSearchInitData()
        this.getPayOrder()
    },
    orderDetail: function (e) {
        wx.navigateTo({
            url: "/mall/pages/my/order_info?order_sn=" + e.currentTarget.dataset.id
        })
    },
    onLoad: function (options) {
        // 生命周期函数--监听页面加载
    },
    /**
     * onShow
     * 初始化页面搜索参数，并加载订单列表
     * 如果正在获取二维码，那么除了上述操作，还会根据获取结果进行用户操作提示
     * onShow触发时机：
     * 1、支付完毕回到页面
     * 2、查看订单详情后，回到页面
     */
    onShow: function () {
        this.setSearchInitData()
        if (this.data.isGettingQrcode) {
            hasQrcode((has_qr_code) => {
                this.data.has_qrcode = has_qr_code
                this.data.isGettingQrcode = false
                this.getPayOrderAndShowGettingQrcode()
            })
        } else {
            this.getPayOrder();
        }
    },
    /**
     * setSearchInitData
     * 以下三个加载订单列表的参数初始化
     * 页数，订单列表，是否还有更多
     * @param e
     */
    setSearchInitData: function(e){
        this.setData({
            p: 1,
            order_list: [],
            loadingMore: true
        })
    },
    /**
     * orderCancel
     * 取消订单
     * @param e
     */
    orderCancel: function (e) {
        this.orderOps(e.currentTarget.dataset.id, "cancel", "确定取消订单？");
    },
    /**
     * getPayOrderAndShowGettingQrcode
     * 除了获取订单列表外，根据二维码获取情况，给用户操作提示
     */
    getPayOrderAndShowGettingQrcode: function(){
        this.getPayOrder()
        wx.showLoading({
            title: '获取闪寻码中',
            mask: true
        })
        if (this.data.has_qrcode) {
            //获取成功
            setTimeout(() => {
                wx.hideLoading()
                wx.showToast({
                    title: '获取成功',
                    icon: 'success',
                    mask: true,
                    duration: 800,
                    success: function () {
                        setTimeout(function () {
                            app.alert({
                                title: '赠品提示',
                                content: '已发放5次免费的失物通知！',
                                cb_confirm: () => {
                                    app.alert({
                                        title: '查看提示',
                                        content: '在入口页【我的】—【个人信息】查看您的专属闪寻码',
                                    })
                                }
                            })
                        }, 700)
                    }
                })
            }, 500)
        } else {
            //获取失败
            setTimeout(() => {
                wx.hideLoading()
                app.alert({
                    title: "跳转提示",
                    content: "联系技术支持帮您获取二维码",
                    cb_confirm: () => {
                        wx.redirectTo({
                           url: '/pages/Mine/connect/index'
                        })
                    }
                })
            }, 500)
        }

    },
    /**
     * getPayOrder 获取一页订单列(更多标记)
     */
    getPayOrder: function () {
        var that = this;
        wx.request({
            url: app.buildUrl("/my/order"),
            header: app.getRequestHeader(),
            data: {
                status: that.data.status[that.data.currentType],
                p: this.data.p
            },
            success: function (res) {
                var resp = res.data;
                if (resp.code != 200) {
                    app.alert({"content": resp.msg});
                    return;
                }
                //页数加一，是否有更多
                that.setData({
                    order_list: that.data.order_list.concat(resp.data.pay_order_list),
                    p: that.data.p + 1,
                    loadingMore: resp['data']['has_more']
                });
            }
        });
    },
    /**
     * 如果订单余额垫付，则增加一层扣除余额
     * @param e
     */
    toPay: function (e) {
        let dataset = e.currentTarget.dataset
        //订单流水号和垫付的余额数
        let order_sn = dataset.id
        let balance_discount = dataset.balance
        //订单中购买的非周边产品
        let sms_num = dataset.sms
        let sms_pkg_num = dataset.sms_pkg
        let qr_code_num = dataset.qr_code
        if(balance_discount == 0) {
            //无余额垫付
            orderPay(order_sn, () => {
                this.orderPaySuccessCallback(qr_code_num, sms_pkg_num, sms_num)
            })
        }else{
            //余额垫付
            orderPay(order_sn, () => {
                changeUserBalance(-balance_discount, () => {
                    this.orderPaySuccessCallback(qr_code_num, sms_pkg_num, sms_num)
                })
            })
        }
    },
    /***
     * 根据是否购买了非周边产品，支付后进行回调操作
     * @param qr_code_num 购买的二维码数量
     * @param sms_pkg_num 购买的套餐包数量
     * @param sms_num 购买的按量计费消息数
     */
    orderPaySuccessCallback: function(qr_code_num=0, sms_pkg_num=0, sms_num=0){
        if (qr_code_num) {
            //操作member和qr_code表
            this.data.isGettingQrcode = true
            getQrcodeFromWechat(()=>{
                changeMemberSmsTimes(app.globalData.buyQrCodeFreeSmsTimes, ()=>{})
            })
        }
        else if(sms_pkg_num) {
            //操作sms_pkg表
            addSmsPkg(()=>{
               smsBuySuccessCommonCallback('短信包购买成功')
            })
        }
        else if(sms_num){
            //操作qr_code表
            changeMemberSmsTimes(sms_num, ()=>{
                smsBuySuccessCommonCallback('短信购买成功')
            })
        }
    },
    orderConfirm: function (e) {
        this.orderOps(e.currentTarget.dataset.id, "confirm", "确定收到？");
    },
    orderComment: function (e) {
        wx.navigateTo({
            url: "/mall/pages/my/comment?order_sn=" + e.currentTarget.dataset.id
        })
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
    },
    /**
     * onReachBottom 如果还有未加载的订单就获取下一页
     */
    onReachBottom() {
        if (this.data.loadingMore) {
            this.getPayOrder()
        }
    }
});
