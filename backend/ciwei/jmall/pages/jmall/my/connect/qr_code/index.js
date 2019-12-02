// pages/jmall/my/controls/feedback/index.js
Page({
  data: {
    show_qr_code: true,
    qr_code_list: ["/images/more/qr_code.jpg"],
  },
  onLoad: function(options) {},

  //预览图片
  previewQrCodeImage: function(e) {
    var current = e.target.dataset.src;
    var qr_code_list=this.data.qr_code_list;
    wx.previewImage({
      current: current, // 当前显示图片的http链接  
      urls: qr_code_list // 需要预览的图片http链接列表  
    })
  },

  //选择图片方法
  chooseQrcode: function(e) {
    var that = this; //获取上下文
    //选择图片
    var qr_code_list = this.data.qr_code_list;
    if (qr_code_list.length>0) {
      wx.showModal({
        title: '提示',
        content: "如需更新，请删除原文件再上传",
      })
    } else {
      wx.chooseImage({
        count: 1,
        sizeType: ['compressed'],
        sourceType: ['album'],
        success: function(res) {
          var tempFiles = res.tempFiles;
          var qr_code_list=[];
          qr_code_list.push(tempFiles[0].path);
          console.log(tempFiles[0].path);
          console.log(qr_code_list[0]);
          //显示
          that.setData({
            qr_code_list: qr_code_list ,
            show_qr_code: true,
          });
        }
      })
    }
  },
  //点击上传事件
  upLoadPics: function() {

  },
  // 删除图片
  deleteQrcode: function(e) {
    this.setData({
      qr_code_list: [],
      show_qr_code: false,
    });
  },
  //表单提交
  formSubmit: function(e) {
    //跳转到首页级页面，需要使用switchTab
    wx.showModal({
      title: '上传路径',
      content: this.data.qr_code_src,
      complete: function() {
        wx.navigateBack({})
      }
    })

  },
})