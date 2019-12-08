const app = getApp()
// pages/Qrcode/Qrcode.js
Page({

  /**
   * 页面的初始数据
   */
  data: {
    register:false,
    release:false
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad: function (options) {
    console.log("扫了二维码")
    console.log(options)
    wx.request({
      method:"post",
      url:app.buildUrl("/qrcode/scan"),
      data: {
        id:options.id
      },
      success: function(res) {
        if(res.data == true){
          wx.navigateTo({
            url: "/pages/Release/release/index"
          })
        }else {
          wx.navigateTo({
            url: "/pages/Qrcode/register/index"
          })
        }
      },
      fail:function(res) {
        app.serverBusy()
      }
    })
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

  }
})