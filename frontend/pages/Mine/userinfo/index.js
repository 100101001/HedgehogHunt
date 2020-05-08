const app = getApp();
const globalData = app.globalData;
const util = require('../../../utils/util');

/**
 * 在获取新二维码，短信(包)时{@link doGetNewProduct, @link confirmSmsTimes, @link confirmSmsPkg} 前往下单
 * @param data 订单项
 */
const toOrderSpecialProduct = function (data={}) {
  wx.showToast({
    title: '前往下单',
    icon: 'loading',
    success: res => {
      setTimeout(function () {
        wx.navigateTo({
          'url': '/mall/pages/order/index?data=' + JSON.stringify(data)
        })
      }, 200)
    }
  })
}


/**
 * balanceCharge 为了充余额{@link doBalanceRecharge}付费
 * @param pay_price
 * @param cb_success
 */
const balanceCharge = function (pay_price=0.01, cb_success=()=>{}) {
  wx.request({
    url: app.buildUrl('/member/balance/order'),
    header: app.getRequestHeader(),
    data: {
      price: pay_price
    },
    method: 'POST',
    success: res => {
      let resp = res.data

      //下单失败提示后返回
      if (resp['code'] !== 200) {
        app.alert({
          content: resp['msg']
        })
        return
      }

      //下单成功调起支付
      let pay_data = resp['data']
      wx.requestPayment({
        timeStamp: pay_data['timeStamp'],
        nonceStr: pay_data['nonceStr'],
        package: pay_data['package'],
        signType: pay_data['signType'],
        paySign: pay_data['paySign'],
        success: res => {
          //支付成功，继续发布
          cb_success()
        },
        fail: res => {
          app.alert({content: "支付失败"})
        }
      })
    },
    fail: res => {
      app.serverBusy()
    }
  })
}

/**
 * changeUserBalance
 * 充值支付成功后{@link doBalanceRecharge}，扣除(改变)用户余额
 * @param unit 改变量
 * @param cb_success 回调函数
 * @param cb_fail
 */
const changeUserBalance = function (unit = 0, cb_success = () => {}, cb_fail=()=>{}) {
  wx.showLoading({
    title: "扣除余额中"
  })
  wx.request({
    url: app.buildUrl("/member/balance/change"),
    header: app.getRequestHeader(),
    data: {
      unit: unit,
      note: "余额充值"
    },
    success: res => {
      cb_success()
    },
    fail: res=>{
      cb_fail()
    },
    complete: res => {
      wx.hideLoading()
    }
  })
}


/**
 * remindOldOrder 获取二维码时 {@link doGetQrCode} 提醒还有旧的二维码，短信包，短信订单
 * 用户可选择继续获取新的 {@see doGetNewProduct}
 * @param product_name
 * @param that
 */
const remindOldOrder = function (product_name = "二维码", that = null) {
  app.alert({
    title: '已购提示',
    content: '有未支付的' + product_name + '订单，前往支付？',
    showCancel: true,
    cb_confirm: res => {
      wx.navigateTo({
        url: '/mall/pages/my/order_list'
      })
    },
    cb_cancel: res => {
      app.alert({
        title: '操作提示',
        content: '是否继续获取' + product_name + '？',
        showCancel: true,
        cb_confirm: res => {
          doGetNewProduct(product_name, that)
        }
      })
    }
  })
}

/**
 * doGetNewProduct 用户无视旧订单提醒{@link remindOldOrder}或本来就没有{@link toRechargeSms, @link doGetQrCode}时，根据产品名进入获取新产品的下一步处理
 * @param product_name
 * @param that
 */
const doGetNewProduct = function (product_name = "二维码", that = null) {

  if (product_name === "二维码") {
    let data = {
      type: 'toBuy',
      goods: [{'id': globalData.qrcodeProductId, 'price': globalData.qrcodePrice, 'number': 1}]
    }
    toOrderSpecialProduct(data)
  } else if (product_name === "短信包") {
    that.setData({
      hiddenSmsPkgModal: false
    })
  } else if (product_name === "短信") {
    app.alert({
      title: '计价提示',
      content: '0.1元/1条。继续购买？',
      showCancel: true,
      cb_confirm: () => {
        that.setData({
          hiddenSmsTimesModal: false
        })
      }
    })
  }
}


/**
 * onFailContactTech 系统操作使得用户利益受损的，让用户联系技术人员
 * 余额充值时，已支付，但到账失败的{@link doBalanceRecharge}
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
}

Page({
  data: {
    dataReady: false,
    userInfo: {},
    has_qrcode: false,
    show_qrcode: false,
    qr_code: "",
    hiddenNameModal: true, //编辑姓名
    hiddenMobileModal: true, //编辑手机
    hiddenContactModal: true, //余额提现，客服
    hiddenSmsTimesModal: true, //短信按量购买
    hiddenSmsPkgModal: true, //短信套餐包购买
    hiddenIntroduceModal: true, //二维码使用介绍
    hiddenBalanceRecharge: true, //充值余额
    hiddenSmsDetailModal: true, //短信余额详情
    contact_img: globalData.static_file_domain + "/static/QRcode.jpg",
    intro_url: globalData.static_file_domain+ "/static/introduce.mp4",
    intro_init_time: 0, //
    balance_recharge_amount: "",
    sms_num: "",
    sms_pkg_price: globalData.smsPkgProductPrice
  },
  onLoad: function () {
    wx.showLoading({
      title: '加载中',
      mask: true,
      success: res => {
        setTimeout(wx.hideLoading, 300)
      }
    })
  },
  onShow() {
    // 会员的闪寻码信息
    this.getMemberInfo()
  },
  getMemberInfo: function(){
    wx.request({
      url: app.buildUrl("/member/info"),
      header: app.getRequestHeader(),
      success: (res) => {
        let resp = res.data;
        if (resp['code'] !== 200) {
          app.alert({
            content: resp['msg'],
            cb_confirm: () => {
              wx.navigateBack()
            }
          });
          return
        }
        let info = resp['data']['info'];
        this.setData({
          avatar: info['avatar'],
          nickname: info['nickname'],
          name: info['name'],
          mobile: info['mobile'],
          balance: util.toFixed(info['balance'],2),
          has_qrcode: info['has_qrcode'],
          qr_code: info['qr_code'],
          member_notify_times: info['m_times'],
          total_notify_times: info['total_times'],
          sms_pkgs: info['pkgs'],
          dataReady: true
        })
      },
      fail: (res) => {
        app.serverBusy(wx.navigateBack)
      }
    })
  },
  /**
   * 检测更换手机的频率，1个月内只能绑定一次
   */
  onEditMobile: function () {
    wx.request({
      url: app.buildUrl('/qrcode/mobile/change'),
      header: app.getRequestHeader(),
      success: (res) => {
        let resp = res.data;
        if (resp['code'] !== 200) {
          app.alert({content: resp['msg']});
          return;
        }
        this.setData({
          hiddenMobileModal: false
        })
      },
      fail: (res) => {
        app.serverBusy()
      }
    });
  },
  cancelMobileEdit: function () {
    this.setData({
      hiddenMobileModal: true
    })
  },
  onEditName: function () {
    this.setData({
      hiddenNameModal: false,
    })
  },
  cancelNameEdit: function () {
    this.setData({
      hiddenNameModal: true,
    })
  },
  showToast: function (title = '', icon = 'none', duraton = 1000, mask = true) {
    wx.showToast({
      title: title,
      icon: icon,
      duration: duraton,
      mask: mask
    })
  },
  confirmNameEdit: function (e) {
    if (!this.data.editName) {
      app.alert({
        content: '姓名不能为空'
      })
      return
    }
    if (this.data.name === this.data.editName) {
      this.showToast('请填不同姓名!', 'none')
      return
    }
    //关闭输入框
    this.cancelNameEdit()
    this.doSetName()
  },
  doSetName: function () {
    this.showToast('设置中', 'loading')
    wx.request({
      method: 'POST',
      url: app.buildUrl('/member/set/name'),
      header: app.getRequestHeader(),
      data: {name: this.data.editName},
      success: res => {
        let resp = res.data
        if (resp['code'] !== 200) {
          app.alert({content: resp['msg']})
          return
        }
        this.setData({
          name: resp['data'].name
        })
      }, complete: res => {
        wx.hideToast()
      }
    })
  },
  listenerNameInput: function (e) {
    this.setData({
      editName: e.detail.value
    })
  },
  /***
   * toGetQrCode 判断没有姓名或手机号提示用户补上，否则继续下单获取二维码{@see doGetQrCode}
   */
  toGetQrCode: function () {
    let name = this.data.name
    let mobile = this.data.mobile
    if (!name) {
      app.alert({title: '姓名不能为空', content: '点击确认去设置姓名', showCancel: true, cb_confirm: this.onEditName})
      return
    }
    if (!mobile) {
      app.alert({'content': '手机不能为空'})
      return
    }
    this.doGetQrCode()
  },
  /**
   * doGetQrCode 如果还有未支付的二维码，会提醒用户{@see remindOldOrder}，否则直接下新的二维码订单 {@see doGetNewProduct}
   * @link toGetQrCode
   */
  doGetQrCode: function () {
    wx.request({
      url: app.buildUrl('/order/sp/has'),
      header: app.getRequestHeader(),
      data: {
        product_id: globalData.qrcodeProductId
      },
      success: res => {
        let has = res.data['has']
        if (has) {
          remindOldOrder( "二维码", this)
        } else {
          doGetNewProduct( "二维码", this)
        }
      },
      fail: res => {
        app.serverBusy()
      }
    })
  },
  /**
   * checkQrCode 点击查看/隐藏二维码
   */
  checkQrCode: function () {
    this.setData({
      show_qrcode: !this.data.show_qrcode
    })
  },
  /**
   * onWithDrawTap 用户按下提现按钮后根据余额，做出操作提示
   */
  onWithDrawTap: function () {
    if (this.data.balance < 10) {
      app.alert({
        title: '提现提示',
        content: '额度满10元即可提现'
      })
      return
    }
    this.setData({
      hiddenContactModal: false
    })
  },
  /**
   * cancelContact 关闭了提现客服窗口
   * @param e
   */
  cancelContact: function (e) {
    this.setData({
      hiddenContactModal: true
    })
  },
  /**
   * previewImage 预览并保存二维码
   * @param e
   */
  previewImage: function (e) {
    let image = e.currentTarget.dataset.src
    wx.previewImage({
      current: image, // 当前显示图片的http链接
      urls: [image] // 需要预览的图片http链接列表
    })
  },
  /**
   * toRechargeBalance 用户按下余额充值按钮显示输入充值金额的模态框
   */
  toRechargeBalance: function(){
    app.alert({
      title: '充值提示',
      content: '余额可用于置顶，答谢，购物，短信付费等。提现额度为10元，确认充值？',
      showCancel: true,
      cb_confirm: ()=>{
        this.setData({
          hiddenBalanceRecharge: false
        })
      }
    })
  },
  /**
   * listenBalanceRecharge 监听用户输入的钱数
   * @param e
   */
  listenBalanceRecharge: function(e){
    this.data.balance_recharge_amount = e.detail.value
  },
  /**
   * confirmRechargeBalance 与用户核对充值收费金额
   * 如果用户确认就继续进入收费充值过程
   * 否则，终止操作
   */
  confirmRechargeBalance: function(){
    let pay_price = util.toFixed(this.data.balance_recharge_amount, 2)
    if (pay_price) {
      //充值金额大于零才继续
      app.alert({
        title: '充值确认',
        content: '您需要支付' + pay_price + '元，确认充值？',
        showCancel: true,
        cb_confirm: () => {
          this.doBalanceRecharge(pay_price)
        }
      })
    }
    //关闭输入金额的弹出框
    this.cancelRechargeBalance()
  },
  /**
   * doBalanceRecharge 充值余额的实际操作函数
   * 先收费{@see balanceCharge}，如果支付成功增加余额{@see changeUserBalance}，
   * 如果收费成功但是余额增加失败则提示用户联系技术人员操作增加{@see onFailContactTech}
   * @param pay_price
   */
  doBalanceRecharge: function (pay_price = 0.01) {
    balanceCharge(pay_price, () => {
      changeUserBalance(pay_price, () => {
        wx.showToast({
          title: '充值成功',
          duration: 500
        })
        this.setData({
          balance: this.data.balance + pay_price
        })
      }, onFailContactTech)
    })
  },
  /**
   * cancelRechargeBalance 隐藏金额输入的模态框
   */
  cancelRechargeBalance: function(){
    this.setData({
      hiddenBalanceRecharge: true,
      balance_recharge_amount: ""
    })
  },
  /**
   * toRechargeSms 根据用户选择的按量购买或者短信包进入下一步的操作
   */
  toRechargeSms: function () {
    wx.showActionSheet({
      itemList: ['按量计费', '优惠短信包'],
      success: (res) => {
        let idx = res.tapIndex
        let product_id = idx ? globalData.smsPkgProductId : globalData.smsProductId
        let product_name = idx ? '短信包' : '短信'
        wx.request({
          url: app.buildUrl('/order/sp/has'),
          header: app.getRequestHeader(),
          data: {
            product_id: product_id
          },
          success: res => {
            let has = res.data['has']
            if (has) {
              remindOldOrder(product_name, this)
            } else {
              doGetNewProduct(product_name, this)
            }
          },
          fail: res => {
            app.serverBusy()
          }
        })
      }
    })
  },
  /**
   * listenSmsCnt 监听用户输入购买的短信条数
   * @param e
   */
  listenSmsCnt: function(e){
    this.data.sms_num = e.detail.value
  },
  /**
   * confirmSmsTimes 确定购买指定条数的短信
   * @param e
   */
  confirmSmsTimes: function(e){
    let num = parseInt(this.data.sms_num);
    if (num > 0) {
      //购买数量大于0，才继续
      let data = {
        type: 'toBuy',
        goods: [{'id': app.globalData.smsProductId, 'price': app.globalData.smsProductPrice, 'number': num}]
      }
      toOrderSpecialProduct(data)
    }
    this.cancelSmsTimes()
  },
  /**
   * cancelSmsTimes 关闭短信购买数量的盒子
   */
  cancelSmsTimes: function(){
    this.setData({
      hiddenSmsTimesModal: true,
      sms_num: ""
    })
  },
  confirmSmsPkg: function(){
    let data = {
      type: 'toBuy',
      goods: [{'id': app.globalData.smsPkgProductId, 'price': app.globalData.smsPkgProductPrice, 'number': 1}]
    }
    toOrderSpecialProduct(data)
    this.setData({
      hiddenSmsPkgModal: true
    })
  },
  cancelSmsPkg: function(){
    this.setData({
      hiddenSmsPkgModal: true
    })
  },
  toIntroduce: function () {
    this.setData({
      hiddenIntroduceModal: false
    })
  },
  cancelIntroduce: function(){
    //停止播放并隐藏模态框
    setTimeout(()=>{
      this.setData({
        hiddenIntroduceModal: true
      })
    }, 580)
  },
  toEditPhone: function () {
    wx.navigateTo({
      url: '/pages/Qrcode/Mobile/index'
    });
    this.cancelMobileEdit()
  },
  toLookupSms: function () {
    this.setData({
      hiddenSmsDetailModal: false
    })
  },
  smsTips: function() {
    let content = '';
    if (this.data.userInfo.has_qrcode){
      content = '如果你有二维码，但是没有短信条数，且账户余额不足1毛。当发生扫码归还时，你将收不到系统及时的短信通知。'
    } else {
      content = '获取二维码，系统赠送你免费的5条短信哦！'
    }
    app.alert({
      title: '短信提示',
      content: content
    })
  },
  closeSmsDetail: function () {
    this.setData({
      hiddenSmsDetailModal: true
    })
  }
})