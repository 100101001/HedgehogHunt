var util = require("../../utils/util.js");
var app=getApp();
const HedgeHogClient = require('../../utils/api').HedgeHogClient
Page({
  data: {
    
  },
  onLoad: function () {
    var that = this
    var is_user = app.globalData.is_user;
    this.setData({
      is_user: is_user
    })
    var [isSelecteds, urls] = util.onNavigateTap(4);
    var total_new = app.globalData.total_new;
    var recommend_new = app.globalData.recommend_new;
    var thanks_new = app.globalData.thanks_new;
    isSelecteds['total_new'] = total_new;
    this.setData({
      isSelecteds: isSelecteds,
      recommend_new: recommend_new,
      thanks_new: thanks_new
    })
    this.setLoadData();
  },
  setLoadData:function(){
   var  items1=[
      {
        label: "个人信息",
        icons: "/images/icons/next.png",
        act: "goUserInfo",
      },
      {
        label: "反馈建议",
        icons: "/images/icons/next.png",
        act: "goFeedback",
      },
      {
        label: "联系我们",
        icons: "/images/icons/next.png",
        act: "goConnect",
      },
    ];
    var  items2=[
        {
          label: "发布记录",
          icons: "/images/icons/next.png",
          act: "goRecord",
          op_status: "0"
        },
        {
          label: "认领记录",
          icons: "/images/icons/next.png",
          act: "goRecord",
          op_status: "1"
        },
        {
          label: "匹配推送",
          icons: "/images/icons/next.png",
          value: this.data.recommend_new,//value值是新推送的，未查看过的记录数，按时间来划分
          act: "goRecord",
          op_status: "2"
        },
        {
          label: "物主答谢",
          icons: "/images/icons/next.png",
          value: this.data.thanks_new,//value值是新推送的，未查看过的用户答谢数，按时间来划分
          act: "goThanksList",
          op_status: "3"
        }
      ];
      this.setData({
        items1:items1,
        items2:items2,
      })
  },
  goControls: function () {
    wx.navigateTo({
      url: 'controls/index',
    })
  },
  goUserInfo: function () {
    wx.navigateTo({
      url: 'userinfo/index',
    })
  },
  goConnect: function () {
    wx.navigateTo({
      url: 'connect/index',
    })
  },
  goFeedback: function () {
    wx.navigateTo({
      url: 'controls/feedback/index',
    })
  },
  goRecord: function (event) {
    var op_status = event.currentTarget.dataset.op_status* 1;
    wx.navigateTo({
      url: '../Record/index?op_status=' + op_status,
    })
  },
  goThanksList: function () {
    app.globalData.op_status=2;
    wx.navigateTo({
      url: '../Thanks/record/index',
    })
  },
  //点击导航
  onNavigateTap: function (event) {
    app.getNewRecommend();
    var id = event.currentTarget.dataset.id * 1; //乘1强制转换成数字
    var [isSelecteds, urls] = util.onNavigateTap(id);
    this.setData({
      isSelecteds: isSelecteds,
    })
    wx.redirectTo({
      url: urls[id],
    })
  }
})