const app = getApp();
const util = require('../../../utils/util')
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


const balanceCharge = function (pay_price=0.01, cb_success=()=>{}) {
  wx.request({
    url: app.buildUrl('/balance/order'),
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
 * 扣除(改变)用户余额
 * @param unit 改变量
 * @param cb_success 回调函数
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


Page({
  data: {
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
    contact_img: app.globalData.static_file_domain + "/static/QRcode.jpg",
    intro_url: app.globalData.static_file_domain+ "/static/introduce.mp4",
    intro_init_time: 0, //
    balance_recharge_amount: "",
    sms_num: "",
    sms_pkg_price: app.globalData.smsPkgProductPrice
  },
  onLoad: function () {
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
        let resp = res.data
        if (resp['code'] !== 200) {
          app.alert({
            content: resp['msg'],
            cb_confirm: () => {
              wx.navigateBack()
            }
          })
          return
        }
        let info = resp['data']['info']
        this.setData({
          avatar: info['avatar'],
          nickname: info['nickname'],
          name: info['name'],
          mobile: info['mobile'],
          balance: util.toFixed(info['balance'],2),
          has_qrcode: info['has_qrcode'],
          qr_code: info['qr_code'],
          member_notify_times: info['m_times'],
          pkg_notify_times: info['p_times'],
          total_notify_times: info['m_times'] + info['p_times'],
          pkg_expire: info['p_expire']
        })
      },
      fail: (res) => {
        app.serverBusy(()=>{wx.navigateBack()})
      }
    })
  },
  onEditMobile: function () {
    this.setData({
      hiddenMobileModal: false
    })
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
      duraton: duraton,
      mask: mask
    })
  },
  confirmNameEdit: function (e) {
    if (this.data.editName == "") {
      app.alert({
        'content': '姓名不能为空'
      })
      return
    }
    if (this.data.name == this.data.editName) {
      this.showToast('请填不同姓名!', 'none')
      return
    }
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
          name: resp.data.name,
          hiddenNameModal: true
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
   * toGetQrCode 判断没有姓名或手机号提示用户补上，否则继续下单获取二维码
   */
  toGetQrCode: function(){
    let name = this.data.name
    let mobile = this.data.mobile
    if (!name) {
      app.alert({ 'content': '姓名不能为空' })
      return
    }
    if (!mobile) {
      app.alert({ 'content': '手机不能为空' })
      return
    }
    this.doGetQrCode()
  },
  /***
   * doGetQrCode 去下单获取二维码
   */
  doGetQrCode: function () {
    //下单
    let data = {
      type: 'toBuy',
      goods: [{'id': app.globalData.qrcodeProductId, 'price': app.globalData.qrcodePrice, 'number': 1}]
    }
    toOrderSpecialProduct(data)
  },
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
   *
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
    this.setData({
      hiddenBalanceRecharge: false
    })
  },
  listenBalanceRecharge: function(e){
    this.data.balance_recharge_amount = e.detail.value
  },
  /**
   * confirmRechargeBalance 与用户核对充值收费金额
   * 如果用户确认就继续进入收费充值过程
   * 否则，终止操作
   */
  confirmRechargeBalance: function(){
    if(!this.data.balance_recharge_amount){
      this.cancelRechargeBalance()
      return
    }
    let pay_price = util.toFixed(this.data.balance_recharge_amount*1.01, 2)
    if(!pay_price) {
      this.cancelRechargeBalance()
      return
    }

    console.log(pay_price)
    app.alert({
      title: '充值确认',
      content: '您需要支付'+pay_price+'元，确认充值？',
      showCancel: true,
      cb_confirm: ()=>{
        this.doBalanceRecharge(pay_price)
        this.cancelRechargeBalance() //隐藏输入金额的模态框
      },
      cb_cancel: this.cancelRechargeBalance() //隐藏金额输入的模态框
    })
  },
  /**
   * doBalanceRecharge 充值余额的实际操作函数
   * 先收费，如果支付成功增加余额，
   * 如果收费成功但是余额增加失败则提示用户联系技术人员操作增加
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
      }, () => {
        app.alert({
          title: '跳转提示',
          content: '联系技术人员充值余额',
          cb_confirm: () => {
            wx.navigateTo({url: '/pages/Mine/connect/index'})
          }
        })
      })
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
  toRechargeSms: function(){
    wx.showActionSheet({
      itemList: ['按量计费', '优惠短信包'],
      success: (res) => {
        if(res.tapIndex == 0){
          //出现编辑购买条数
          app.alert({
            title: '计价提示',
            content: '0.1元/1条。继续购买？',
            showCancel: true,
            cb_confirm: ()=>{
              this.setData({
                hiddenSmsTimesModal: false
              })
            }
          })
        } else {
          //直接跳转下单
          this.setData({
            hiddenSmsPkgModal: false
          })
        }
      }
    })
  },
  listenSmsCnt: function(e){
    this.data.sms_num = e.detail.value
  },
  /**
   * 确定购买指定条数的短信
   * @param e
   */
  confirmSmsTimes: function(e){
    let data = {
      type: 'toBuy',
      goods: [{'id': app.globalData.smsProductId, 'price': app.globalData.smsProductPrice, 'number': parseInt(this.data.sms_num)}]
    }
    toOrderSpecialProduct(data)
    this.setData({
      hiddenSmsTimesModal: true
    })
  },
  /**
   * 取消购买指定条数的短信
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
    this.setData({
      hiddenIntroduceModal: true
    })
  },
  toEditPhone: function () {
    wx.navigateTo({
      url: '/pages/Qrcode/Mobile/index'
    })
    this.cancelMobileEdit()
  },
  toLookupSms: function () {
    // let pkg_times = this.data.pkg_notify_times
    // let m_times = this.data.member_notify_times
    // wx.showModal({
    //   title: '次数明细',
    //   content: (pkg_times?  pkg_times+'条至'+this.data.pkg_expire+'。' : '') + (m_times? '不限期'+m_times+'条。':'')
    // })
    this.setData({
      hiddenSmsDetailModal: false
    })
  },
  closeSmsDetail: function () {
    this.setData({
      hiddenSmsDetailModal: true
    })
  }
})