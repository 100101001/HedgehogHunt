var util = require("../../utils/util.js");
const HedgeHogClient = require('../../utils/api').HedgeHogClient
Page({
  data: {
    items1: [
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
    ],
    items2:[
      {
        label: "发布记录",
        icons: "/images/icons/next.png",
        act: "goRecord",
        record_status:"1"
      },
      {
        label: "认领记录",
        icons: "/images/icons/next.png",
        act: "goRecord",
        record_status: "2"
      },
      {
        label: "匹配推送",
        icons: "/images/icons/next.png",
        value: 99,//value值是新推送的，未查看过的记录数，按时间来划分
        act: "goRecord",
        record_status: "3"
      },
      {
        label: "物主答谢",
        icons: "/images/icons/next.png",
        value: 99,//value值是新推送的，未查看过的用户答谢数，按时间来划分
        act: "goThanksList",
        record_status: "3"
      }

    ]
  },
  onLoad: function () {
    var that = this
    // wx.request(HedgeHogClient.GetUserInfoRequest(1, function (res) {
    //   that.setData({
    //     userinfo: res.data
    //   })
    // }))
    var [isSelecteds, urls] = util.onNavigateTap(4);
    this.setData({
      isSelecteds: isSelecteds
    })
  },
  onChooseAddresTap: function (event) {
    var that = this;
    var items=that.data.items;
    wx.chooseAddress({
      success(res) {
        console.log(res)
        items[0].value = res.userName;
        items[1].value = res.telNumber;
        items[2].value = res.cityName + res.countyName + res.detailInfo;
        that.setData({
          items:items
        })
        // console.log(res.userName)
        // console.log(res.postalCode)
        // console.log(res.provinceName)
        // console.log(res.cityName)
        // console.log(res.countyName)
        // console.log(res.detailInfo)
        // console.log(res.nationalCode)
        // console.log(res.telNumber)
      }
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
  goRecord: function () {
    wx.navigateTo({
      url: '../Record/index',
    })
  },
  goThanksList: function () {
    wx.navigateTo({
      url: '../Thanks/record/record',
    })
  },
  //点击导航
  onNavigateTap: function (event) {
    var id = event.currentTarget.dataset.id * 1; //乘1强制转换成数字
    var [isSelecteds, urls] = util.onNavigateTap(id);
    this.setData({
      isSelecteds: isSelecteds
    })
    wx.redirectTo({
      url: urls[id],
    })
  }
})