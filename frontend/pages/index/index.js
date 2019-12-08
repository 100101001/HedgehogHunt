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
  test: function () {
    wx.request({
      url: app.buildUrl("/test"),
      header: app.getRequestHeader(),
      success: function (res) { }
    })
  },
  onLoad: function (options) {
    //this.test();
    wx.setNavigationBarTitle({
      title: app.globalData.shopName
    });
    app.checkLogin();
    app.getNewRecommend();
    this.goToIndex();

    //later will use index page for redirect
    if (options.id) {
      wx.navigateTo({
        url: "/pages/Qrcode/index?id=" + options.id
      })
      wx.request({
        method: 'post',
        url: app.buildUrl("/qrcode/scan"),
        data: {
          id: options.id
        },
        success: function (res) {
          if (res.data == true) {
            wx.navigateTo({
              url: "/pages/Release/release/index"
            })
          } else {
            wx.navigateTo({
              url: "/pages/Qrcode/Register/index"
            })
          }
        },
        fail: function (res) {
          app.serverBusy()
        }
      })
    } else {
      //comment code for debug scan qrcode
      //this.goToIndex();
    }

    //only for debug scan qr code
    wx.navigateTo({
      url: "/pages/Qrcode/index?id=" + 1
    })

    //this.goToIndex();
    // var goods_id = options.goods_id;
    // if (goods_id) {
    //   this.setData({
    //     goods_id: goods_id,
    //   })
    // }
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