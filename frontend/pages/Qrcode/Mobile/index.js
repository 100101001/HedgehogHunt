// pages/Qrcode/Register/index.js
var util = require("../../../utils/util.js")
const app = getApp()

Page({
  data: {
    registBtnTxt: "绑定",
    registBtnBgColor: "#ff9900",
    registBtnDisabled: false,
    registBtnLoading: false,
    getSmsCodeBtnTxt: "获取验证码",
    getSmsCodeBtnColor: "#ff9900",
    getSmsCodeBtnDisabled: false,
    phoneNum: '',
    qrcode_openid: ''
  },
  onLoad: function (options) {
    this.setData({
      qrcode_openid: options.openid,
    })
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
    var param = e.detail.value
    //后端检查码，对就注册跳转新页面，错就提示失败
    this.checkSmsCode(param)
  },
  listenPhoneInput: function (e) {
    var value = e.detail.value
    this.setData({
      phoneNum: value
    })
  },
  loading: function () {
    this.setData({
      registBtnTxt: "绑定中",
      registBtnDisabled: true,
      registBtnBgColor: "#999",
      registBtnLoading: true,
      getSmsCodeBtnDisabled: true
    })
  },
  cancelLoading: function () {
    this.setData({
      registBtnTxt: "绑定",
      registBtnDisabled: false,
      registBtnBgColor: "#ff9900",
      registBtnLoading: false,
      getSmsCodeBtnDisabled: false
    })
  },
  verifyInput: function (param) {
    var phone = util.regexConfig().phone
    var inputUserName = param.trim()
    if (phone.test(inputUserName)) {
      return true
    } else {
      wx.showModal({
        title: '提示',
        showCancel: false,
        content: '请输入正确的手机号码'
      })
      return false
    }
  },
  getSmsCode: function () {
    var phoneNum = this.data.phoneNum
    var that = this
    var count = 60
    if (this.verifyInput(phoneNum)) {
      //前端禁用验证码按钮
      var si = setInterval(function () {
        if (count > 0) {
          count--
          that.setData({
            getSmsCodeBtnTxt: count + ' s',
            getSmsCodeBtnColor: "#999",
            getSmsCodeBtnDisabled: true
          })
        } else {
          that.setData({
            getSmsCodeBtnTxt: "获取验证码",
            getSmsCodeBtnColor: "#ff9900",
            getSmsCodeBtnDisabled: false
          })
          count = 60
          clearInterval(si)
        }
      }, 1000)
      //后端发送短信
      wx.request({
        method: 'post',
        url: app.buildUrl('/qrcode/sms'),
        header: app.getRequestHeader(1),
        data: {
          "phone": phoneNum
        },
        success: function (res) {
          var resp = res.data
          if (resp.code === 200) {
            app.alert({
              content: "验证码发送成功，请留意短信"
            })
          } else if (resp.code === 400) {
            app.alert({
              content: "操作过于频繁，请稍后再试"
            })
          } else if (resp.code === 500) {
            app.alert({
              content: "验证码发送失败"
            })
          }
        },
        fail: function (res) {
          that.alert({
            content: "验证码发送失败"
          })
        }
      })
    }
  },
  checkSmsCode: function (param) {
    var qrcode_openid = this.data.qrcode_openid
    if (this.verifyInput(param.phone)) {
      //前端禁用按钮
      this.loading()
      var smsCode = param.smsCode.trim()
      var that = this
      // 请求后端校验码，后端校验成功就绑定成功，否则就提示短信码失败
      wx.request({
        method: 'post',
        header: app.getRequestHeader(1),
        url: app.buildUrl("/qrcode/check/sms"),
        data: {
          phone: that.data.phoneNum,
          code: smsCode,
          openid: qrcode_openid
        },
        success: function (res) {
          console.log(res)
          var resp = res.data
          //前端提示
          if (resp.code == 200) {
            wx.showToast({
              title: '绑定成功',
              icon: 'success',
              duration: 1200
            })
            app.globalData.memberInfo.mobile = that.data.phoneNum
            that.cancelLoading()
            that.redirectTo("/pages/Find/Find?business_type=1")
            return
          } else if (resp.code == 401) {
            wx.showModal({
              title: '提示',
              showCancel: false,
              content: '请输入正确的短信验证码'
            })
          } else if (resp.code == 400) {
            wx.showModal({
              title: '提示',
              showCancel: false,
              content: '短信验证码已过期，请重新获取验证码'
            })
          }
          that.cancelLoading()
        },
        fail: function (res) {
          app.serverBusy()
          that.cancelLoading()
        }
      })
    }
  },
  redirectTo: function (url) {
    //需要将param转换为字符串
    wx.reLaunch({
      url: url//参数只能是字符串形式，不能为json对象
    })
  }

})