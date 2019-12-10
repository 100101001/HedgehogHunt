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
    // qr_code_list: [
    //   "/images/more/wcx.jpg",
    // ],
    userInfo: {},
    has_qrcode: false,
    show_qrcode: false,
    qrCode: ""
  },
  onLoad: function () {
    var that = this;
    var base64code = wx.getStorageSync('qrcode')
    if (base64code) {
      console.log("获取到了缓存的qrcode")
      // Do something with return value
      this.setData({
        qrCode: base64code,
        has_qrcode: true
      })
    } else {
      //尝试获取数据库存储的该会员的二维码，根据状态码
      //判断是否获取到了，以此
      //设置页面数据has_qrcode，和qrCode
      wx.request({
        method: 'post',
        url: app.buildUrl('/qrcode/db'),
        data: {
          memberId: 1
        },
        success: function (res) {
          if (res.statusCode == 200) {
            console.log("获取到了数据库的qrcode,存到缓存")
            wx.setStorage({
              key: "qrcode",
              data: "data:image/jpeg;base64," + res.data
            })
            that.setData({
              qrCode: "data:image/jpeg;base64," + res.data,
              has_qrcode: true
            })
          } else if (res.statusCode == 201) {
            console.log("没获取到")
            that.setData({
              has_qrcode: false
            })
          } else if (res.statusCode == 500) {
            app.serverInternalError()
          }
        },
        fail: function (res) {
          app.serverBusy()
        }
      })
    }


    // while (app.globalData.userInfo == null) {
    //   //app 还没获取到userInfo，空等待  
    // }
    this.setData({
      userInfo: app.globalData.userInfo
    });
  },
  onChooseAddresTap: function (event) {
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
      }
    })
  },
  getQrCode: function () {
    var that = this
    if (!this.data.has_qrcode) {
      wx.request({
        method: 'post',
        url: app.buildUrl('/qrcode/wx'),
        header: {
          'content-type': 'application/json'
        },
        data: {
          memberId: 1,
          orderId: 1,
          username: "lyx1"
        },
        success: function (res) {
          console.log(res)
          if (res.statusCode === 200) {
            var resp = res.data;
            that.setData({
              // qrCode:"data:image/jpeg;base64,"+wx.arrayBufferToBase64(resp),
              qrCode: "data:image/jpeg;base64," + resp,
              has_qrcode: true,
              show_qrcode: true
            })
          }
          else {
            app.serverInternalError()
          }
        },
        fail: function (res) {
          app.serverBusy()
        }
      })
    } else {
      //从db直接拿
    }
  },
  checkQrCode: function () {
    var show_qrcode = !this.data.show_qrcode;
    console.log("点了查看 " + show_qrcode)
    this.setData({
      show_qrcode: show_qrcode
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