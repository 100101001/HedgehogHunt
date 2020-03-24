const navigate = require("../template/navigate-bar/navigate-bar-template.js")
var util = require("../../utils/util.js");
var app = getApp();
Page({
  data:{
    schoolInput: "",
    unis: [],
    p: 1,
    searching: false
  },
  onLoad: function () {
    var textArray = {
      text1: "好看又实用校园闪寻周边可附着在物品上",
      text2: "在物品遗失后可帮助物主快速寻回物品",
      text3: "快来点击获取你学校专属的闪寻周边吧！",
    };
    this.setData({
      textArray: textArray
    })
  },
  onShow: function(){
    //设置底部导航栏
    var [isSelecteds, urls] = util.onNavigateTap(0);
    isSelecteds['total_new'] = app.globalData.total_new;
    isSelecteds['showHintQrcode'] = app.globalData.showHintQrcode
    isSelecteds['regFlag'] = app.globalData.regFlag
    isSelecteds['hasQrcode'] = app.globalData.has_qrcode
    this.setData({
      isSelecteds: isSelecteds
    })
    this.getUniversityList()
    
  },
  getUniversityList: function(){
    var that = this
    this.setData({
      searching: true
    })
    wx.request({
      url: app.buildUrl('/campus/search'),
      data: {
        p: that.data.p,
        school : that.data.schoolInput
      },
      success: function(res){
        var resp = res.data
        if(resp.code!=200){
          app.alert({
            'content':resp.msg
          })
          return
        }
        that.setData({
          loadingMore: resp.data.has_more,
          unis: that.data.unis.concat(resp.data.unis),
          p: that.data.p + 1
        })
      },
      complete: function(res){
        that.setData({
          searching: false
        })
      }
    })
  },
  onReachBottom: function(e){
    if(this.data.loadingMore){
      this.getUniversityList()
    }
  },
  listenerSchoolInput: function(e){
    this.setData({
      schoolInput: e.detail.value
    })
  },
  searchSchool: function(e){
    this.setData({
      unis: [],
      p: 1
    })
    this.getUniversityList(true)
  },
  //点击意见反馈之后跳转
  onAboutUsTap: function (event) {
    wx.navigateTo({
      url: "../homepage/homepage/aboutus/aboutus",
    })
  },
  //点击意见反馈之后跳转
  onAdviceTap: function (event) {
    wx.navigateTo({
      url: "../homepage/homepage/advice/advice",
    })
  },

  //点击立即领取之后跳转至付费界面
  onPayTap: function (event) {
    wx.navigateTo({
      url: "../homepage/homepage/pay/pay",
    })
  },
  //点击商品栏
  onDetailTap: function (event) {
    var id = event.currentTarget.dataset.id;
    wx.navigateTo({
      url: 'homepage/commodity/commodity?id=' + id,
    })
  },
  //点击导航
  onNavigateTap: function (event) {
    navigate.onNavigateTap(event, this)
  },
  goBuy: function (e) {
    var id = e.currentTarget.dataset.id
    var campus = this.data.unis[id].option
    var name = this.data.unis[id].id
    app.globalData.campus_id = campus
    app.globalData.campus_name = name
    wx.navigateTo({
      url: '/mall/pages/index?campus_id=' + campus + '&campus_name=' + encodeURIComponent(name),
    })
  },
  closeQrcodeHint: function(e){
    navigate.closeQrcodeHint(this)
  }
})