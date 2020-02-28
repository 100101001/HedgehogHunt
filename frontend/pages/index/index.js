//login.js
//获取应用实例
var app = getApp();
Page({
  data: {
    remind: '加载中',
    angle: 0,
    userInfo: {},
    member_status: 1,
    goods_id: 0,
    isScanQrcode: true
  },
  goToIndex: function () {
    var goods_id = this.data.goods_id;
    var member_status = app.globalData.member_status;
    if (member_status == 0) {
      return
    }
    /****(member_)id干什么用的？？***/
    var id = app.globalData.id;
    this.setData({
      member_status: member_status,
    })
    if (id) {
      this.setData({
        id: id
      })
    }
    /****(member_)id干什么用的？？***/
    if (goods_id) {
      wx.redirectTo({
        url: '/pages/Find/info?goods_id=' + goods_id,
      })
    } else {
      wx.redirectTo({
        url: '/pages/Find/Find?business_type=1',
      })
    }
  },
  //****************************************************
  //               韦朝旭调试
  onLoad: function (options) {
    wx.setNavigationBarTitle({
      title: app.globalData.shopName
    })
    /***********扫二维码开始******************/
    var openid = this.getOpenId(options)
    if (openid == null) {
      this.setData({
        isScanQrcode: false
      })
      // 无二维码==>走韦朝旭代码
      app.checkLogin();
      app.getNewRecommend();
      // 去默认首页
      //this.goToIndex()
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
      wx.showActionSheet({
        itemList: ['绑定手机号', '更换手机号', '随便扫扫'],
        success(res) {
          if (res.tapIndex < 2) {
            wx.redirectTo({
              url: "/pages/Qrcode/Mobile/index?openid=" + openid
            })
          }
        },
        fail: res => {
          this.setData({
            isScanQrcode: false
          })
        }
      })
    } else {
      //别人扫码发布帖子，通知失主
      wx.redirectTo({
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
