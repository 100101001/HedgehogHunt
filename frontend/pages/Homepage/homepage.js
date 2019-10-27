var util = require("../../utils/util.js");
Page({
  onLoad:function(){
    var textArray={
      text1:"信息为网友发布",
      text2:"私下联系请自行判断真伪"
    };
    var goodsInfo=[
      {
        goods:"卡贴卡套",
        img:"/images/icons/卡.png",
        num:3,
        price:"￥2",
        id:0
      },
      {
        goods: "钥匙扣",
        img: "/images/icons/钥匙.png",
        num: 1,
        price: "￥4",
        id: 1
      },
      {
        goods: "贴纸",
        img: "/images/icons/贴纸.png",
        num: 5,
        price: "￥1",
        id: 2
      },
      {
        goods: "小印章",
        img: "/images/icons/印章.png",
        num: 1,
        price: "￥5",
        id: 3
      }
    ]
    //设置底部导航栏
    var [isSelecteds, urls] = util.onNavigateTap(0);
    this.setData({
      isSelecteds: isSelecteds,
      goodsInfo: goodsInfo,
      textArray:textArray,
    })
  },

  //点击意见反馈之后跳转
  onAboutUsTap:function(event){
    wx.navigateTo({
      url: "../homepage/homepage/aboutus/aboutus",
    })
  },
  //点击意见反馈之后跳转
  onAdviceTap: function (event) {
    wx.navigateTo({
      url: "../homepage/homepage/advice/advice",
    })
  },

   //点击立即领取之后跳转至付费界面
    onPayTap: function (event) {
    wx.navigateTo({
      url: "../homepage/homepage/pay/pay",
    })
  },
  //点击商品栏
  onDetailTap:function(event){
    var id = event.currentTarget.dataset.id;
    wx.navigateTo({
      url: 'homepage/commodity/commodity?id='+id,
    })
  },
  //点击导航
  onNavigateTap: function (event) {
    var id = event.currentTarget.dataset.id * 1; //乘1强制转换成数字
    var [isSelecteds, urls]= util.onNavigateTap(id);
    this.setData({
      isSelecteds: isSelecteds
    })
    wx.redirectTo({
      url: urls[id],
    })
  }
})