var util = require("../../utils/util.js");
var app=getApp();
Page({
  data: {
    isHide: false
  },

  onLoad: function () {
  },
  goHome: function (e) {
    wx.navigateTo({
      url: "../Find/Find",
    })
  },
  moneyThanks(e) {
    app.alert({
      'content':'调起微信支付'
    });
  },
  formSubmit: function (e) {
    var data = e.detail.value;
    console.log(data);
  }
})