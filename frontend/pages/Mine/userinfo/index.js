var app = getApp();

Page({
  data: {
    userInfo: {},
    has_qrcode: false,
    show_qrcode: false,
    qrCode: "",
    hiddenNameModal: true,
    hiddenMobileModal: true,
    hiddenContactModal: true,
    contact_img: app.globalData.static_file_domain + "/static/QRcode.jpg"
  },
  onLoad: function () {
    //会员基本信息
    var name = app.globalData.memberInfo.name
    var mobile = app.globalData.memberInfo.mobile
    this.setData({
      avatar: app.globalData.memberInfo.avatar,
      nickname: app.globalData.memberInfo.nickname,
      mobile: mobile == "" ? "-" : mobile,
      name: name == "" ? "-" : name,
      balance: app.globalData.memberInfo.balance
    });
  },
  onShow() {
    wx.checkSession({
      fail: (res) => {
        wx.login({
          success: res => {
            wx.request({
              method: 'POST',
              url: app.buildUrl('/member/login/wx'),
              header: {
                'content-type': 'application/json',
              },
              data: {code: res.code},
              success: res => {
                app.setCache("loginInfo", res.data.data)
              }
            })
          }
        })
      }
    })
    // 会员的闪寻码信息
    this.setData({
      has_qrcode: app.globalData.has_qrcode,
      qrCode: app.globalData.has_qrcode ? app.globalData.qr_code_list[0] : "",
    })
  },
  getPhoneNumber(e) {
    console.log(e)
    var msg = e.detail.errMsg
    var that = this
    var session_key = app.getCache('loginInfo').session_key
    var encryptedData = e.detail.encryptedData
    var iv = e.detail.iv;
    if (msg == "getPhoneNumber:fail:user deny") {
      this.setData({
        hiddenMobileModal: true
      })
      return
    }
    if (msg == 'getPhoneNumber:ok') {
      wx.checkSession({
        success: (res) => {
          that.deciyption(session_key, encryptedData, iv);
        },
        fail: (res) => {
          wx.login({
            success: res => {
              wx.request({
                method: 'POST',
                url: app.buildUrl('/member/login/wx'),
                header: {
                  'content-type': 'application/json',
                },
                data: { code: res.code },
                success: function (res) {
                  var resp = res.data
                  if (resp.code !== 200) {
                    app.alert({
                      'content': resp.msg
                    })
                    return
                  }
                  var loginInfo = resp.data;
                  app.setCache('loginInfo', loginInfo)
                  that.deciyption(loginInfo.session_key, encryptedData, iv);
                }
              })
            }
          })
        }
      })
    }
  },
  deciyption(session_key, encryptedData, iv) {
    this.showToast('设置中', 'loading', 800)
    wx.request({
      method: 'POST',
      url: app.buildUrl('/member/set/phone'),
      header: app.getRequestHeader(1),
      data: {
        session_key: session_key,
        encrypted_data: encryptedData,
        iv: iv
      },
      success: res => {
        var resp = res.data
        if (resp.code !== 200) {
          app.alert({
            'content': resp.msg
          })
          return
        }
        app.globalData.memberInfo.mobile = resp.data.mobile
        this.setData({
          hiddenMobileModal: true,
          mobile: resp.data.mobile
        })
      }
    })
  },
  onEditMobile: function () {
    this.setData({
      hiddenMobileModal: false
    })
  },
  cancelMobileEdit: function () {
    this.setData({
      hiddenMobileModal: true
    })
  },
  onEditName: function () {
    this.setData({
      hiddenNameModal: false,
    })
  },
  cancelNameEdit: function () {
    this.setData({
      hiddenNameModal: true,
    })
  },
  showToast: function (title = '', icon = 'none', duraton = 1000, mask = true) {
    wx.showToast({
      'title': title,
      'icon': icon,
      'duraton': duraton,
      'mask': mask
    })
  },
  confirmNameEdit: function (e) {
    if (this.data.editName == "") {
      app.alert({
        'content': '姓名不能为空'
      })
      return
    }
    if (this.data.name == this.data.editName) {
      this.showToast('请填不同姓名!', 'none')
      return
    }
    var that = this
    this.showToast('设置中', 'loading')
    wx.request({
      method: 'POST',
      url: app.buildUrl('/member/set/name'),
      header: app.getRequestHeader(),
      data: { name: that.data.editName },
      success: res => {
        console.log(res)
        var resp = res.data
        if (resp.code !== 200) {
          app.alert({
            'content': resp.msg
          })
          return
        }
        app.globalData.memberInfo.name = resp.data.name
        this.setData({
          name: resp.data.name,
          hiddenNameModal: true,
          nameInputfocus: false
        })
      }
    })
  },
  listenerNameInput: function (e) {
    this.setData({
      editName: e.detail.value
    })
  },
  /***
   * toGetQrCode 判断没有姓名或手机号提示用户补上，否则继续下单获取二维码
   */
  toGetQrCode: function(){
    var name = this.data.name
    var mobile = this.data.mobile
    if (name == "-") {
      app.alert({ 'content': '姓名不能为空' })
      return
    }
    if (mobile == "-") {
      app.alert({ 'content': '手机不能为空' })
      return
    }
    this.getQrCode()
  },
  /***
   * getQrCode 去下单获取二维码
   */
  getQrCode: function () {
    //下单
    let data = {
      type: 'toBuy',
      goods: [{'id': app.globalData.qrcodeProductId, 'price': app.globalData.qrcodePrice, 'number': 1}]
    }
    wx.showToast({
      title: '前往下单',
      icon: 'loading',
      success: res => {
         setTimeout(function(){
           wx.navigateTo({
             'url' : '/mall/pages/order/index?data='+ JSON.stringify(data)
           })
         }, 200)
      }
    })
  },
  checkQrCode: function () {
    var show_qrcode = !this.data.show_qrcode;
    this.setData({
      show_qrcode: show_qrcode
    });
  },
  onWithDrawTap: function () {
    var balance = this.data.balance
    if (balance < 10) {
      app.alert({
        'title': '温馨提示',
        'content': '余额满10元即可提现'
      })
      return
    }
    this.setData({
      hiddenContactModal: false
    })
  },
  cancelContact: function (e) {
    this.setData({
      hiddenContactModal: true
    })
  },
  previewImage: function (e) {
    var image = e.currentTarget.dataset.src
    wx.previewImage({
      current: image, // 当前显示图片的http链接
      urls: [image] // 需要预览的图片http链接列表
    })
  },
})