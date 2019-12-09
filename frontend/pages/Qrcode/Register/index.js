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
    if(this.checkUserName(phoneNum)){
      wx.request({
        method:'post',
        url:app.buildUrl('/qrcode/sms'),
        data: {
          "phone": phoneNum
        },
        success: function(res){
           that.alert({
             content:"验证码发送成功"
           })
        },
        fail:function(res) {
          that.alert({
            content:"验证码发送失败"
          })
        }
      })
      var si = setInterval(function(){
      if(count > 0){
        count--;
        that.setData({
          getSmsCodeBtnTxt:count+' s',
          getSmsCodeBtnColor:"#999",
          smsCodeDisabled: true
        });
      }else{
        that.setData({
          getSmsCodeBtnTxt:"获取验证码",
          getSmsCodeBtnColor:"#ff9900",
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
          if (res.statusCode === 200) {
            setTimeout(function () {
              wx.showToast({
                title: '注册成功',
                icon: 'success',
                duration: 1500
              });
              that.setregistData2();
              that.redirectTo(param);
            }, 2000);
            that.setregistData2();
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