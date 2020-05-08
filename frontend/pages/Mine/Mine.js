const navigate = require("../template/navigate-bar/navigate-bar-template.js")
const util = require("../../utils/util.js");
const app = getApp();
Page({
  data: {

  },
  onLoad: function () {
    this.setData({
      is_user: app.globalData.is_user  //管理员可见管理后台
    });
    this.setLoadData(); //所有入口entry的初始化
  },
  setLoadData: function () {
    //基本信息栏
    let items1 = [
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
    //记录栏
    let items2 = [
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
  onShow: function () {
    util.getNewRecommend((data) => {
      //新的推荐通知
      let items2 = this.data.items2;
      //设置新消息计数
      items2[2].value = data.return_new;
      items2[3].value = data.recommend_new;
      items2[4].value = data.thanks_new;
      this.setData({
        items2: items2
      });
    });
  },
  goControls: function () {
    wx.navigateTo({
      url: '/controls/pages/index',
      complete(res){
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
      url: 'feedback/index',
    })
  },
  goRecord: function (event) {
    wx.navigateTo({
      url: '../Record/index?op_status=' +  event.currentTarget.dataset.op_status
    })
  },
  goThanksList: function (event) {
    wx.navigateTo({
      url: '../Thanks/record/index?op_status=' + event.currentTarget.dataset.op_status,
    })
  }
})