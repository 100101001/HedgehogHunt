const app = getApp();

Page({
  data: {
    userInfo: {},
    has_qrcode: false,
    show_qrcode: false,
    qr_code: "",
    hiddenNameModal: true,
    hiddenMobileModal: true,
    hiddenContactModal: true,
    contact_img: app.globalData.static_file_domain + "/static/QRcode.jpg"
  },
  onLoad: function () {
  },
  onShow() {
    // 会员的闪寻码信息
    this.getMemberInfo()
  },
  getMemberInfo: function(){
    wx.request({
      url: app.buildUrl("/member/info"),
      header: app.getRequestHeader(),
      success: (res) => {
        let resp = res.data
        if (resp['code'] !== 200) {
          app.alert({
            content: resp['msg'],
            cb_confirm: () => {
              wx.navigateBack()
            }
          })
          return
        }
        let info = resp['data']['info']
        this.setData({
          avatar: info['avatar'],
          nickname: info['nickname'],
          name: info['name'],
          mobile: info['mobile'],
          balance: info['balance'],
          has_qrcode: info['has_qrcode'],
          qr_code: info['qr_code']
        })
      },
      fail: (res) => {
        app.serverBusy()
        wx.navigateBack()
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
    this.doSetName()
  },
  doSetName: function () {
    this.showToast('设置中', 'loading')
    wx.request({
      method: 'POST',
      url: app.buildUrl('/member/set/name'),
      header: app.getRequestHeader(),
      data: {name: this.data.editName},
      success: res => {
        let resp = res.data
        if (resp['code'] !== 200) {
          app.alert({content: resp['msg']})
          return
        }
        this.setData({
          name: resp.data.name,
          hiddenNameModal: true
        })
      }, complete: res => {
        wx.hideToast()
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
    this.doGetQrCode()
  },
  /***
   * doGetQrCode 去下单获取二维码
   */
  doGetQrCode: function () {
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
    this.setData({
      show_qrcode: !this.data.show_qrcode
    })
  },
  onWithDrawTap: function () {
    if (this.data.balance < 10) {
      app.alert({
        title: '提现提示',
        content: '额度满10元即可提现'
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
    let image = e.currentTarget.dataset.src
    wx.previewImage({
      current: image, // 当前显示图片的http链接
      urls: [image] // 需要预览的图片http链接列表
    })
  },
  toIntroduce: function () {


  },
  toEditPhone: function () {
    wx.navigateTo({
      url: '/pages/Qrcode/Mobile/index'
    })
    this.cancelMobileEdit()
  }
})