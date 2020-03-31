// pages/jmall/my/controls/feedback/index.js
const app = getApp()
Page({
  data: {
    show_qr_code: true,
    qr_code_list: [
      "/images/more/wcx.jpg",
      "/images/more/lyx.jpg",
    ],
    qr_code_preview_list:[
      app.globalData.static_file_domain+"/static/wcx.jpg",
      app.globalData.static_file_domain +"/static/lyx.jpg"
    ],
    business_contact: true,
    tech_contact: true
  },
  onLoad: function (options) {
    if (options.only_tech_contact) {
      this.setData({
        business_contact: false
      })
    }
  },
  //预览图片
  previewImage: function (e) {
    var image = e.currentTarget.dataset.src;
    wx.previewImage({
      current: image, // 当前显示图片的http链接  
      urls: [image] // 需要预览的图片http链接列表  
    })
  }
})