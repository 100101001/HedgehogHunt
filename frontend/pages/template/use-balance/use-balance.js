const app = getApp()


/**
 * 勾选框状态变化
 * 如果状态变为勾选：
 * 1、如果有二维码且账户没有通讯费，则提示让用户慎用余额
 * 2、否则就直接勾选
 * @param cb_confirm
 */
const changeUseBalance = function (e = {}, cb_confirm = () => {}) {
  //如果勾选使余额，对有二维码的用户进行余额使用预警
  if (e.detail.value.length == 1) {
    wx.request({
      url: app.buildUrl("/balance/use/warn"),
      header: app.getRequestHeader(),
      success: res => {
        let resp = res.data
        if (resp['code'] !== 200) {
          cb_confirm()
          return
        }
        if (resp['data']) {
          //谨慎操作提示
          app.alert({
            title: "谨慎操作",
            content: "务必确保账户余额充足以便接收短信通知！！",
            cb_confirm: cb_confirm
          })
        } else {
          cb_confirm()
        }
      }
    })
  } else {
    cb_confirm()
  }
}

/**
 * 如果余额大于5毛钱则
 * @param cb_confirm
 */
const initData = function (that, cb_success=(total_balance)=>{}){
  wx.request({
    url: app.buildUrl("/member/balance"),
    header: app.getRequestHeader(),
    success: res => {
      let resp = res.data
      if (resp['code'] !== 200) {
        that.setData({
          balance_got: false
        })
        return
      }
      let balance = parseFloat(resp['data']['balance'])
      that.setData({
        balance_got: balance > 0, //没有余额不可见
        balance_use_disabled: balance <= 0, //禁用选项框
        balance_low: balance <= 0, //余额低于0不可用
        total_balance: balance, //余额总量
        balance: 0 // 可用余额
      })
      cb_success(balance)
    }, fail: res => {
      app.serverBusy()
    }
  })
}

module.exports ={
  changeUseBalance: changeUseBalance,
  initData: initData
}