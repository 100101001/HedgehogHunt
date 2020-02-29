var util = require("../../utils/util.js");
var app = getApp();
Page({
  data: {
    isHide: false,
    thanks_text: "",
    items: [
      { "name": 0, value: "0元", price: 0, checked: "true" },
      { "name": 1, value: "0.5元", price: 0.5 },
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
      data: data
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
    value = value.replace(/[^\d)]/g, '')
    console.log(value)
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

    //取出答谢金额
    var items = this.data.items
    var checkedRadio = this.data.checkedRadio
    var price = this.data.price
    price = checkedRadio == 3 ? price : items[checkedRadio]['price']

    if (price == 0) {
      //纯文字感谢
      this.createThank(price)
    } else {
      //红包加文字感谢
      var that = this
      //后端下支付单
      wx.request({
        'url': app.buildUrl('/thank/order/place'),
        'header': app.getRequestHeader(),
        'method': 'POST',
        'data': {
          'price': price
        },
        'success': function (res) {
          console.log(res)
          if (res.code == 200) {
            //前端微信支付
            data = res.data
            wx.requestPayment({
              timeStamp: data['timeStamp'],
              nonceStr: data['nonceStr'],
              package: data['package'],
              signType: data['signType'],
              paySign: data['paySign'],
              complete: function (res) {
                //后端查询支付状态
                wx.request({
                  url: app.buildUrl('/thank/order/query'),
                  method: 'post',
                  header: app.getRequestHeader(),
                  success: function (res) {
                    resp = res.data
                    if (resp.code == 200) {
                      that.createThank(price, resp.data.order_id)
                    } else {
                      app.alert({ 'content': resp.msg })
                    }
                  },
                  fail: function (res) {
                    app.alert({ 'content': res.data.msg })
                  }
                })
              }
            })
          } else {
            wx.showToast({ title: JSON.stringify(data['msg']), icon: 'none' })
          }
        },
        'fail': function (res) {
          console.log(res)
        }
      })
    }
  },
  //支付单id默认为空
  createThank: function (price, order_id = "") {
    var thanks_text = this.data.thanks_text;
    var data = this.data.data;
    data['price'] = price;
    data['thanks_text'] = thanks_text;
    data['order_id'] = order_id
    console.log(data);
    var that = this;
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
          complete:function(){
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