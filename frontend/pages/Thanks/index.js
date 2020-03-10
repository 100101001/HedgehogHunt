var util = require("../../utils/util.js");
var app = getApp();
Page({
  data: {
    isHide: false,
    thanks_text: "",
    items: [
      { "name": 0, value: "0元", price: 0, checked: "true" },
      { "name": 1, value: "0.01元", price: 0.01 },
      { "name": 2, value: "1元", price: 1 },
      { "name": 3, value: "自定义", price: "" }
    ],
    checkedRadio: 0,
    price: "",
    canSendThank: false
  },
  onLoad: function (options) {
    var data = JSON.parse(options.data)
    this.setData({
      data: data,
      balance: app.globalData.memberInfo.balance
    })
  },
  listenerTextInput: function (e) {
    this.setData({
      thanks_text: e.detail.value
    });
  },
  listenerMoneyInput: function (e) {
    console.log(e)
    var value = e.detail.value
    value = value.replace(/[^\d.)]/g, '')
    this.setData({
      price: value
    })
  },
  radioChange: function (e) {
    var checkedRadio = e.detail.value
    var items = this.data.items
    for (var i = 0; i < items.length; i++) {
      items[i]['checked'] = i == checkedRadio
    }
    this.setData({
      checkedRadio: checkedRadio,
      items: items
    })
  },
  sendThank: function (e) {
    if(this.data.thanks_text == ""){
      app.alert({
        'title':'温馨提示',
        'content':'别忘了用文字传递感谢~'
      })
      return
    }
    //取出答谢金额，可能是自定义金额或者指定金额
    var price = this.data.price
    var items = this.data.items
    var checkedRadio = this.data.checkedRadio
    price = checkedRadio == 3 ? price : items[checkedRadio]['price']
    // 金额合法性检测
    var reg = /^[0-9]+([.]{1}[0-9]+){0,1}$/
    if (!reg.test(price)) {
      app.alert({
        'title': '温馨提示',
        'content': '请输入合法的钱数'
      })
      return
    }
    //分纯答谢和金额答谢
    //金额答谢分纯账户和混合付款
    if (price == 0) { 
      //纯文字感谢
      this.createThank(price)
    } else {
      //红包加文字感谢
      var balance = this.data.balance
      //答谢金额保留两位小数
      var pay = Math.round(price * 101) / 100
      //微信支付金额保留两位小数
      var wx_pay = Math.round((pay - balance)*100)/100
      var content = ''
      if (wx_pay <= 0) {
        //纯余额
        content = (pay == price ? '' : '由于微信手续费，') + '将从您的余额扣除' + pay + '元'
      } else {
        //余额加现金支付
        content = (pay == price ? '' : '由于微信手续费，') + 
                  (balance==0? '':'从您账户扣除余额后，')+'您需支付' + wx_pay + '元'
      }
      var that = this
      app.alert({
        'title': '温馨提示',
        'content': content,
        'showCancel': true,
        'cb_cancel': function(){

        },
        'cb_confirm': function () {
          //后端下支付单
          wx.request({
            'url': app.buildUrl('/thank/order/place'),
            'header': app.getRequestHeader(),
            'method': 'POST',
            'data': {
              'wx_price': wx_pay <= 0 ? 0 : wx_pay,
              'account_price': wx_pay <= 0 ? pay : balance,
              'pay_type': wx_pay <= 0 ? 'pure_balance' : 'mixed'
            },
            'success': function (res) {
              console.log(res)
              var resp = res.data
              if (resp.code !== 200) {
                app.alert({
                  'content': resp.msg
                })
                return
              }
              //更新账户余额
              var data = resp.data
              app.globalData.memberInfo.balance = data.balance
              //纯账户扣款直接转入对方余额
              if (resp.data.pay_type == "pure_balance") {
                that.createThank(pay)
                return
              }
              //发起微信支付
              wx.requestPayment({
                timeStamp: data['timeStamp'],
                nonceStr: data['nonceStr'],
                package: data['package'],
                signType: data['signType'],
                paySign: data['paySign'],
                complete: function (res) {
                  console.log(res)
                  //取消支付
                  if (res.errMsg == "requestPayment:fail cancel") {
                    //用户取消了支付，且没有余额，不询问
                    if (balance <= 0) {
                      wx.showToast({
                        title: '答谢失败',
                        duration: 1200,
                      })
                      return
                    }
                    //用户取消了支付，询问余额是退还还是只用余额答谢
                    app.alert({
                      'title': '是否终止答谢',
                      'content': "取消将仅用账户余额答谢",
                      'showCancel': true,
                      'cb_confirm': function () {
                        //支付是因为余额全扣了也不够
                        that.setBalance(balance)
                      },
                      'cb_cancel': function () {
                        //支付是因为余额全扣了也不够，所以余额全给别人，等于纯余额答谢
                        that.createThank(balance)
                      }
                    })
                  }
                  //支付成功
                  if (res.errMsg == "requestPayment:ok") {
                    that.createThank(pay, data.order_sn)
                    return
                  }
                }
              })
            },
            'fail': function (res) {
              //无响应
              app.serverBusy()
            }
          })
        }
      })
    }
  },
  setBalance: function (amount = 0) {
    var that = this
    wx.request({
      url: app.buildUrl('/thank/balance/rollback'),
      method: 'post',
      header: app.getRequestHeader(),
      data: {
        amount: amount
      },
      success: function (res) {
        var resp = res.data
        if (resp.code !== 200) {
          app.alert({ 'content': '请联系开发者索要扣除的余额' })
          return
        }
        var data = resp.data
        app.globalData.memberInfo.balance = data.balance
        that.goHome()
      }
    })
  },
  //支付单id默认为空
  createThank: function (price, order_sn = 'no') {
    var thanks_text = this.data.thanks_text;
    var data = this.data.data;
    data['target_price'] = price;
    data['thanks_text'] = thanks_text;
    data['order_sn'] = order_sn
    //答谢用户的名字
    data['owner_name'] = app.globalData.memberInfo.nickname
    var that = this
    //后端创建感谢记录
    wx.request({
      url: app.buildUrl("/thanks/create"),
      header: app.getRequestHeader(),
      data: data,
      success: function (res) {
        var resp = res.data;
        if (resp.code !== 200) {
          app.alert({
            'content': resp.msg
          });
          return
        }
        wx.hideLoading();
        wx.showToast({
          title: '答谢成功！',
          icon: 'success',
          duration: 2000,
          complete: function () {
            that.goHome()
          }
        })
      },
      fail: function (res) {
        wx.hideLoading();
        wx.showToast({
          title: '系统繁忙，反馈失败！',
          duration: 2000
        });
        app.serverBusy();
        return;
      }
    });
  },
  goHome: function (e) {
    wx.reLaunch({
      url: "../Find/Find?business_type=1",
    })
  }
})