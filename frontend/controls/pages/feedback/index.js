// pages/jmall/my/controls/feedback/index.js
const app = getApp();
Page({
  data: {
    text_placeholder: "使用过程中遇到的问题，UI的设计优化，功能的增减，使用体验，以及鼓励和认可，都欢迎反馈!",
    imglist: [],
    count: 1,
    pic_status: true,
    loadingHidden: true,
    submit_disabled: false,
    empty: true,
    focus: false,
    warn: false
  },
  onLoad: function (options) {
  },

  /**
   * 点击已添加图片进入预览
   * @param e
   */
  previewImage: function (e) {
    wx.previewImage({
      current: e.target.dataset.src, // 当前显示图片的http链接
      urls: this.data.imglist // 需要预览的图片http链接列表
    })
  },

  /**
   * 选择本地图片添加
   * @param e
   */
  chooseLoadPics: function (e) {
    let imglist = this.data.imglist;
    //选择图片
    wx.chooseImage({
      count: 8 - imglist.length,
      sizeType: ['compressed'],
      sourceType: ['album', 'camera'],
      success:  (res) => {
        imglist = app.addImages(res.tempFiles, imglist);
        //显示
        this.setData({
          imglist: imglist,
          pic_status: imglist.length < 9
        });
      }
    })
  },
  /**
   * 删除添加的本地图片
   * @param e
   */
  deleteImg: function (e) {
    let imglist = this.data.imglist;
    imglist.splice(e.currentTarget.dataset.index, 1);
    this.setData({
      imglist: imglist,
      pic_status: imglist.length < 9
    });
  },
  formSubmit: function (e) {
    this.setData({
      submit_disabled: true
    });
    let data = e.detail.value;
    if (data.summary === '') {
      app.alert({
        title: '提交提示',
        content: '请填写反馈内容后提交'
      });
      this.setData({
        submit_disabled: false
      });
      return
    }
    app.alert({
      title: '反馈提示',
      content: '确认提交？',
      showCancel: true,
      cb_confirm: ()=>{
        let img_list = this.data.imglist;
        let url = "/feedback/create";
        data['has_img'] = img_list.length !== 0;
        this.uploadData(data, url, img_list);
      }
    })
  },
  /**
   * 上传反馈数据
   * @param data
   * @param url
   * @param img_list
   */
  uploadData: function (data, url, img_list) {
    wx.request({
      url: app.buildUrl(url),
      method: 'POST',
      header: app.getRequestHeader(),
      data: data,
      success:  (res) => {
        let resp = res.data;
        if (resp['code'] !== 200) {
          app.alert({content: resp['msg']});
          this.setData({
            submit_disabled: false
          });
          return
        }
        //获取商品的id,之后用于提交图片
        this.uploadImage(resp['data']['id'], img_list);
      },
      fail:  (res) => {
        this.setData({
          submit_disabled: false
        });
        app.serverBusy();
      },
      complete:  (res) => {
        this.setData({
          loadingHidden: true
        });
      },
    });
  },
  /**
   * 上传反馈图片
   * @param id
   * @param img_list
   */
  uploadImage: function (id, img_list) {
    let n = img_list.length;
    for (let i = 1; i <= n; i++) {
      //正在上传第 i 张图片的loading
      this.setData({
        i: i,
        loadingHidden: false,
      });
      //为
      this.addImage(img_list[i-1], id, n === i)
    }
  },
  /**
   *
   * @param image_file
   * @param feedback_id
   * @param end
   */
  addImage: function(image_file='', feedback_id=0, end = false){
    //图片不存在，则重新上传
    wx.uploadFile({
      url: app.buildUrl('/feedback/add-pics'), //接口地址
      header: app.getRequestHeader(),
      filePath: image_file,//文件路径
      formData: {'id': feedback_id},
      name: 'file',//文件名，不要修改，Flask直接读取
      success:  (res) => {
        if (end) {
          this.endCreate(feedback_id);
        }
      },
      fail:  (res) => {
        this.setData({
          submit_disabled: false
        });
        app.serverBusy();
      },
      complete:  (res) => {
        this.setData({
          loadingHidden: true
        });
      },
    })
  },
  /**
   * 结束创建 endCreate
   * @param id
   */
  endCreate: function (id = 0) {
    wx.request({
      url: app.buildUrl("/feedback/end-create"),
      method: 'POST',
      header: app.getRequestHeader(),
      data: {id: id},
      success: (res) => {
        let resp = res.data;
        if (resp['code'] !== 200) {
          app.alert({content: resp['msg']});
          this.setData({
            submit_disabled: false
          });
          return
        }
        wx.showToast({
          title: '提交成功,感谢反馈！    ',
          icon: 'success',
          duration: 1000,
          success: (res) => {
            setTimeout(wx.navigateBack, 800);
          }
        });
      },
      fail: (res) => {
        this.setData({
          submit_disabled: false
        });
        app.serverBusy();
      },
      complete: (res) => {
        this.setData({
          loadingHidden: true
        });
      },
    });
  },
  /**
   * 监听输入
   * @param e
   */
  feedbackInput: function (e) {
    this.setData({
      warn: e.detail.value.length >= 130,
      empty: e.detail.value.length === 0
    })
  },
  feedbackFocus: function (e) {
    this.setData({
      focus: 1
    })
  },
  feedbackBlur: function (e) {
    this.setData({
      focus: 0
    })
  },
});