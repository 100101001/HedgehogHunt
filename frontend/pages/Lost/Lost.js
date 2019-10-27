var util = require("../../utils/util.js");
Page({
  data:{

  },
  onLoad:function(event){
    //设置底部导航栏
    var [isSelecteds, urls] = util.onNavigateTap(3);
    this.setData({
      isSelecteds: isSelecteds,
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