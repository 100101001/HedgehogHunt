//从写的假数据里面加载的数据
var Data = require("../../data/posts-data.js");
var util = require("../../utils/util.js");
Page({
  data: {

  },
  onLoad: function() {
    var userinfo = Data.userinfo;
    var [isSelecteds, urls] = util.onNavigateTap(4);
    this.setData({
      isSelecteds: isSelecteds,
      userinfo: userinfo,
    })
  },

  //改导航栏名称
  onReady: function() {
    wx.setNavigationBarTitle({
      title: "个人信息"
    })
  },

  onChooseAddresTap: function(event) {
    var id = event.currentTarget.dataset.id;
    wx.chooseAddress({
      success(res) {
        console.log(res.userName)
        console.log(res.postalCode)
        console.log(res.provinceName)
        console.log(res.cityName)
        console.log(res.countyName)
        console.log(res.detailInfo)
        console.log(res.nationalCode)
        console.log(res.telNumber)
      }
    })
  },

  onCatchTap: function(event) {
    {
    var id = event.currentTarget.dataset.id;
      wx.navigateTo({
        url: 'Mine-item-modify/Mine-item-modify?id=' + id,
      })
    }
  },
  //点击导航
  onNavigateTap: function(event) {
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