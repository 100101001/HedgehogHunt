var goodsData = require("../../../data/posts-data.js");
var util = require("../../../utils/util.js");
Page({
  data: {},
  onLoad: function(options) {
    var id = options.id;
    this.setData({
      goodsDetail: goodsData.goodsList[id]
    })
  },

  //点击联系之后
  onConnectTap: function(event) {
    util.showMessage('点击联系', '需要让用户自己联系吗？存在诈骗风险');
  },

  onShareTap: function(event) {
    var itemList = [
      "分享给微信好友",
      "分享到朋友圈",
      "分享到QQ",
      "分享到微博"
    ]
    wx.showActionSheet({
      itemList: itemList,
      itemColor: "#405f80",
      success: function(res) {
        //res.cancel
        //res.tapIndex
        util.showMessage('用户 ' + itemList[res.tapIndex], res.cancel ? "取消分享" : "分享成功");
      }
    })
  },

  onLocateTap: function(event) {
    wx.openLocation({
      latitude: 31.2854,
      longitude: 121.49854,
      scale: 14
    })
  }
})