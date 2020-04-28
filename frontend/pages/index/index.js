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
    isScanQrcode: true,
    isLogging: true
  },
  /**
   * goToIndex
   * 点击首页逛一逛，如果用户状态为封锁，就进入不了
   */
  goToIndex: function () {
    let member_status = app.globalData.member_status;
    let id = app.globalData.id;
    if (member_status !== 1) {
      app.alert({
        title: '封号告示',
        content: '因恶意操作，您的账号已被封锁。如有异议点击确定查看详情和进行申诉。',
        showCancel: true,
        cb_confirm: ()=>{
          wx.navigateTo({url: '/controls/pages/blockmember/more_record/index?op_status=1&id='+id})
        }
      });
      return
    }
    this.setData({
      member_status: member_status
    });
    wx.navigateTo({
      url: '/pages/Homepage/index',
    })
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
      app.globalData.indexPage = this;
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
