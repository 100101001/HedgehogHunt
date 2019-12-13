// pages/jmall/my/controls/index.js
var app=getApp();
Page({
  data: {
    items: [
      {
        label: "物品举报",
        icons: "/images/icons/next.png",
        act: "toCheckReport",
      },
      {
        label: "答谢举报",
        icons: "/images/icons/next.png",
        act: "toCheckThanksReport",
      },
      {
        label: "反馈信息",
        icons: "/images/icons/next.png",
        act: "toCheckFeedback",
      },
        {
        label: "黑名单",
        icons: "/images/icons/next.png",
        act: "toCheckBlockMember",
      },
      {
        label: "统计数据",
        icons: "/images/icons/next.png",
        act: "toCheckStat",
      }
    ]

  },
  onLoad: function (options) {
        var is_adm = app.globalData.is_adm;
        this.setData({
            is_adm: is_adm
        })
  },
  onShareAppMessage: function () {

  },
  toReleaseAdv: function () {
    wx.navigateTo({
      url: '../../adv/release/adv-release',
    })
  },
  toAddAdm:function(){
    wx.navigateTo({
      url: 'add_adm/index',
    })
  },
  toCheckReport:function(){
    var check_report = app.globalData.check_report;
    if(!check_report){
      app.globalData.check_report=!check_report;
    }
    console.log(!check_report);
    wx.navigateTo({
      url: '/pages/Record/index?op_status=4',
    })
  },
  toCheckThanksReport: function () {
    var check_report = app.globalData.check_report;
    if (!check_report) {
      app.globalData.check_report = !check_report;
    }
    console.log(!check_report);
    wx.navigateTo({
      url: '/pages/Thanks/record?op_status=4',
    })
  },
  toCheckStat:function(){
    wx.navigateTo({
      url: 'static/index',
    })
  },
  toCheckFeedback:function(){
    wx.navigateTo({
      url: 'feedback_msg/index',
    })
  },
    toCheckBlockMember:function(){
    wx.navigateTo({
      url: 'blockmember/blockmember',
    })
  }
});