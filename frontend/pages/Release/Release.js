const navigate = require("../template/navigate-bar/navigate-bar-template.js")
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
    navigate.onNavigateTap(event, this)
  },

  onFindTap: function(event) {
    wx.navigateTo({
      url: 'release/index?business_type=1',
    })
  },

  onLostTap: function(event) {
    wx.navigateTo({
      url: 'release/index?business_type=0',
    })
  }
})