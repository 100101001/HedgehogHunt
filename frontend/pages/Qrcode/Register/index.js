// pages/Qrcode/Register/index.js
var util = require("../../../utils/util.js");
const app = getApp()

Page({
  data:{
    registBtnTxt:"注册",
    registBtnBgBgColor:"#ff9900",
    getSmsCodeBtnTxt:"获取验证码",
    getSmsCodeBtnColor:"#ff9900",
    // getSmsCodeBtnTime:60,
    btnLoading:false,
    registDisabled:true,
    smsCodeDisabled:false,
    inputUserName: '',
    inputPassword: '',
    phoneNum: ''
  },
  onLoad:function(options){
    // 页面初始化 options为页面跳转所带来的参数
    
  },
  onReady:function(){
    // 页面渲染完成
    
  },
  onShow:function(){
    // 页面显示
    
  },
  onHide:function(){
    // 页面隐藏
    
  },
  onUnload:function(){
    // 页面关闭
    
  },
  formSubmit:function(e){
    var param = e.detail.value;
    this.mysubmit(param);
  },
  mysubmit:function (param){
    var flag = this.checkUserName(param.username)&&this.checkPassword(param)&&this.checkSmsCode(param)
    var that = this;
    if(flag){
        this.setregistData1();
        setTimeout(function(){
          wx.showToast({
            title: '成功',
            icon: 'success',
            duration: 1500
          });
          that.setregistData2();
          that.redirectTo(param);
        },2000);
    } 
  },
  getPhoneNum:function(e){
   var value  = e.detail.value;
   this.setData({
    phoneNum: value     
   });
  },
  setregistData1:function(){
    this.setData({
      registBtnTxt:"注册中",
      registDisabled: !this.data.registDisabled,
      registBtnBgBgColor:"#999",
      btnLoading:!this.data.btnLoading
    });
  },
  setregistData2:function(){
    this.setData({
      registBtnTxt:"注册",
      registDisabled: !this.data.registDisabled,
      registBtnBgBgColor:"#ff9900",
      btnLoading:!this.data.btnLoading
    });
  },
  checkUserName:function(param){ 
    var phone = util.regexConfig().phone;
    var inputUserName = param.trim();
    if(phone.test(inputUserName)){
      return true;
    }else{
      wx.showModal({
        title: '提示',
        showCancel:false,
        content: '请输入正确的手机号码'
      });
      return false;
    }
  },
  checkPassword:function(param){
    var userName = param.username.trim();
    var password = param.password.trim();
    if(password.length<=0){
      wx.showModal({
        title: '提示',
        showCancel:false,
        content: '请设置密码'
      });
      return false;
    }else if(password.length<6||password.length>20){
      wx.showModal({
        title: '提示',
        showCancel:false,
        content: '密码长度为6-20位字符'
      });
      return false;
    }else{
      return true;
    }
  },
  getSmsCode:function(){
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
      },1000);
    }
    
  },
  checkSmsCode:function(param){
    var smsCode = param.smsCode.trim();
    var tempSmsCode = '000000';//演示效果临时变量，正式开发需要通过wx.request获取
    if(smsCode!=tempSmsCode){
      wx.showModal({
        title: '提示',
        showCancel:false,
        content: '请输入正确的短信验证码'
      });
      return false;
    }else{
      return true;
    }
  },
  redirectTo:function(param){
    //需要将param转换为字符串
    param = JSON.stringify(param);
    wx.redirectTo({
      url: '../main/index?param='+ param//参数只能是字符串形式，不能为json对象
    })
  }

})