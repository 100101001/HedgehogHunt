// pages/Mine/Mine-item-modify/Mine-item-modify.js
//从写的假数据里面加载的数据
// var Data = require("../../../data/posts-data.js");
Page({
  data: {
    newValue: "empty"
  },

  //点击页面之后从前端加载所有的用户数据
  onLoad: function (options) {
    //授权设置
    var set_title = [{
      title: "位置信息",
    },
    {
      title: "用户信息"
    },
    {
      title: "保存图片"
    }
    ]
    const pages = getCurrentPages();
    var prevPage = pages[pages.length - 2]
    var userinfo = prevPage.data.userinfo;

    var statusArray = [false, false, false, false, false, false];
    var id = options.id;
    statusArray[id] = true;
    this.setData({
      status0: statusArray[0],
      status1: statusArray[1],
      status2: statusArray[2],
      status3: statusArray[3],
      status4: statusArray[4],
      status5: statusArray[5],
      //以传过来的值做为输入框中原本的值
      userinfo: userinfo,
      set_title: set_title
    })
  },
  //获取修改的值
  onBindInput: function (event) {
    this.setData({
      newValue: event.detail.value
    })
  },
  //获取修改的信息
  onBindConfirm: function (event) {
    wx.showModal({
      title: '获取信息：' + this.data.newValue,
      content: "接下来的逻辑我就不知道了。。"
    })
  },
  //点击保存按钮之后的事件
  onSubmit: function (event) {
    wx.showModal({
      title: '获取信息：' + this.data.newValue,
      content: "还没搞懂怎么获取input里面的值。。"
    })
  },

  //switch开关操作
  switch1Change: function (event) {
    wx.showModal({
      title: '捕获修改事件',
      content: '获取的值为' + event.detail.value + "依然不会接下来逻辑。。",
    })
  },

  onSaveImgTap: function (event) {
    wx.showModal({
      title: '页面加载时',
      content: "应该从服务器加载用户的二维码",
    })
    //调用保存图片的api
    wx.saveImageToPhotosAlbum({
      success(res) { },
      complete(rex) {
        wx.showModal({
          title: '保存图片',
          content: "需指定保存路径",
        })
      }
    })
  },
  //清除缓存
  onClearStorage: function (event) {
    wx.clearStorageSync();
    wx.showToast({
      title: '缓存清除完成',
    })
  },
  //微信支付接口
  onPayTap: function (event) {
    wx.showModal({
      title: '微信支付',
      content: "调用微信支付的API,有待真机检验",
    })
    wx.requestPayment({
      timeStamp: '',
      nonceStr: '',
      package: '',
      signType: 'MD5',
      paySign: '',
      success(res) { },
      fail(res) { }
    })
  },

  //用户提现
  onRePayTap: function (event) {
    wx.showModal({
      title: '账户提现',
      content: "调用微信支付的API,有待真机检验",
    })
  }
})