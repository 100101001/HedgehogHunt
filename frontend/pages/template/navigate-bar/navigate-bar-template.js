const util = require("../../../utils/util.js");
const app=getApp();
const onNavigateTap = function(event, object) {
    var id = event.currentTarget.dataset.id * 1; //乘1强制转换成数字
    //TODO: 希望登录后直接进入页面
    if((id==4||id==2) && !app.loginTip()){
        return;
    }
    app.getNewRecommend();
    var [isSelecteds, urls] = util.onNavigateTap(id);
    object.setData({
      isSelecteds: isSelecteds
    })
    wx.redirectTo({
      url: urls[id],
    })
}

module.exports = {
    onNavigateTap:onNavigateTap
}