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
    phoneNum: ''
  },
  onLoad: function (options) {
    setTimeout(() => {
      wx.navigateBack()
    }, 1000)
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
    //后端检查码，对就注册跳转新页面，错就提示失败
    this.checkSmsCode(e.detail.value)
  },
  listenPhoneInput: function (e) {
    this.setData({
      phoneNum: e.detail.value
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
    let phone = util.regexConfig().phone
    let inputUserName = param.trim()
    if (phone.test(inputUserName)) {
      return true
    } else {
      app.alert({content: '请输入正确的手机号码'})
      return false
    }
  },
  getSmsCode: function () {
    let phoneNum = this.data.phoneNum
    if (this.verifyInput(phoneNum)) {
      //前端禁用验证码按钮
      //后端发送短信
      this.doGetSmsCode(phoneNum)
    }
  },
  doDownCounting: function (count = 60) {
    let si = setInterval(() => {
      if (count > 0) {
        count--
        this.setData({
          getSmsCodeBtnTxt: count + ' s',
          getSmsCodeBtnColor: "#999",
          getSmsCodeBtnDisabled: true
        })
      } else {
        this.setData({
          getSmsCodeBtnTxt: "获取验证码",
          getSmsCodeBtnColor: "#ff9900",
          getSmsCodeBtnDisabled: false
        })
        clearInterval(si)
      }
    }, 1000)
  },
  doGetSmsCode: function (phone) {
    wx.request({
      method: 'post',
      url: app.buildUrl('/qrcode/sms'),
      header: app.getRequestHeader(1),
      data: {
        "phone": phone
      },
      success: (res) => {
        app.alert({
          content: res.data['msg']
        })
        if (res.data['code'] == 200) {
          this.doDownCounting(60)
        }
      },
      fail: (res) => {
        app.serverBusy()
      }
    })
  },
  checkSmsCode: function (param) {
    if (this.verifyInput(param.phone)) {
      //前端禁用按钮
      this.loading()
      // 请求后端校验码，后端校验成功就绑定成功，否则就提示短信码失败
      wx.request({
        method: 'post',
        header: app.getRequestHeader(1),
        url: app.buildUrl("/qrcode/check/sms"),
        data: {
          phone: this.data.phoneNum,
          code: param.smsCode.trim()
        },
        success: (res) => {
          let resp = res.data
          if (resp['code'] !== 200) {
            app.alert({content: resp['msg']})
            return
          }
          wx.showToast({
            title: '绑定成功',
            icon: 'success',
            duration: 800,
            success: (res) => {
              setTimeout(() => {
                wx.navigateBack()
              }, 700)
            }
          })
        },
        fail: (res) => {
          app.serverBusy()
        },
        complete: (res) => {
          this.cancelLoading()
        }
      })
    }
  }
})