var util = require("../../utils/util.js");
var app = getApp();
Page({
  data: {
    isHide: false,
    thanks_text: "",
    price: 0
  },
  onLoad: function(options) {
    // var data = JSON.parse(options.data)
    var data = {
      auther_id: 100000,
      auther_name: "Joker",
      avatar: "https://wx.qlogo.cn/mmopen/vi_32/bIp2ka72wPydCEsH6U1oFbVoINfxeJwJ4uGTicGfgSCGC8jGPCnicxAIPlCt2bkUy50cCPEbOPo4cm39r6seyLVw/132",
      business_type: 1,
      goods_id: 8,
      goods_name: "相机",
      updated_time: "2019-12-10 09:34:49",
      owner_name:"韦朝旭"
    };
    this.setData({
      data: data
    })
  },
  goHome: function(e) {
    wx.navigateTo({
      url: "../Find/Find?business_type=1",
    })
  },
  listenerTextInput: function(e) {
    this.setData({
      thanks_text: e.detail.value
    });
  },
  moneyThanks(e) {
    app.alert({
      'content': '调起微信支付'
    });
  },
  subMit: function(e) {
    var thanks_text = this.data.thanks_text;
    var data = this.data.data;
    data['price'] = 0;
    data['thanks_text'] = thanks_text;
    console.log(data);
    var that=this;
    wx.request({
      url: app.buildUrl("/thanks/create"),
      header: app.getRequestHeader(),
      data:data,
      success: function(res) {
        var resp = res.data;
        if (resp.code !== 200) {
          app.alert({
            'content': resp.msg
          });
          return
        }
        wx.hideLoading();
        wx.showToast({
          title: '答谢成功！',
          icon: 'success',
          duration: 2000
        });
        that.goHome();
      },
      fail: function(res) {
        wx.hideLoading();
        wx.showToast({
          title: '系统繁忙，反馈失败！',
          duration: 2000
        });
        app.serverBusy();
        return;
      }
    });
  }
})