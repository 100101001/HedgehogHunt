
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
  //如果进入页面时没有手机号，则设置先获取手机号
  onLoad: function (options) {
    wx.checkSession({
      fail: (res) => {
        wx.login({
          success: res => {
            wx.request({
              method: 'POST',
              url: app.buildUrl('/member/login/wx'),
              header: {
                'content-type': 'application/json',
              },
              data: { code: res.code },
              success: res => {
                app.setCache("loginInfo", res.data.data)
              }
            })
          }
        })
      },
      complete: res => {
        console.log(res)
      }
    })
    var phone = options.phone
    if (phone != undefined) {
      this.setData({
        getUserInfo: true,
        getPhone: false,
        mobile: phone
      })
    }
  },
  //如果进入页面时，已经登陆，就回退
  onShow: function () {
    if (app.globalData.regFlag && app.getCache("token") != "") {
      wx.navigateBack({})
    }
  },
  //微信用户授权后,获取公开用户信息
  getInfo: function (e) {
    this.login(e.detail.userInfo, this.data.mobile)
  },
  login: function (userInfo, mobile) {
    if (userInfo) {
      wx.showLoading({
        title: '登陆中',
      })
      setTimeout(function () {
        wx.hideLoading()
      }, 1500)
      userInfo['mobile'] = mobile
    }
    app.login(userInfo);
  },
  //微信用户授权后,获取加密的手机号
  getPhoneNumber(e) {
    console.log(e)
    var msg = e.detail.errMsg
    var that = this
    var cached_login_info = app.getCache('loginInfo')
    var openid = cached_login_info.openid
    var session_key = cached_login_info.session_key
    var encryptedData = e.detail.encryptedData
    var iv = e.detail.iv;
    if (msg == 'getPhoneNumber:ok') {
      wx.showToast({
        title: '请稍等',
        icon: 'loading',
        duration: 1000,
        mask: true
      })
      // 已注册用户直接登陆
      // 未注册用户解密手机
      // session_key过期，重新续命
      wx.checkSession({
        // 没过期
        success: (res) => {
          wx.request({
            method: 'POST',
            url: app.buildUrl('/member/exists'),
            header: {
              'content-type': 'application/x-www-form-urlencoded',
            },
            data: {
              openid: openid
            },
            success: res => {
              var resp = res.data
              if (resp.code !== 200) {
                app.alert({
                  'content': resp.msg
                })
                return
              }
              if (resp.exists) {
                // 提示信息和登录数据(用户已存在)
                that.directLogin(function () {
                  wx.showToast({
                    title: '登录中',
                    icon: 'loading',
                    duration: 1000,
                    mask: true
                  })
                  app.checkLogin()
                })
              } else {
                // 用户不存在
                that.deciyption(session_key, encryptedData, iv);
              }
            }
          })
        },
        //过期续命
        fail: (res) => {
          wx.login({
            success: res => {
              wx.request({
                method: 'POST',
                url: app.buildUrl('/member/check-reg'),
                header: {
                  'content-type': 'application/x-www-form-urlencoded',
                },
                data: { code: res.code },
                success: function (res) {
                  var resp = res.data

                  //未注册过，正常授权手机号登陆
                  if (resp.code == -2) {
                    var loginInfo = resp.data;
                    app.setCache("loginInfo", loginInfo)
                    that.deciyption(loginInfo.session_key, encryptedData, iv);
                    return
                  }
                  // 提示信息和登录数据(用户已存在)
                  if (resp.code == 200) {
                    var loginInfo = resp.data.login_info
                    app.setCache("loginInfo", loginInfo)
                    that.directLogin(function () {
                      app.onCheckLoginSuccess(res)
                      app.onCheckLoginSuccessShowToast('登陆成功')
                    })
                    return
                  }

                  //获取解密信息出错
                  app.alert({
                    'content': resp.msg
                  })
                }
              })
            }
          })
        }
      })
    }
  },
  directLogin: function (cb_confirm) {
    //已注册过,直接设置全局数据，登陆成功
    app.alert({
      'title': '温馨提示',
      'content': '注册用户, 直接登陆',
      'cb_confirm': function () {
        app.alert({
          'title': '修改手机号',
          'content': '请前往【我的】->【个人信息】',
          'cb_confirm': cb_confirm
        })
      }
    })
  },
  //解码手机号
  deciyption(session_key, encryptedData, iv) {
    var that = this
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
        var mobile = resp.data.mobile
        wx.getSetting({
          success: res => {
            // 已经授权，可以直接调用 getUserInfo 获取头像昵称，不会弹框
            if (res.authSetting['scope.userInfo']) {
              wx.getUserInfo({
                success: res => {
                  // 获取用户信息成功
                  if (res.errMsg == "getUserInfo:ok") {
                    that.login(res.userInfo, mobile)
                  } else {
                    wx.navigateTo({
                      url: '/pages/login/index?phone=' + mobile
                    })
                  }
                }
              })
              return
            }

            //未获得用户授权信息，进入按钮弹窗授权
            wx.navigateTo({
              url: '/pages/login/index?phone=' + mobile
            })
          }
        })
      }
    })
  },
})