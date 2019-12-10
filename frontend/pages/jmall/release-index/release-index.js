// pages/jmall/release-index/release-index.js
var app = getApp();
Page({
  data: {

  },
  onLoad: function(options) {

  },
  goSell: function() {
    var regFlag = app.globalData.regFlag;
    if (!regFlag) {
      app.loginTip();
      return;
    } else {
      wx.navigateTo({
        url: '../release/index?business_type=1',
      })
    }
  },
  goBuy: function() {
    var regFlag = app.globalData.regFlag;
    if (!regFlag) {
      app.loginTip();
      return;
    } else {
      wx.navigateTo({
        url: '../release/index?business_type=0',
      })
    }
  },

})