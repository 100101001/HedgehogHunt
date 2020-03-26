const util = require("../../../utils/util.js");
const app = getApp();
const onNavigateTap = function (event, object) {
  var id = event.currentTarget.dataset.id * 1; //乘1强制转换成数字
  //TODO: 希望登录后直接进入页面
  if ((id == 4 || id == 2) && !app.loginTip()) {
    return;
  }
  app.getNewRecommend()
  var [isSelecteds, urls] = util.onNavigateTap(id);
  object.setData({
    isSelecteds: isSelecteds
  })

  //发布信息页面没有导航栏
  if (id == 2) {
    wx.navigateTo({
      url: urls[id]
    })
  } else {
    wx.redirectTo({
      url: urls[id],
    })
  }
}

const closeQrcodeHint = function (that) {
  app.alert({
    title: '关闭提示',
    content: '在【我的】-【个人信息】可' + (app.globalData.has_qrcode ? '查看' : '获取') + '您的专属闪寻码~',
    cb_confirm: function () {
      app.globalData.showHintQrcode = false
      var isSelecteds = that.data.isSelecteds
      isSelecteds['showHintQrcode'] = false
      that.setData({
        isSelecteds: isSelecteds
      })
    },
    showCancel: true
  })
}

const closeQrcodeHintConfirm = function (that) {
  app.globalData.showHintQrcode = false
  var isSelecteds = that.data.isSelecteds
  isSelecteds['showHintQrcode'] = false
  that.setData({
    isSelecteds: isSelecteds
  })
}

module.exports = {
  onNavigateTap: onNavigateTap,
  closeQrcodeHint: closeQrcodeHint,
  closeQrcodeHintConfirm: closeQrcodeHintConfirm
}