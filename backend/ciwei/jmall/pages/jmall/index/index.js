//login.js
//获取应用实例
var app = getApp();
Page({
    data: {
        remind: '加载中',
        angle: 0,
        userInfo: {},
    },
    goToIndex: function () {
        wx.switchTab({
            url: '/pages/jmall/goods/index',
        });
    },
    onLoad: function (options) {
      wx.setNavigationBarTitle({
        title: app.globalData.shopName
      });
      app.checkLogin();
      var goods_id=options.goods;
      if (goods_id){
      wx.navigateTo({
        url: '/pages/jmall/goods/info?goods_id='+goods_id,
      })
      }
      else{
       
      }
    },
    onShow: function () {
      
    },
    onReady: function () {
        var that = this;
        setTimeout(function () {
            that.setData({
                remind: ''
            });
        }, 1000);
        wx.onAccelerometerChange(function (res) {
            var angle = -(res.x * 30).toFixed(1);
            if (angle > 14) {
                angle = 14;
            } else if (angle < -14) {
                angle = -14;
            }
            if (that.data.angle !== angle) {
                that.setData({
                    angle: angle
                });
            }
        });
    },
});