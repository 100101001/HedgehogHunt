const util = require("../../../utils/util.js")
const app = getApp()

/**
 * 点击了导航栏
 * @param event
 * @param object
 */
const onNavigateTap = function (event, that) {
  let id = event.currentTarget.dataset.id * 1; //乘1强制转换成数字
  //TODO: 希望登录后直接进入页面
  if ((id === 4 || id === 2) && !app.loginTip()) {
    return
  }
  if(id === 1 || id === 3){
    that.businessTypeClick()
  } else {
    //导航，并延时隐藏提示浮窗
    wx.navigateTo({
      url: app.globalData.navigateUrls[id],
      success: () => {
        hideHint(that)
      }
    })
  }
}

const closeQrcodeHint = function (that) {

  let hint_content = ''
  if (app.globalData.regFlag) {
    hint_content = '在【我的】-【个人信息】' + (app.globalData.has_qrcode ? '查看' : '获取')
  } else {
    hint_content = '部分功能需要登录使用'
  }

  app.alert({
    title: '关闭确认',
    content: hint_content,
    cb_confirm: function () {
      app.globalData.showHintQrcode = false
      let isSelecteds = that.data.isSelecteds
      isSelecteds['showHintQrcode'] = false
      that.setData({
        isSelecteds: isSelecteds
      })
    },
    showCancel: true
  })
}

const toGetQrcode = function (that) {
  wx.navigateTo({
    url: '/pages/Mine/userinfo/index',
    success: ()=>{
      hideHint(that)
    }
  })
}

const toLogin = function (that) {
  wx.navigateTo({
    url: '/pages/login/index',
    success: ()=>{
      hideHint(that)
    }
  })
}

const toSeeQrcode=function (that) {
  wx.navigateTo({
    url: '/pages/Mine/userinfo/index',
    success: res => {
      //关闭浮窗，为了回来能显示动画效果
      hideHint(that)
    }
  })
}


const hideHint = function (that) {
  setTimeout(()=>{
    let isSelecteds = that.data.isSelecteds
    isSelecteds['showHintQrcode'] = false
    that.setData({
      isSelecteds: isSelecteds
    })
  }, 300)
}


const tapOnHint = function(that){
  that.setData({
    touch_hint: true
  })
  setTimeout(()=>{
    that.setData({
      touch_hint: false
    })
  }, 1000)
}

module.exports = {
  onNavigateTap: onNavigateTap,
  closeQrcodeHint: closeQrcodeHint,
  toGetQrcode: toGetQrcode,
  toSeeQrcode: toSeeQrcode,
  toLogin: toLogin,
  tapOnHint: tapOnHint
}