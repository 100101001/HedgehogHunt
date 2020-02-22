const util = require("../../../utils/util.js");
const app = getApp();
const onNavigateTap = function (event, that) {
  var id = event.currentTarget.dataset.id * 1; //乘1强制转换成数字
  //TODO: 希望登录后直接进入页面
  if ((id == 1 || id == 2) && !app.loginTip()) {
    return;
  }
  var [isSelecteds, urls] = util.onNavigateTap(id);
  that.setData({
    isSelecteds: isSelecteds
  })
  wx.reLaunch({
    url: urls[id],
  })
}

module.exports = {
  onNavigateTap: onNavigateTap
}