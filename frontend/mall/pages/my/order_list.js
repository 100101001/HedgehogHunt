const app = getApp()
const globalData = app.globalData


/**
 * orderPay 订单缴费
 * @param order_sn 订单流水号
 * @param cb_success 回调函数
 * @link toPay
 */
const orderPay = function (order_sn, cb_success = () => {}) {
  wx.request({
    url: app.buildUrl("/order/pay"),
    header: app.getRequestHeader(),
    method: 'POST',
    data: {
      order_sn: order_sn
    },
    success: function (res) {
      let resp = res.data;
      if (resp['code'] !== 200) {
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
          app.alert({content: '支付失败'})
        }
      })
    }
  })
}

/***
 * 对虚拟商品进行发货，分别有
 * 二维码发货 {@see getQrcodeFromWechat, @see changeMemberSmsTimes},
 * 短信包发货 {@see addSmsPkg}
 * 短信按量购发货 {@see changeMemberSmsTimes}，
 * 并对订单状态进行处理{@see onQrcodeSuccess, @see onSmsBuySuccess}
 * 如果操作失败提示联系技术人员解决 {@see onFailContactTech}
 * @param order_sn 订单流水号
 * @param qr_code_num 购买的二维码数量
 * @param sms_pkg_num 购买的套餐包数量
 * @param sms_num 购买的按量计费消息数
 * @param only_special 是否只有非实物产品(非周边)，据此自动变更订单状态
 * @link toPay
 */
const onOrderPaySuccess = function (order_sn = "", qr_code_num = 0, sms_pkg_num = 0, sms_num = 0, only_special = false) {
  if (qr_code_num) {
    //操作member和qr_code表
    getQrcodeFromWechat(() => {
      changeMemberSmsTimes(globalData.buyQrCodeFreeSmsTimes, () => {
        onQrcodeSuccess(only_special, order_sn)  //自动发货和用户提示
      }, onFailContactTech)
    }, onFailContactTech)
  } else if (sms_pkg_num) {
    //操作sms_pkg表
    addSmsPkg(() => {
      onSmsBuySuccess(order_sn, '短信包购买成功') //自动发货和用户提示
    }, onFailContactTech)
  } else if (sms_num) {
    //操作qr_code表
    changeMemberSmsTimes(sms_num, () => {
      onSmsBuySuccess(order_sn, '短信购买成功') //自动发货和用户提示
    }, onFailContactTech)
  }
}

/**
 * getQrcodeFromWechat
 * 获取二维码
 * @link onOrderPaySuccess
 */
const getQrcodeFromWechat = function (cb_success=() => {}, cb_fail=() => {}) {
  wx.request({
    method: 'post',
    url: app.buildUrl('/qrcode/wx'),
    header: app.getRequestHeader(),
    success: function (res) {
      let resp = res.data
      if (resp['code'] !== 200) {
        cb_fail()
        return
      }
      globalData.has_qrcode = true
      cb_success()
    },
    fail: function (res) {
      cb_fail()
    }
  })
}

/**
 * onQrcodeSuccess 获取二维码成功时，且附赠了免费通知次数后
 * 自动发货{@see autoSendGoods}，和进行用户提示
 * @link onOrderPaySuccess
 */
const onQrcodeSuccess = function (only_special = false, order_sn = "") {
  if (only_special) {
    autoSendGoods(order_sn)
  }
  wx.showToast({
    title: '购买寻物码成功',
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
              title: '寻物码查看',
              content: '入口页【我的】—【个人信息】',
            })
          }
        })
      }, 700)
    }
  })
}


/**
 * addSmsPkg 为用户增加一个短信套餐包
 * @param cb_success
 * @param cb_fail
 * @link onOrderPaySuccess
 */
const addSmsPkg = function (cb_success = () => {}, cb_fail = () => {}) {
  wx.request({
    url: app.buildUrl('/member/sms/pkg/add'),
    header: app.getRequestHeader(),
    success: res => {
      let resp = res.data
      if (resp['code'] !== 200) {
        cb_fail()
        return
      }
      cb_success()
    },
    fail: (res) => {
      cb_fail()
    }
  })
}

/**
 * changeMemberSmsTimes 会员增加通知次数（改变）
 * @param buy_times
 * @param cb_success
 * @param cb_fail
 * @link onOrderPaySuccess
 */
const changeMemberSmsTimes = function (buy_times = 0, cb_success = () => {}, cb_fail = () => {}) {
  wx.request({
    url: app.buildUrl('/member/sms/change'),
    header: app.getRequestHeader(),
    data: {
      times: buy_times
    },
    success: res => {
      let resp = res.data
      if (resp['code'] !== 200) {
        cb_fail()
        return
      }
      cb_success()
    },
    fail: (res) => {
      cb_fail()
    }
  })
}

/**
 * onSmsBuySuccess
 * 自动发短信包和短信货{@see autoSendGoods}，并且用户提示
 * @param order_sn
 * @param msg
 */
const onSmsBuySuccess = function (order_sn = "", msg = "") {
  autoSendGoods(order_sn)
  wx.showToast({
    title: msg,
    duration: 600
  })
}

/**
 * autoSendGoods 将order_sn订单物流状态设为已发货
 * @param order_sn
 * @link onSmsBuySuccess
 * @link onQrcodeSuccess
 */
const autoSendGoods = function (order_sn) {
  wx.request({
    url: app.buildUrl("/order/express/status/set"),
    data: {
      order_sn: order_sn,
      status: -6
    }
  })
}


/**
 * onFailContactTech 系统操作使得用户利益受损的，让用户联系技术人员
 * 已支付后未成功获取非周边产品{@link onOrderPaySuccess}
 * 已取消订单，余额退回失败的{@link onOrderCancelSuccess}
 * @param title
 * @param content
 * @link onOrderCancelSuccess
 * @link onOrderPaySuccess
 */
const onFailContactTech = function (title = "跳转提示", content = '服务出错了，为避免您的利益损失，将跳转联系技术支持') {
  app.alert({
    title: title,
    content: content,
    cb_confirm: () => {
      wx.navigateTo({
        url: '/pages/Mine/connect/index?only_tech_contact='+ 1
      })
    }
  })
};

/**
 * onOrderCancelSuccess 取消订单成功的回调函数
 * 根据订单余额折扣退余额{@see changeUserBalance}
 * 回退失败联系技术人员 {@see onFailContactTech}
 * @param balance_discount 回退余额
 * @link orderCancel
 */
const onOrderCancelSuccess = function (balance_discount=0) {
  if (balance_discount) {
    //如果有折扣加回去
    changeUserBalance(balance_discount, () => {
    }, onFailContactTech)
  }
}

/**
 * changeUserBalance 用于取消订单后，回退用户余额
 * @param unit 余额变化
 * @param cb_success 回调函数
 * @param cb_fail
 * @link onOrderCancelSuccess
 */
const changeUserBalance = function (unit = 0, cb_success = () => {}, cb_fail=()=>{}) {
  wx.showLoading({
    title: "退回余额中"
  })
  wx.request({
    url: app.buildUrl("/member/balance/change"),
    header: app.getRequestHeader(),
    data: {
      unit: unit,
      note: "订单退款"
    },
    success: res => {
      cb_success()
    },
    complete: res => {
      wx.hideLoading()
    },
    fail: res => {
      cb_fail()
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
    loadingMore: true
  },
  /**
   * statusTap 切换状态时，重新加载对应的订单列表
   * @param e
   */
  statusTap: function (e) {
    this.setData({
      currentType: e.currentTarget.dataset.index
    })
    this.setSearchInitData()
    this.getPayOrder()
  },
  /**
   * orderDetail 进入订单详情页
   * @param e
   */
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
    this.getPayOrder()
  },
  /**
   * setSearchInitData
   * 以下三个加载订单列表的参数初始化
   * 页数，订单列表，是否还有更多
   * @param e
   */
  setSearchInitData: function (e) {
    this.setData({
      p: 1,
      order_list: [],
      loadingMore: true
    })
  },
  /**
   * orderCancel 取消订单
   * 先删除订单{@see orderOps}，删除成功后进行退款{@see onOrderCancelSuccess}
   * @param e
   */
  orderCancel: function (e) {
    //dataset的id是订单流水号，balance是订单所带余额折扣
    this.orderOps(e.currentTarget.dataset.id, "cancel", "确定取消订单？", () => {
      onOrderCancelSuccess(e.currentTarget.dataset.balance)
    })
  },
  /**
   * getPayOrder 获取一页订单列(更多标记)
   */
  getPayOrder: function () {
    wx.request({
      url: app.buildUrl("/my/order"),
      header: app.getRequestHeader(),
      data: {
        status: this.data.status[this.data.currentType],
        p: this.data.p
      },
      success:  (res) => {
        let resp = res.data
        if (resp['code'] !== 200) {
          app.alert({content: resp['msg']})
          return
        }
        //页数加一，是否有更多
        this.setData({
          order_list: this.data.order_list.concat(resp['data']['pay_order_list']),
          p: this.data.p + 1,
          loadingMore: resp['data']['has_more']
        })
      }
    })
  },
  /**
   * toPay 支付订单后{@see orderPay}，根据订单是否包含虚拟商品进行发货{@see onOrderPaySuccess}
   * @param e
   */
  toPay: function (e) {
    let dataset = e.currentTarget.dataset
    //订单流水号和垫付的余额数
    let order_sn = dataset.id
    let only_special = dataset.special //订单仅包含非周边商品，用来自动发货
    //订单中购买的非周边产品
    let sms_num = dataset.sms
    let sms_pkg_num = dataset.sms_pkg
    let qr_code_num = dataset.qr_code
    orderPay(order_sn, () => {
      onOrderPaySuccess(order_sn, qr_code_num, sms_pkg_num, sms_num, only_special)
    })
  },
  /**
   * orderConfirm 待确认订单 status=-6,进行确认收货操作{@see orderOps}
   * @param e
   */
  orderConfirm: function (e) {
    this.orderOps(e.currentTarget.dataset.id, "confirm", "确定收到？");
  },
  /**
   * orderComment 待评价的订单
   * @param e
   */
  orderComment: function (e) {
    wx.navigateTo({
      url: "/mall/pages/my/comment?order_sn=" + e.currentTarget.dataset.id
    })
  },
  /**
   * orderRecall 待发货订单——进行退货
   * @param e
   */
  orderRecall: function (e) {
    //提示确认退货
    //调用后端进行退款 https://pay.weixin.qq.com/wiki/doc/api/jsapi.php?chapter=9_4
    //显示调用成功，等待退款到账
    wx.request({
      url: app.buildUrl(),
      header: app.getRequestHeader(),
      data: {},
      success: (res) => {

      }
    })
  },
  /**
   * orderLogistic 待确认订单——查看物流
   * @param e
   */
  orderLogistic: function (e) {
    // e.currentTarget.dataset.express_sn
    wx.setClipboardData({
      data: "75337965025053",
      success: res => {
        wx.showToast({
          title: '快递单号已复制',
          success: res => {
            setTimeout(() => {
              wx.navigateToMiniProgram({
                appId: globalData.kd100.appId,
                path: `${globalData.kd100.paths.result}75337965025053`,
                complete: res => {
                  //防止用户取消跳转时，控制台报错
                }
              })
            }, 400)
          }
        })
      }
    })
  },
  /**
   * orderOps 订单操作前进行操作核实
   * 确认继续操作，否则终止
   * @param order_sn 订单号
   * @param act 操作
   * @param msg 核实信息
   * @param cb_success
   */
  orderOps: function (order_sn, act, msg, cb_success = () => {}) {
    app.alert({
      title: '提示信息',
      content: msg,
      showCancel: true,
      cb_confirm: () => {
        wx.request({
          url: app.buildUrl("/order/ops"),
          header: app.getRequestHeader(),
          method: 'POST',
          data: {
            order_sn: order_sn,
            act: act
          },
          success: (res) => {
            let resp = res.data;
            app.alert({content: resp['msg']})
            if (resp['code'] === 200) {
              this.setSearchInitData()
              this.getPayOrder()
              cb_success()
            }
          }
        })
      }
    })
  },
  /**
   * onReachBottom 如果还有未加载的订单就获取下一页{@see getPayOrder}
   */
  onReachBottom() {
    if (this.data.loadingMore) {
      this.getPayOrder()
    }
  }
});
