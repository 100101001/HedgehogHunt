
var app = getApp();
Page({
  data: {
    //判断小程序的API，回调，参数，组件等是否在当前版本可用。
    canIUse: wx.canIUse('button.open-type.getUserInfo') && wx.canIUse('button.open-type.getPhoneNumber'),
    isHide: false,
    getUserInfo: false,
    getPhone: true,
    loginInfo: null
  },

  onLoad: function (options) {
    var phone = options.phone
    if (phone == undefined) {
      var loginInfo = app.getCache("loginInfo")
      this.setData({
        loginInfo: loginInfo
      })
    } else {
      this.setData({
        getUserInfo: true,
        getPhone: false,
        mobile: phone
      })
    }
  },
  onShow: function () {
    if (app.globalData.regFlag && app.getCache("token") != "") {
      wx.navigateBack({})
    }
  },
  login: function (e) {
    if (e.detail.userInfo) {
      e.detail.userInfo['mobile'] = this.data.mobile
    }
    app.login(e);
  },
  getPhoneNumber(e) {
    var msg = e.detail.errMsg
    var that = this
    var session_key = that.data.loginInfo.session_key
    var encryptedData = e.detail.encryptedData
    var iv = e.detail.iv;
    if (msg == 'getPhoneNumber:ok') {
      wx.checkSession({
        success: function () {
          that.deciyption(session_key, encryptedData, iv);
        },
        fail: function (res) {
          wx.login({
            success: res => {
              wx.request({
                method: 'POST',
                url: app.buildUrl('/member/login/wx'),
                header: {
                  'content-type': 'application/json',
                },
                data: { code: res.code },
                success: function (res) {
                  var resp = res.data
                  if (resp.code !== 200) {
                    app.alert({
                      'content': resp.msg
                    })
                    return
                  }
                  var loginInfo = resp.data;
                  app.setCache('loginInfo', loginInfo);
                  that.setData({
                    loginInfo: loginInfo
                  });
                  that.deciyption(loginInfo.session_key, encryptedData, iv);
                }
              })
            }
          })
        }
      })
    }
  },
  deciyption(session_key, encryptedData, iv) {
    wx.request({
      method: 'POST',
      url: app.buildUrl('/member/phone/decrypt'),
      header: {
        'content-type': 'application/json',
      },
      data: {
        session_key: session_key,
        encrypted_data: encryptedData,
        iv: iv
      },
      success: function (res) {
        var resp = res.data
        if (resp.code !== 200) {
          app.alert({
            'content': resp.msg
          })
          return
        }
        wx.navigateTo({
          url: '/pages/login/index?phone=' + resp.data.mobile,
        })
      }
    })
  },
})