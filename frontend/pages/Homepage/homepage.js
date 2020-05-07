const navigate = require("../template/navigate-bar/navigate-bar-template.js")
const util = require("../../utils/util.js")
const app = getApp()
Page({
  data:{
    schoolInput: "",
    unis: [],
    p: 1,
    searching: false
  },
  onLoad: function () {
    let textArray = {
      text1: "好看又实用校园闪寻周边可附着在物品上",
      text2: "在物品遗失后可帮助物主快速寻回物品",
      text3: "快来点击获取你学校专属的闪寻周边吧！",
    }
    this.setData({
      textArray: textArray
    })
  },
  onBindBlur: function(){

  },
  onShow: function(){
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
        p: this.data.p,
        school : this.data.schoolInput
      },
      success: (res) => {
        let resp = res.data;
        if(resp['code']!==200){
          app.alert({
            content:resp['msg']
          })
          return
        }
        this.setData({
          loadingMore: resp.data.has_more,
          unis: this.data.unis.concat(resp.data.unis),
          p: this.data.p + 1
        })
      },
      fail: (res) => {
        app.serverBusy()
      },
      complete: (res) => {
        this.setData({
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