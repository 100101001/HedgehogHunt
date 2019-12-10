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
    //this.goToIndex();

    // can be used by both of us, 
    // qrcodeId==null indicates not qrcode
    var qrcodeId = this.getQrcodeId(options)
    if (qrcodeId == null) {
      this.goToIndex();
    } else {
      wx.request({
        method: 'post',
        url: app.buildUrl("/qrcode/scan"),
        data: {
          id: qrcodeId
        },
        success: function (res) {
          if (res.data == true) {
            wx.navigateTo({
              url: "/pages/Release/release/index?qrcodeId=" + qrcodeId
            })
          } else {
            wx.navigateTo({
              url: "/pages/Qrcode/Register/index?qrcodeId=" + qrcodeId
            })
          }
        },
        fail: function (res) {
          app.serverBusy()
        }
      })
    }

    // var goods_id = options.goods_id;
    // if (goods_id) {
    //   this.setData({
    //     goods_id: goods_id,
    //   })
    // }
  },
  getQrcodeId: function (options) {
    if (app.globalData.debug) {
      return options.id
    } else {
      if (options.scene) {
        return decodeURIComponent(options.scene)
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
