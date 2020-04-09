const navigate = require("../template/navigate-bar/navigate-bar-template.js")
var util = require("../../utils/util.js");
var app = getApp();
Page({
  data: {

  },
  onLoad: function () {
    var is_user = app.globalData.is_user;
    this.setData({
      is_user: is_user
    })
  },
  onShow: function () {
    util.getNewRecommend((data) => {
      //新的推荐通知
      this.setData({
        recommend_new: data.recommend_new,
        thanks_new: data.thanks_new,
        return_new: data.return_new
      });
    });
    this.setLoadData();
  },
  setLoadData: function () {
    var items1 = [
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
    var items2 = [
      {
        label: "发布记录",
        icons: "/images/icons/next.png",
        act: "goRecord",
        op_status: 0
      },
      {
        label: "认领记录",
        icons: "/images/icons/next.png",
        act: "goRecord",
        op_status: 1
      },
      {
        label: "归还通知",
        icons: "/images/icons/next.png",
        value: this.data.return_new, //value值是待取回的归还
        act: "goRecord",
        op_status: 5
      },
      {
        label: "匹配推送",
        icons: "/images/icons/next.png",
        value: this.data.recommend_new,//value值是新推送的，未查看过的记录数，按时间来划分
        act: "goRecord",
        op_status: 2
      },
      {
        label: "物主答谢",
        icons: "/images/icons/next.png",
        value: this.data.thanks_new,//value值是新推送的，未查看过的用户答谢数，按时间来划分
        act: "goThanksList",
        op_status: 3
      },
      {
        label: "申诉记录",
        icons: "/images/icons/next.png",
        // value: this.data.appealed, //value值是待取回的归还
        act: "goRecord",
        op_status: 6 //记录
      },
    ];
    this.setData({
      items1: items1,
      items2: items2,
    })
  },
  goControls: function () {
    wx.navigateTo({
      url: '/controls/pages/index',
      complete(res){
        console.log(res)
      }
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
      url: '/controls/pages/feedback/index',
    })
  },
  goRecord: function (event) {
    //var op_status = event.currentTarget.dataset.op_status * 1;
    let op_status = event.currentTarget.dataset.op_status
    console.log(op_status);
    wx.navigateTo({
      url: '../Record/index?op_status=' + op_status
    })
  },
  goThanksList: function (event) {
    //app.globalData.op_status = 2;
    //var op_status = event.currentTarget.dataset.op_status * 1;
    wx.navigateTo({
      url: '../Thanks/record/index?op_status=' + event.currentTarget.dataset.op_status,
    })
  },
  //点击导航
  onNavigateTap: function (event) {
    navigate.onNavigateTap(event, this)
  },
  closeQrcodeHint: function (e) {
    navigate.closeQrcodeHint(this)
  }
})