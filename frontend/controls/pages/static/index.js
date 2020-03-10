// pages/jmall/my/controls/static/index.js
var app=getApp();
Page({
  data: {

  },
  onLoad: function (options) {
    var that=this;
    wx.request({
            url: app.buildUrl("/static/num"),
            header: app.getRequestHeader(),
            success: function (res) {
                wx.showToast({
                    title: '加载成功',
                    content: '加载统计数据成功！',
                    duration: 2000
                });
                that.setData({
                  items:res.data.data.items
                });
            }
        })
  }
});