var app = getApp();
Page({
  data: {
    loadingHidden: true,
    tips_obj: {
      "goods_name": "广告名称",
      "target_price": "定价",
      "location": "地址",
      "stock": "库存",
      "summary": "描述",
    },
    imglist: [],
    flush: false,
    qr_code_list:[]
  },
  onLoad: function(options) {
    this.setInitData();
  },
  onShow: function() {

  },
  //预览图片
  previewImage: function(e) {
    var index = e.currentTarget.dataset.index;
    this.setData({
      flush: false,
    });
    wx.previewImage({
      current: this.data.imglist[index], // 当前显示图片的http链接
      urls: this.data.imglist // 需要预览的图片http链接列表
    })
  },
  //选择图片方法
  chooseLoadPics: function(e) {
    var that = this; //获取上下文
    var imglist = that.data.imglist;
    //选择图片
    wx.chooseImage({
      count: 8 - imglist.length,
      sizeType: ['compressed'],
      sourceType: ['album', 'camera'],
      success: function(res) {
        var tempFiles_ori = res.tempFiles;
        var imglist = that.data.imglist;
        imglist = app.addImages(tempFiles_ori, imglist);
        //显示
        that.setData({
          imglist: imglist,
          flush: false
        });
        if (imglist.length >= 9) {
          that.setData({
            pic_status: false,
          });
        } else {
          that.setData({
            pic_status: true,
          });
        }
      }
    })
  },
  // 删除图片
  deleteImg: function(e) {
    let index = e.currentTarget.dataset.index;
    let imglist = this.data.imglist;
    if (imglist.length === 1) {
      app.alert({
        'content': "删除失败，至少要提交一张图片"
      });
    } else {
      imglist.splice(index, 1);
      this.setData({
        imglist: imglist,
        flush: false,
      });
      if (imglist.length < 9) {
        this.setData({
          pic_status: true,
        });
      }
    }
  },
  //表单提交
  formSubmit: function(e) {
    var data = e.detail.value;
    var qr_code_list = this.data.qr_code_list;
    if (qr_code_list.length === 0) {
      app.alert({
        'content': "请添加用于联系的微信二维码"
      });
      return;
    }
    var tips_obj = this.data.tips_obj;
    var is_empty = app.judgeEmpty(data, tips_obj);
    if (is_empty) {
      return;
    }
    var img_list = this.data.imglist;
    if (img_list.length === 0) {
      app.alert({
        'content': "至少要提交一张图片"
      });
      return;
    }
    data['img_list'] = img_list;
    var url = "/adv/create";
    this.uploadData(data, url, img_list);
  },
  //上传文件
  uploadData: function(data, url, img_list) {
    var that = this;
    wx.request({
      url: app.buildUrl(url),
      method: 'POST',
      header: app.getRequestHeader(),
      data: data,
      success: function(res) {
        var resp = res.data;
        if (resp.code !== 200) {
          app.alert({
            'content': resp.msg
          });
          return
        }
        //获取商品的id,之后用于提交图片
        var id = resp.id;
        var img_list_status = resp.img_list_status;
        //地址提交过之后更新全局地址变量
        that.updateQrCode(id, img_list, img_list_status);
      },
      fail: function(res) {
        app.serverBusy();
        return;
      },
      complete: function(res) {

      },
    });
  },
  updateQrCode: function(id, img_list, img_list_status) {
    var that = this;
    var qr_code_list = this.data.qr_code_list;
    wx.uploadFile({
      url: app.buildUrl("/adv/add-qrcode"), //接口地址
      filePath: qr_code_list[0], //文件路径
      header: app.getRequestHeader(),
      formData: {
        'id': id,
      },
      name: 'file', //文件名，不要修改，Flask直接读取
      success: function(res) {
        that.uploadImage(id, img_list, img_list_status);
      },
      fail: function(res) {
        app.serverBusy();
        return;
      },
      complete: function(res) {
        that.setData({
          upload_qrcode: false,
        });
      },
    })
  },
  uploadImage: function(id, img_list, img_list_status) {
    var that = this;
    var n = img_list.length;
    for (var i = 1; i <= n; i++) {
      if (n === i) {
        var end_s = true;
      }
      this.setData({
        i: i,
        loadingHidden: false,
      });
      if (img_list_status[i - 1]) {
        //图片存在，则更新
        wx.request({
          url: app.buildUrl('/adv/update-pics'),
          method: 'POST',
          header: app.getRequestHeader(),
          data: {
            id: id,
            img_url: img_list[i - 1]
          },
          success: function(res) {
            if (end_s) {
              that.endCreate(id);
            }
          },
          fail: function(res) {
            app.serverBusy();
            return;
          },
          complete: function(res) {},
        })
      } else {
        //图片不存在存在，则重新上传
        wx.uploadFile({
          url: app.buildUrl('/adv/add-pics'), //接口地址
          header: app.getRequestHeader(),
          filePath: img_list[i - 1], //文件路径
          formData: {
            'id': id
          },
          name: 'file', //文件名，不要修改，Flask直接读取
          success: function(res) {
            // var resp = res.data;
            // if (resp.code !== 200) {
            //     app.alert({'content': resp.msg});
            //     return;
            // }
            if (end_s) {
              that.endCreate(id);
            }
          },
          fail: function(res) {
            app.serverBusy();
            return;
          },
          complete: function(res) {},
        })
      }
    }
  },
  endCreate: function(id) {
    var that = this;
    that.setData({
      flush: false
    });
    wx.request({
      url: app.buildUrl("/adv/end-create"),
      method: 'POST',
      header: app.getRequestHeader(),
      data: {
        id: id
      },
      success: function(res) {
        var resp = res.data;
        if (resp.code !== 200) {
          app.alert({
            'content': resp.msg
          });
          return
        }
        that.setData({
          change_qrcode: false,
        });
        that.setInitData();
        wx.showToast({
          title: '提交成功',
          icon: 'success',
          duration: 2000
        });
        wx.switchTab({
          url: '../../goods/index',
        });
      },
      fail: function(res) {
        app.serverBusy();
        return;
      },
      complete: function(res) {
        that.setData({
          loadingHidden: true
        });
      },
    });
  },
  //设置页面参数
  setInitData: function() {
    var summary_placeholder = "添加广告描述";
    var imglist = [];
    var tips_obj = {
      "goods_name": "广告名称",
      "target_price": "价格",
      "location": "地址",
      "stock": "库存",
      "summary": "描述",
    };
    var items = [{
        name: "goods_name",
        placeholder: "例:相机",
        label: "广告名称",
        icons: "/images/icons/goods_name.png",
      },
      {
        name: "target_price",
        placeholder: "例:0.00",
        label: "价格",
        icons: "/images/icons/discount_price.png",
        kb_type: "digit",
      },
      {
        name: "stock",
        placeholder: "1",
        value: 1,
        label: "库存",
        kb_type: "number",
        icons: "/images/icons/stock.png",
      },
      {
        name: "location",
        placeholder: "例:同济大学四平校区",
        label: "地址",
        value: location,
        icons: "/images/icons/location.png",
      }
    ];
    var summary_value = "";
    this.setData({
      imglist: imglist,
      count: imglist.length,
      pic_status: true,
      loadingHidden: true,
      items: items,
      summary_placeholder: summary_placeholder,
      show_qr_code: true,
      summary_value: summary_value,
      tips_obj: tips_obj,
    })
  },
  //预览二维码
  previewQrCodeImage: function(e) {
    var current = e.target.dataset.src;
    var qr_code_list = this.data.qr_code_list;
    this.setData({
      flush: false,
    });
    wx.previewImage({
      current: current, // 当前显示图片的http链接
      urls: qr_code_list, // 需要预览的图片http链接列表
    })
  },
  //选择二维码方法
  chooseQrcode: function(e) {
    var that = this; //获取上下文
    //选择图片
    var qr_code_list = this.data.qr_code_list;
    if (qr_code_list.length > 0) {
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
          var qr_code_list = [];
          qr_code_list.push(tempFiles[0].path);
          console.log(tempFiles[0].path);
          console.log(qr_code_list[0]);
          //显示
          that.setData({
            qr_code_list: qr_code_list,
            show_qr_code: true,
            change_qrcode: true,
            flush: false
          });
        }
      })
    }
  },
  // 删除二维码
  deleteQrcode: function(e) {
    this.setData({
      qr_code_list: [],
      show_qr_code: false,
      flush: false
    });
  },
});