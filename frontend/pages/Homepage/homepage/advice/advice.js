Page({

  onSubmitTap: function (event) {
    wx.showModal({
      title: '提交函数',
      content: "我写了提交函数....壳",
    })
  },

  //点击图片添加容器之后调用添加图片的API，存在bug
  onAddPhotoTap:function(event){
    wx.chooseImage({
      count:9,
      sizeType:['original','compressed'],
      sourceType:['album','camera'],
      success: function(res) {
        //多次选择一张照片，需把每次上传的图片拼接到一个数组中渲染
        var tempFile=res.tempFilePaths;
        for (var i in res.tempFilePaths){
          tempFilePaths=tempFilePaths.concat(res.tempFilePaths[i]);
        }
        thi.setData({
          tempFilePaths:tempFilePaths,
        })

      },
    })
  }
  
})