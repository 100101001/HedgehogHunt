const navigate = require("../template/navigate-bar/navigate-bar-template.js")
const util = require("../../utils/util.js")
const app = getApp()



/**
 * hasQrcode 用户是否有二维码
 * @param cb_success
 */
const hasQrcode = function (cb_complete=()=>{}) {
  wx.request({
    url: app.buildUrl("/member/has-qrcode"),
    header: app.getRequestHeader(),
    success: res => {
      let resp = res.data
      if (resp['code'] !== 200) {
        cb_complete(false)
        return
      }
      cb_complete(resp['data']['has_qr_code'])
    }, fail: res => {
      cb_complete(false)
    }
  })
}

/**
 * getNewRecommend 获取新消息计数
 * @param cb_complete
 */
const getNewRecommend = function(cb_complete=(total_new=0)=>{}){
  wx.request({
    url: app.buildUrl('/member/get-new-recommend'),
    header: app.getRequestHeader(),
    success: (res) => {
      let resp = res.data
      if (resp['code'] !== 200) {
        cb_complete(0)
        return
      }
      let data = resp['data']
      app.globalData.total_new = data.total_new;
      app.globalData.recommend_new = data.recommend_new;
      app.globalData.thanks_new = data.thanks_new;
      app.globalData.recommend = data.recommend;
      cb_complete(data.total_new)
    },
    fail: res => {
      cb_complete(0)
    }
  })
}

// pages/Homepage/index.js
Page({

  /**
   * 页面的初始数据
   */
  data: {

  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad: function (options) {

  },

  /**
   * 生命周期函数--监听页面初次渲染完成
   */
  onReady: function () {

  },

  /**
   * 生命周期函数--监听页面显示
   */
  onShow: function () {
    let [isSelecteds, urls] = util.onNavigateTap()  //不传值代表没有页被选中
    isSelecteds['showHintQrcode'] = app.globalData.showHintQrcode
    isSelecteds['regFlag'] = app.globalData.regFlag
    hasQrcode((has_qrcode) => {
      isSelecteds['hasQrcode'] = has_qrcode
      getNewRecommend((total_new = 0) => {
        isSelecteds['total_new'] = total_new
        this.setData({
          isSelecteds: isSelecteds
        })
      })
    })
  },

  /**
   * 生命周期函数--监听页面隐藏
   */
  onHide: function () {

  },

  /**
   * 生命周期函数--监听页面卸载
   */
  onUnload: function () {

  },

  /**
   * 页面相关事件处理函数--监听用户下拉动作
   */
  onPullDownRefresh: function () {

  },

  /**
   * 页面上拉触底事件的处理函数
   */
  onReachBottom: function () {

  },

  /**
   * 用户点击右上角分享
   */
  onShareAppMessage: function () {

  },
  //点击导航
  onNavigateTap: function (event) {
    navigate.onNavigateTap(event, this)
  },
  tapOnHint: function(e){
    navigate.tapOnHint(this)
  },
  closeQrcodeHint: function (e) {
    navigate.closeQrcodeHint(this)
  },
  toSeeQrcode: function () {
    navigate.toSeeQrcode(this)
  },
  toGetQrcode: function () {
    navigate.toGetQrcode(this)
  },
  toLogin: function () {
    navigate.toLogin(this)
  }
})