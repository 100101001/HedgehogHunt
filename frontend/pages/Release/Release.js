var app=getApp();
var util = require("../../utils/util.js");
Page({
  onLoad: function(event) {
    //设置底部导航栏
    var [isSelecteds, urls] = util.onNavigateTap(2);
    var total_new = app.globalData.total_new;
    isSelecteds['total_new'] = total_new;
    this.setData({
      isSelecteds: isSelecteds,
    });
  },

  onNavigateTap: function(event) {
    app.getNewRecommend();
    var id = event.currentTarget.dataset.id * 1; //乘1强制转换成数字
    var [isSelecteds, urls] = util.onNavigateTap(id, 2);
    this.setData({
      isSelecteds: isSelecteds
    })
    wx.redirectTo({
      url: urls[id],
    })
  },

  onFindTap: function(event) {
    var regFlag = app.globalData.regFlag;
    var token = wx.getStorageSync('token')
    if (!regFlag && token == "") {
      app.loginTip();
      return;
    }
    wx.navigateTo({
      url: 'release/index?business_type=1',
    })
  },

  onLostTap: function(event) {
    var regFlag = app.globalData.regFlag;
    var token = wx.getStorageSync('token')
    console.log(token)
    if (!regFlag && token == "") {
      app.loginTip();
      return;
    }
    wx.navigateTo({
      url: 'release/index?business_type=0',
    })
  }
})