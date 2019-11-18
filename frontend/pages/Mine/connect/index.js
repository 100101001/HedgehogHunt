// pages/jmall/my/controls/feedback/index.js
Page({
  data: {
    show_qr_code: true,
    qr_code_list: [
      "/images/more/mhx.jpg",
      "/images/more/wcx.jpg",
    ],
  },
  onLoad: function (options) { },

  //预览图片
  previewImage: function (e) {
    var id = e.currentTarget.dataset.id;
    var qr_code_list = this.data.qr_code_list;
    wx.previewImage({
      current: qr_code_list[id], // 当前显示图片的http链接  
      urls: qr_code_list // 需要预览的图片http链接列表  
    })
  }
})