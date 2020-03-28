const util = require('../../utils/util')
const useBalance = require("../template/use-balance/use-balance.js")
const app = getApp();


/**
 * thankPay
 * 答谢支付
 * @param pay_price 答谢价格
 * @param cb_success 回调函数
 * @param that 页面指针
 */
const thankPay = function (pay_price=app.globalData.goodsTopPrice, cb_success=()=>{}, that) {
  wx.request({
    url: app.buildUrl('/thank/order'),
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
        that.setData({
          canSendThank: true
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
          cb_success(pay_data['thank_order_sn'])
        },
        fail: res => {
          that.setData({
            canSendThank: true
          })
        }
      })
    },
    fail: res => {
      app.serverBusy()
      that.setData({
        canSendThank: true
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
      note: "答谢支付"
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
    isHide: false,
    thanks_text: "",
    items: [
      {"name": 0, value: "0元", price: 0, checked: "true"},
      {"name": 1, value: "0.5元", price: 0.5},
      {"name": 2, value: "1元", price: 1},
      {"name": 3, value: "自定义", price: ""}
    ],
    checkedRadio: 0,
    price: "",
    canSendThank: true,
    use_balance: false, //使用余额
    balance_got: false, //数据正确加载，向用户显示勾选框
    balance_use_disabled: true, //禁用余额勾选框
    balance: 0.00, //用户可垫付余额
    total_balance: 0.00  //用户余额
  },
  onLoad: function (options) {
    let data = JSON.parse(options.data)
    this.setData({
      data: data
    })
  },
  onShow: function () {
    useBalance.initData(this, (total_balance)=>{
      this.setData({
        balance_use_disabled: true
      })
    })
  },
  listenerTextInput: function (e) {
    this.setData({
      thanks_text: e.detail.value
    })
  },
  listenerMoneyInput: function (e) {
    this.setData({
      price: e.detail.value
    })
    //计算可用余额
    let pay_money = util.toFixed(parseFloat(e.detail.value)*1.01, 2)
    if(pay_money<=this.data.total_balance){
      //余额足够
      this.setData({
        balance: pay_money //可用余额
      })
    } else {
      //余额不够
      this.setData({
        balance: this.data.total_balance //全用
      })
    }
  },
  /**
   * 自定义了0元时，禁用选项
   * @param e
   */
  confirmMoneyInput: function (e) {
    if (!util.toFixed(parseFloat(e.detail.value), 2)) {
      this.setData({
        balance_use_disabled: true,
        use_balance: false
      })
    }
  },
  /**
   * radioChange
   * 选择答谢钱数，如果选择了0元，或者自定义且输入了0元，则禁用使用余额的选项，并重置为不使用余额
   * @param e
   */
  radioChange: function (e) {
    let checkedRadio = e.detail.value
    let items = this.data.items
    for (let i = 0; i < items.length; i++) {
      items[i]['checked'] = i == checkedRadio
    }
    this.setData({
      checkedRadio: checkedRadio,
      items: items,
      balance_use_disabled: checkedRadio == 0,
      use_balance: checkedRadio == 0 ? false : this.data.use_balance
    })
    //计算可用余额
    if(checkedRadio != 3 && checkedRadio!=0){
      //没有选择0元和自定义
      let pay_price = util.toFixed(items[checkedRadio].price*1.01, 2)
      if(pay_price<=this.data.total_balance) {
        this.setData({
          balance: pay_price
        })
      } else {
        this.setData({
          balance: this.data.total_balance
        })
      }
    }else{
      this.setData({
        balance: 0
      })
    }
  },
  toSendThanks: function (e) {
    this.setData({canSendThank: false})
    if (this.data.thanks_text == "") {
      app.alert({
        title: '温馨提示',
        content: '别忘了用文字传递感谢~'
      })
      this.setData({canSendThank: true})
      return
    }
    //取出答谢金额，可能是自定义金额或者指定金额
    let price = this.data.price
    let checkedRadio = this.data.checkedRadio
    price = checkedRadio == 3 ? price : this.data.items[checkedRadio]['price']
    // 金额合法性检测
    if (!/^[0-9]+([.][0-9]+)?$/.test(price)) {
      app.alert({
        title: '温馨提示',
        content: '请输入合法的钱数'
      })
      this.setData({canSendThank: true})
      return
    }
    this.data.thank_price = util.toFixed(price, 2)
    this.doSendThanks()
  },
  doSendThanks: function () {
    //分纯答谢和金额答谢
    //金额答谢分纯账户和混合付款
    let thanks_price = this.data.thank_price
    if (thanks_price == 0) {
      //纯文字感谢
      this.createThanks(0.00)
    } else {
      if (this.data.use_balance) {
        this.toThankPayWithBalance()
      } else {
        this.toThankPayWithoutBalance(thanks_price)
      }
    }
  },
  toThankPayWithoutBalance: function (thanks_price = 0) {
    let thank_price = this.data.thank_price
    let total_pay = this.data.total_pay = util.toFixed(this.data.thank_price*1.01, 2)
    app.alert({
      title: '扣费提示',
      content: (total_pay == thank_price ? '' : '由于微信手续费，') + '您需支付' + total_pay + '元。',
      showCancel: true,
      cb_confirm: () => {
        //后端下支付单
        this.doThankPayWithoutBalance()
      }
    })
  },
  /**
   * doThankPayWithoutBalance
   * 纯支付
   */
  doThankPayWithoutBalance: function(){
    thankPay(this.data.total_pay, (order_sn) => {
      this.createThanks(this.data.thank_price, order_sn)
    }, this)
  },
  /**
   * toThankPayWithBalance 借用余额支付酬金，支付前进行支付金额核对
   * 分为纯从账户扣和另需要支付
   */
  toThankPayWithBalance: function() {
    let thank_price = this.data.thank_price
    let total_pay = this.data.total_pay = util.toFixed((thank_price * 1.01), 2)
    let fee_hint_content = ""
    let balance = this.data.balance
    if (total_pay <= balance) {
      //纯余额支付
      fee_hint_content = (total_pay == thank_price ? '' : '由于微信手续费，') + '将从您的余额扣除' + total_pay + '元。'
    } else {
      //支付+余额
      let pay_price = util.toFixed(total_pay - balance, 2)
      fee_hint_content = (total_pay == thank_price ? '' : '由于微信手续费，') +
        '从账户扣除' + balance + '元后，您需支付' + pay_price + '元。'
    }
    app.alert({
      title: '扣费提示',
      content: fee_hint_content,
      showCancel: true,
      cb_confirm: () => {
        //后端下支付单
        this.doThankPayWithBalance()
      },
      cb_cancel: ()=>{
        this.setData({canSendThank: true})
      }
    })
  },
  /**
   * doThankPayWithBalance 勾选余额垫付的答谢支付实际处理函数
   */
  doThankPayWithBalance: function () {
    let total_pay = this.data.total_pay
    let balance = this.data.balance
    let thank_price = this.data.thank_price
    if (total_pay <= balance) {
      //纯余额支付
      changeUserBalance(-total_pay, () => {
        this.createThanks(thank_price)
      })
    } else {
      //先支付后再扣除余额
      let pay_price = util.toFixed(total_pay - balance, 2)
      thankPay(pay_price, (order_sn) => {
        console.log(order_sn)
        changeUserBalance(-balance, () => {
          console.log(order_sn)
          this.createThanks(thank_price, order_sn)
        })
      }, this)
    }
  },
  /**
   * 创建答谢记录
   * @param price 答谢金
   * @param order_sn 答谢订单
   */
  createThanks: function (price, order_sn = 'no') {
    let data = this.data.data
    data['target_price'] = price
    data['thanks_text'] = this.data.thanks_text
    data['order_sn'] = order_sn
    //后端创建感谢记录
    this.doCreateThanks(data)
  },
  doCreateThanks: function (data = {}) {
    wx.request({
      url: app.buildUrl("/thanks/create"),
      header: app.getRequestHeader(),
      data: data,
      success: (res) => {
        let resp = res.data;
        if (resp['code'] !== 200) {
          app.alert({
            content: resp['msg']
          })
          this.setData({canSendThank: true})
          return
        }
        this.setInitData()
        wx.showToast({
          title: '答谢成功！',
          icon: 'success',
          duration: 700,
          complete: () => {
            setTimeout(() => {
              this.goHome()
            }, 500)
          }
        })
      },
      fail: (res) => {
        app.serverBusy()
        this.setData({canSendThank: true})
      }
    })
  },
  setInitData: function () {
    this.setData({
      use_balance: false,
      thanks_text: ''
    })
  },
  goHome: function (e) {
    wx.reLaunch({
      url: "../Find/Find?business_type=1",
    })
  },
  changeUseBalance: function (e) {
    useBalance.changeUseBalance(e, () => {
      this.setData({
        use_balance: e.detail.value.length == 1
      })
    })
  }
})