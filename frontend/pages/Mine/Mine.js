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
    var [isSelecteds, urls] = util.onNavigateTap(4);
    isSelecteds['total_new'] = app.globalData.total_new;
    isSelecteds['showHintQrcode'] = app.globalData.showHintQrcode
    isSelecteds['regFlag'] = app.globalData.regFlag
    isSelecteds['hasQrcode'] = app.globalData.has_qrcode
    this.setData({
      isSelecteds: isSelecteds,
      recommend_new: app.globalData.recommend_new,
      thanks_new: app.globalData.thanks_new
    })
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
    var op_status = event.currentTarget.dataset.op_status * 1;
    wx.navigateTo({
      url: '../Record/index?op_status=' + op_status,
    })
  },
  goThanksList: function (event) {
    //app.globalData.op_status = 2;
    var op_status = event.currentTarget.dataset.op_status * 1;
    wx.navigateTo({
      url: '../Thanks/record/index?op_status=' + op_status,
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