var util = require("../../utils/util.js");
var app=getApp();
Page({
  onLoad:function(){
    var textArray={
      text1:"信息为网友发布",
      text2:"私下联系请自行判断真伪"
    };
    var unis=[
      "/images/unis/TJU.jpeg",
      "/images/unis/PKU.jpeg",
      "/images/unis/SJTU.jpeg",
      "/images/unis/BNU.jpeg",
      "/images/unis/SEU.jpg",
      "/images/unis/XJTU.jpeg",
      "/images/unis/SCU.jpeg",
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
    app.getNewRecommend();
    var id = event.currentTarget.dataset.id * 1; //乘1强制转换成数字
    var [isSelecteds, urls]= util.onNavigateTap(id);
    this.setData({
      isSelecteds: isSelecteds
    })
    wx.redirectTo({
      url: urls[id],
    })
  }
})