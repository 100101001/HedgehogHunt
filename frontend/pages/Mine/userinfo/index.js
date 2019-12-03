var util = require("../../../utils/util.js");
var app = getApp();
const HedgeHogClient = require('../../../utils/api').HedgeHogClient
Page({
  data: {
    items: [{
        name: "姓名",
        value: "韦朝旭",
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
        act: "onChooseAddresTap",
        src: '/images/icons/write.png',
      }
    ],
    qr_code_list: [
      "/images/more/wcx.jpg",
    ],
    has_qrcode: false,
    show_qrcode: false

  },
  onLoad: function() {
    var that = this
    // wx.request(HedgeHogClient.GetUserInfoRequest(1, function (res) {
    //   that.setData({
    //     userinfo: res.data
    //   })
    // }))
  },
  onChooseAddresTap: function(event) {
    var that = this;
    var items = that.data.items;
    wx.chooseAddress({
      success(res) {
        console.log(res)
        items[0].value = res.userName;
        items[1].value = res.telNumber;
        items[2].value = res.cityName + res.countyName + res.detailInfo;
        that.setData({
          items: items
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
  getQrCode: function() {
    if (!this.data.has_qrcode) {
      app.alert({
        'content': "从网页获取二维码"
      });
      wx.request({
        url: app.buildUrl('/member/share'),
        success: function(res) {
          var resp = res.data;
          if (resp.code != 200) {
            app.alert({
              'content': resp.msg
            });
            return;
          }
          wx.showToast({
            title: '分享成功！',
            icon: 'success',
            content: '积分+5',
            duration: 3000
          })
        },
        fail: function(res) {
          app.serverBusy();
          return;
        }
      })
    }
  },
  checkQrCode:function(){
    var show_qrcode=!this.data.show_qrcode;
    this.setData({
      show_qrcode:show_qrcode
    });
  },
  //预览图片
  previewImage: function (e) {
    var id = e.currentTarget.dataset.id;
    var qr_code_list = this.data.qr_code_list;
    wx.previewImage({
      current: qr_code_list[id], // 当前显示图片的http链接  
      urls: qr_code_list // 需要预览的图片http链接列表  
    })
  }

})