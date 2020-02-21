const navigate = require("../template/navigate-bar/navigate-bar-template.js")
var util = require("../../utils/util.js");
var app=getApp();
Page({
  onLoad:function(){
    var textArray={
      text1:"信息为网友发布",
      text2:"私下联系请自行判断真伪"
    };
    var unis = [{
      "id": "同济大学",
      "url": "/images/unis/TJU.jpeg",
      "option": "1"
      },
      {
        "id": "北京大学",
        "url": "/images/unis/PKU.jpeg",
        "option": "2"
      },
      {
        "id": "北京师范",
        "url": "/images/unis/BNU.jpeg",
        "option": "3"
      },
      {
        "id": "东南大学",
        "url": "/images/unis/SEU.jpg",
        "option": "4"
      },
      {
        "id": "西安交大",
        "url": "/images/unis/XJTU.jpeg",
        "option": "5"
      },
      {
        "id": "四川大学",
        "url": "/images/unis/SCU.jpeg",
        "option": "6"
      }
    ]
    //设置底部导航栏
    var [isSelecteds, urls] = util.onNavigateTap(0);
    var total_new = app.globalData.total_new;
    isSelecteds['total_new'] = total_new;
    this.setData({
      isSelecteds: isSelecteds,
      textArray:textArray,
      unis:unis,
    })
  },

  //点击意见反馈之后跳转
  onAboutUsTap:function(event){
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
  onDetailTap:function(event){
    var id = event.currentTarget.dataset.id;
    wx.navigateTo({
      url: 'homepage/commodity/commodity?id='+id,
    })
  },
  //点击导航
  onNavigateTap: function (event) {
    navigate.onNavigateTap(event, this)
  },
  goBuy: function (e) {
    console.log(e)
    var id = e.currentTarget.dataset.id
    var campus = this.data.unis[id].option
    var name = this.data.unis[id].id
    console.log(campus)
    wx.navigateTo({
      url: 'product/index?campus=' + campus+'&campus_name='+ encodeURIComponent(name),
    })
  }
})