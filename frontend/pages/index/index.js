//login.js
//获取应用实例
var app = getApp();
Page({
  data: {
    remind: '加载中',
    angle: 0,
    userInfo: {},
    member_status: 1,
    goods_id: 0
  },
  goToIndex: function () {
    var goods_id = this.data.goods_id;
    var member_status = app.globalData.member_status;
    if (member_status == 0) {
      return;
    }
    var id = app.globalData.id;
    this.setData({
      member_status: member_status,
    });
    if (id) {
      this.setData({
        id: id
      });
    }
    if (goods_id) {
      wx.navigateTo({
        url: '/pages/Find/info?goods_id=' + goods_id,
      });
    } else {
      wx.navigateTo({
        url: '/pages/Find/Find?business_type=1',
      });
    }
  },
  //****************************************************
  //               韦朝旭调试
  onLoad: function (options) {
    /***********扫二维码开始********/
    var openid = this.getOpenId(options)
    if (openid == null) {
      // 无二维码
      wx.setNavigationBarTitle({
        title: app.globalData.shopName
      });
      app.checkLogin();
      app.getNewRecommend();
      // 去默认首页
      this.goToIndex();
    } else {
      //有二维码
      app.checkLogin(this.qrCodeNavigate, openid);
    }
    /****************扫二维码结束******************/
  },
  getOpenId: function (options) {
    if (app.globalData.debug) {
      return options.openid
    } else {
      if (options.scene) {
        return decodeURIComponent(options.scene)
      }
      return null
    }
  },
  qrCodeNavigate: function (openid) {
    if (openid == app.globalData.openid) {
      //自己扫码更换绑定手机号
      wx.navigateTo({
        url: "/pages/Qrcode/Mobile/index?openid=" + openid
      })
    } else {
      //别人扫码发布帖子，通知失主
      wx.navigateTo({
        url: "/pages/Release/release/index?business_type=1&openid=" + openid
      })
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
