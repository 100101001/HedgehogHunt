//login.js
//获取应用实例
const app = getApp();

Page({
  data: {
    remind: '加载中',
    angle: 0,
    userInfo: {},
    member_status: 1,
    goods_id: 0,
    isScanQrcode: true
  },
  /**
   * goToIndex
   * 点击首页逛一逛，如果用户状态为封锁，就进入不了
   */
  goToIndex: function () {
    let goods_id = this.data.goods_id;
    let member_status = app.globalData.member_status;
    if (member_status == 0) {
      return
    }
    let id = app.globalData.id;
    this.setData({
      member_status: member_status,
    })
    if (id) {
      this.setData({
        id: id
      })
    }
    /****(member_id干什么用的？？***/
    if (goods_id) {
      wx.navigateTo({
        url: '/pages/Find/info?goods_id=' + goods_id,
      })
    } else {
      wx.navigateTo({
        url: '/pages/Homepage/index',
      })
    }
  },
  onLoad: function (options) {
    wx.setNavigationBarTitle({
      title: app.globalData.shopName
    });
    /***********扫二维码开始******************/
    let openid = this.getOpenId(options);
    if (!openid) {
      this.setData({
        isScanQrcode: false
      });
      app.globalData.isScanQrcode = false;
      app.globalData.qrcodeOpenid = "";
    } else {
      //有二维码
      this.setData({
        isScanQrcode: true
      });
      app.globalData.indexPage = this;
      app.globalData.isScanQrcode = true;
      app.globalData.qrcodeOpenid = openid;
    }
    app.login();
    app.getNewRecommend();
    /****************扫二维码结束******************/
  },
  getOpenId: function (options) {
    if (app.globalData.qrCodeDebug) {
      return options.openid
    } else {
      if (options.scene) {
        return options.scene
      }
      return null
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
