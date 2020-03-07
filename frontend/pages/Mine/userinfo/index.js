var util = require("../../../utils/util.js");
var app = getApp();
Page({
  data: {
    userInfo: {},
    has_qrcode: false,
    show_qrcode: false,
    qrCode: ""
  },
  onLoad: function () {
    //会员基本信息
    var receiver = app.globalData.memberInfo.name == "" ? wx.getStorageSync('receiver') : app.globalData.memberInfo.name
    var mobile = app.globalData.memberInfo.mobile == "" ? wx.getStorageSync('mobile') : app.globalData.memberInfo.mobile
    var address = app.globalData.memberInfo.location == "" ? wx.getStorageSync('location') : app.globalData.memberInfo.location
    var balance = app.globalData.memberInfo.balance
    this.setData({
      items: [{
        name: "姓名",
        value: receiver == "" ? "-" : receiver,
      },
      {
        name: "电话",
        value: mobile == "" ? "-" : mobile,
      },
      {
        name: "收件地址",
        value: address == "" ? "-" : address,
      },
      {
        name: "编辑个人信息",
        value: "",
        act: "onChooseAddresTap",
        src: '/images/icons/write.png',
      }
      ],
    })
    this.setData({
      userInfo: app.globalData.memberInfo,
      has_qrcode: app.globalData.has_qrcode,
      qrCode: app.globalData.has_qrcode ? app.globalData.qr_code_list[0] : "",
      balance: balance
    });
  },
  onChooseAddresTap: function (event) {
    var that = this;
    var items = that.data.items;
    var has_qrcode = this.data.has_qrcode
    wx.chooseAddress({
      success(res) {
        console.log(res)
        items[0].value = app.globalData.memberInfo.name = res.userName;
        items[1].value = app.globalData.memberInfo.mobile = res.telNumber;
        items[2].value = app.globalData.memberInfo.location = res.cityName + res.countyName + res.detailInfo;
        wx.request({
          url: app.buildUrl('/member/contactinfo/set'),
          header: app.getRequestHeader(),
          method: 'POST',
          data: {
            mobile: res.telNumber,
            name: res.userName,
            location: res.cityName + res.countyName + res.detailInfo
          }
        })
        if (has_qrcode) {
          wx.request({
            url: app.buildUrl('/qrcode/contactinfo/set'),
            header: app.getRequestHeader(),
            method: 'POST',
            data: {
              mobile: res.telNumber,
              name: res.userName,
              location: res.cityName + res.countyName + res.detailInfo
            }
          })
        }
        that.setData({
          items: items
        })
        wx.setStorage({
          key: 'receiver',
          data: items[0].value
        });
        wx.setStorage({
          key: 'mobile',
          data: items[1].value
        });
        wx.setStorage({
          key: 'address',
          data: items[2].value
        });
      }
    })
  },
  getQrCode: function () {
    var that = this
    var items = this.data.items
    if (items[0].value == "-" || items[1].value == "-") {
      app.alert({ 'content': '先【编辑个人信息】完善联络信息' })
      return
    }
    if (!this.data.has_qrcode) {
      wx.request({
        method: 'post',
        url: app.buildUrl('/qrcode/wx'),
        data: {
          name: items[0].value,
          mobile: items[1].value,
          location: items[2].value
        },
        header: app.getRequestHeader(),
        success: function (res) {
          var resp = res.data
          if (resp.code === 200) {
            app.globalData.has_qrcode = true
            app.globalData.qr_code_list = [resp.data.qr_code_url]
            that.setData({
              qrCode: resp.data.qr_code_url,
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
    }
  },
  checkQrCode: function () {
    var show_qrcode = !this.data.show_qrcode;
    this.setData({
      show_qrcode: show_qrcode
    });
  },

  //开始点击的时间
  touchstart: function (e) {
    this.setData({ touchstart: e.timeStamp })
  },

  //点击结束的时间
  touchend: function (e) {
    this.setData({ touchend: e.timeStamp })
  },

  //保存图片
  saveImg: function (e) {
    var that = this
    var touched_time = that.data.touchend - that.data.touchstart
    //0.3s
    if (touched_time > 300) {
      wx.showLoading({
        title: '保存中，请稍等~',
      })
      wx.getSetting({
        success: function (res) {
          wx.authorize({
            scope: 'scope.writePhotosAlbum',
            success: function () {
              var img_url = that.data.qrCode //图片地址
              wx.downloadFile({ //下载文件资源到本地，客户端直接发起一个 HTTP GET 请求，返回文件的本地临时路径
                url: img_url,
                success: function (res) {
                  // 下载成功后再保存到本地
                  wx.saveImageToPhotosAlbum({
                    filePath: res.tempFilePath,//返回的临时文件路径，下载后的文件会存储到一个临时文件
                    success: function (res) {
                      wx.showToast({
                        title: '保存到本地相册',
                        complete: res => {
                          wx.hideLoading({
                            complete: (res) => { },
                          })
                        }
                      })
                    },
                    fail: function (res) {
                      wx.hideLoading({
                        complete: (res) => { },
                      })
                    }
                  })
                }
              })
            }
          })
        }
      })
    }
  },
  onWithDrawTap: function () {
    var balance = this.data.balance
    if (balance < 50) {
      app.alert({
        'title': '温馨提示',
        'content': '账户余额不足￥50不能提现'
      })
      return
    }
    app.alert({
      'title': '温馨提示',
      'content': '提现模块正在开发中，请联系客服提现'
    })
  }
})