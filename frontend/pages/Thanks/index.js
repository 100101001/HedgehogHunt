var util = require("../../utils/util.js");
var app = getApp();
Page({
  data: {
    isHide: false,
    thanks_text: "",
    price: 0
  },
  onLoad: function(options) {
    var data = JSON.parse(options.data)
    this.setData({
      data: data
    })
  },
  goHome: function(e) {
    wx.navigateTo({
      url: "../Find/Find?business_type=1",
    })
  },
  listenerTextInput: function(e) {
    this.setData({
      thanks_text: e.detail.value
    });
  },
  moneyThanks(e) {
    app.alert({
      'content': '调起微信支付'
    });
  },
  subMit: function(e) {
    var thanks_text = this.data.thanks_text;
    var data = this.data.data;
    data['price'] = 0;
    data['thanks_text'] = thanks_text;
    console.log(data);
    var that=this;
    wx.request({
      url: app.buildUrl("/thanks/create"),
      header: app.getRequestHeader(),
      data:data,
      success: function(res) {
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
          duration: 2000
        });
        that.goHome();
      },
      fail: function(res) {
        wx.hideLoading();
        wx.showToast({
          title: '系统繁忙，反馈失败！',
          duration: 2000
        });
        app.serverBusy();
        return;
      }
    });
  }
})