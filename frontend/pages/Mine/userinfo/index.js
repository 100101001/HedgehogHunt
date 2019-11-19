var util = require("../../../utils/util.js");
const HedgeHogClient = require('../../../utils/api').HedgeHogClient
Page({
  data: {
    items:[
      {
        name:"姓名",
        value:"韦朝旭",
      },
      {
        name: "电话",
        value: "18385537403",
      },
      {
        name: "收件地址",
        value: "上海市杨浦区四平路1239号",
      },
      {
        name: "编辑个人信息",
        value: "",
        act:"onChooseAddresTap",
        src:'/images/icons/write.png',
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

  onCatchTap: function (event) {
    {
      var id = event.currentTarget.dataset.id;
      wx.navigateTo({
        url: 'Mine-item-modify/Mine-item-modify?id=' + id,
      })
    }
  }
})