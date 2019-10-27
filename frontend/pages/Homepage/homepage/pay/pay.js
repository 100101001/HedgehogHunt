Page({
  onPayTap: function (event) {
    wx.showModal({
      title: '微信支付',
      content: "没啥反应的微信支付",
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

  onLoad: function () {
    //商品信息
    var goodsinfo = [
      {
        goods: "卡贴卡套",
        num: "X3",
        price: "￥2"
      },
      {
        goods: "钥匙扣",
        num: "X1",
        price: "￥4"
      },
      {
        goods: "贴纸",
        num: "X5",
        price: "￥1"
      },
      {
        goods: "小印章",
        num: "X1",
        price: "￥5"
      }
    ]
    //用户信息
    var userMes=[
      {
        title:"姓名",
        content:"韦朝旭",
      },
      {
        title: "电话",
        content: "18385537403",
      },
      {
        title: "地址",
        content: "上海市杨浦区四平路1239号同济大学",
      }
    ]
    this.setData({
      goods_key: goodsinfo,
      user_key:userMes,
    })
  },
})