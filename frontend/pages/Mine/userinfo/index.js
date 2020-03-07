var app = getApp();
Page({
  data: {
    userInfo: {},
    has_qrcode: false,
    show_qrcode: false,
    qrCode: "",
    hiddenNameModal: true,
    hiddenMobileModal: true,
    nameInputfocus: false
  },
  onLoad: function () {
    //会员基本信息
    var name = app.globalData.memberInfo.name
    var mobile = app.globalData.memberInfo.mobile
    var balance = app.globalData.memberInfo.balance
    this.setData({
      avatar: app.globalData.memberInfo.avatar,
      nickname: app.globalData.memberInfo.nickname,
      mobile: mobile == "" ? "-" : mobile,
      name: name == "" ? "-" : name,
      has_qrcode: app.globalData.has_qrcode,
      qrCode: app.globalData.has_qrcode ? app.globalData.qr_code_list[0] : "",
      balance: balance
    });
  },
  getPhoneNumber(e) {
    var msg = e.detail.errMsg
    var that = this
    var session_key = app.getCache("loginInfo").session_key
    var encryptedData = e.detail.encryptedData
    var iv = e.detail.iv;
    if(msg == "getPhoneNumber:fail:user deny"){
      this.setData({
        hiddenMobileModal: true
      })
      return
    }
    if (msg == 'getPhoneNumber:ok') {
      wx.checkSession({
        success: function () {
          that.deciyption(session_key, encryptedData, iv);
        },
        fail: function (res) {
          console.log(res)
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
                  if(resp.code!==200){
                    app.alert({
                      'content': resp.msg
                    })
                    return
                  }
                  var loginInfo = resp.data;
                  app.setCache('loginInfo', loginInfo);
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
      nameInputfocus: true
    })
  },
  cancelNameEdit: function () {
    this.setData({
      hiddenNameModal: true,
      nameInputfocus: false
    })
  },
  confirmNameEdit: function (e) {
    if (this.data.editName == "") {
      app.alert({
        'content': '姓名不能为空'
      })
      return
    }
    if(this.data.name == this.data.editName){
      app.alert({
        'content': '未修改'
      })
      return
    }
    var that = this
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
  getQrCode: function () {
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
    if (!this.data.has_qrcode) {
      wx.showLoading({
        title: '正在获取..',
      })
      var that = this
      wx.request({
        method: 'post',
        url: app.buildUrl('/qrcode/wx'),
        header: app.getRequestHeader(),
        success: function (res) {
          var resp = res.data
          if(resp.code!==200){
            app.alert({
              'content': resp.msg
            })
            return
          }
          app.globalData.has_qrcode = true
          app.globalData.qr_code_list = [resp.data.qr_code_url]
          that.setData({
            qrCode: resp.data.qr_code_url,
            has_qrcode: true,
            show_qrcode: true
          })
        },
        fail: function (res) {
          app.serverBusy()
        },
        complete:res=>{
          wx.hideLoading()
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
    if (balance < 10) {
      app.alert({
        'title': '温馨提示',
        'content': '账户余额不足￥10不能提现'
      })
      return
    }
    app.alert({
      'title': '温馨提示',
      'content': '提现模块正在开发中，请联系客服提现'
    })
  }
})