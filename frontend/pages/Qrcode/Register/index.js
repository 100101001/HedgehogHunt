// pages/Qrcode/Register/index.js
var util = require("../../../utils/util.js");
const app = getApp()

Page({
  data: {
    registBtnTxt: "注册",
    registBtnBgBgColor: "#ff9900",
    getSmsCodeBtnTxt: "获取验证码",
    getSmsCodeBtnColor: "#ff9900",
    // getSmsCodeBtnTime:60,
    btnLoading: false,
    registDisabled: false,
    smsCodeDisabled: false,
    inputUserName: '',
    inputPassword: '',
    phoneNum: ''
  },
  onLoad: function (options) {
    // 页面初始化 options为页面跳转所带来的参数
    // 后续修改/member/login、判断如果是新用户，且带有属性source=qrcode，那么调用QrcodeService类的addQrcode2member，且member表内放入qrcodeId
  },
  onReady: function () {
    // 页面渲染完成

  },
  onShow: function () {
    // 页面显示

  },
  onHide: function () {
    // 页面隐藏

  },
  onUnload: function () {
    // 页面关闭

  },
  formSubmit: function (e) {
    var param = e.detail.value;
    //后端检查码，对就注册跳转新页面，错就提示失败
    this.checkSmsCode(param)
  },
  getPhoneNum: function (e) {
    var value = e.detail.value;
    this.setData({
      phoneNum: value
    });
  },
  setregistData1: function () {
    this.setData({
      registBtnTxt: "注册中",
      registDisabled: !this.data.registDisabled,
      registBtnBgBgColor: "#999",
      btnLoading: !this.data.btnLoading
    });
  },
  setregistData2: function () {
    this.setData({
      registBtnTxt: "注册",
      registDisabled: !this.data.registDisabled,
      registBtnBgBgColor: "#ff9900",
      btnLoading: !this.data.btnLoading
    });
  },
  checkPhone: function (param) {
    var phone = util.regexConfig().phone;
    var inputUserName = param.trim();
    if (phone.test(inputUserName)) {
      return true;
    } else {
      wx.showModal({
        title: '提示',
        showCancel: false,
        content: '请输入正确的手机号码'
      });
      return false;
    }
  },
  getSmsCode: function () {
    var phoneNum = this.data.phoneNum;
    var that = this;
    var count = 60;
    if (this.checkPhone(phoneNum)) {
      wx.request({
        method: 'post',
        url: app.buildUrl('/qrcode/sms'),
        data: {
          "phone": phoneNum
        },
        success: function (res) {
          if (res.statusCode === 200) {
            app.alert({
              content: "验证码发送成功，请留意短信"
            })
          } else if (res.statusCode === 400) {
            app.alert({
              content: "操作过于频繁，请稍后再试"
            })
          } else if (res.statusCode === 500) {
            app.alert({
              content: "验证码发送失败"
            })
          }
        },
        fail: function (res) {
          app.alert({
            content: "验证码发送失败"
          })
        }
      })
      var si = setInterval(function () {
        if (count > 0) {
          count--;
          that.setData({
            getSmsCodeBtnTxt: count + ' s',
            getSmsCodeBtnColor: "#999",
            smsCodeDisabled: true
          });
        } else {
          that.setData({
            getSmsCodeBtnTxt: "获取验证码",
            getSmsCodeBtnColor: "#ff9900",
            smsCodeDisabled: false
          });
          count = 60;
          clearInterval(si);
        }
      }, 1000);
    }

  },
  checkSmsCode: function (param) {
    console.log("进了 checkSms")
    if (this.checkPhone(param.phone)) {
      this.setregistData1();
      var smsCode = param.smsCode.trim();
      var that = this;
      // 请求后端校验码，后端校验成功就注册成功，否则就提示短信码失败
      wx.request({
        method: 'post',
        url: app.buildUrl("/qrcode/check/sms"),
        data: {
          phone: that.data.phoneNum,
          code: smsCode
        },
        success: function (res) {
          console.log("验证码正确")
          console.log(res)
          if (res.statusCode === 200) {
            //调·小程序登录API获取code
            wx.login({
              success: function (res) {
                console.log("小程序login API调用成功")
                console.log(res)
                var userInfo = app.globalData.userInfo == null ? {} : app.globalData.userInfo
                userInfo['code'] = res.code
                console.log("userInfo")
                console.log(userInfo)
                console.log("userInfo")
                //发登录请求（注册）
                wx.request({
                  method: 'post',
                  url: app.buildUrl('/member/login', userInfo),
                  headers: app.getRequestHeader(),
                  success: function (res) {
                    console.log("后端login API调用成功")
                    console.log(res)
                    //校验码确保成功后调用小程序wx.login获取code，给后端获取openid并进行注册
                    if (res.data.code === 200) {
                      setTimeout(function () {
                        wx.showToast({
                          title: '注册成功',
                          icon: 'success',
                          duration: 1500
                        });
                        app.setCache("token", res.data.data.token);
                        that.setregistData2();
                        that.redirectTo(param);
                      }, 2000);
                    } else {
                      app.serverInternalError()
                    }
                  },
                  fail: function (res) {
                    app.serverBusy()
                  }
                })
              }
            })
          } else if (res.statusCode === 401) {
            wx.showModal({
              title: '提示',
              showCancel: false,
              content: '请输入正确的短信验证码'
            });
            that.setregistData2();
          } else if (res.statusCode === 400) {
            wx.showModal({
              title: '提示',
              showCancel: false,
              content: '短信验证码已过期，请重新获取验证码'
            });
            that.setregistData2();
          }
        },
        fail: function (res) {
          app.serverBusy()
          that.setregistData2();
        }
      })
    }
  },
  redirectTo: function (param) {
    //需要将param转换为字符串
    // param = JSON.stringify(param);
    // wx.redirectTo({
    //   url: '../main/index?param=' + param//参数只能是字符串形式，不能为json对象
    // })
  }

})