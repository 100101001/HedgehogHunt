// pages/jmall/my/controls/index.js
var app=getApp();
Page({
  data: {
    items: [
      {
        label: "举报信息",
        icons: "/images/icons/next.png",
        act: "toCheckReport",
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
    wx.switchTab({
      url: '/pages/jmall/record/index',
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