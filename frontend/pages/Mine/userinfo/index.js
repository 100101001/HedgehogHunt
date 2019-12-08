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
    var that = this
    if (!this.data.has_qrcode) {
      wx.request({
        method:'post',
        url: app.buildUrl('/member/qrcode'),
        header: { 
          'content-type': 'application/json' 
        }, 
        data: {
          memberId:1,
          orderId:1,
          username:"lyx1"
        }, 
        success: function(res) {
          console.log(res)
          if(res.statusCode === 200){
            var resp = res.data;
            that.setData({
              // qrCode:"data:image/jpeg;base64,"+wx.arrayBufferToBase64(resp),
              qrCode:"data:image/jpeg;base64,"+resp,
              has_qrcode:true,
              show_qrcode:true
            })
          }
          else{
            app.serverInternalError()
          }
        },
        fail: function(res) {
          app.serverBusy()
        }
      })
    }else {
      //从db直接拿
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