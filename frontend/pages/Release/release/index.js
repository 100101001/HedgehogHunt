var app = getApp();
Page({
  data: {
    loadingHidden: true,
    imglist: [],
  },
  onLoad: function(options) {
    var auther_id=options.auther_id;
    if (auther_id){
      var business_type=1;
      this.setData({
        auther_id:auther_idb 
      })
    }else{
      var business_type = options.business_type;
    }
    this.setData({
      business_type: business_type,
      location: ""
    });
    this.setInitData();
  },
  onShow: function() {

  },
  //获取位置的方法
  getLocation: function(e) {
    var that = this;
    wx.chooseLocation({
      success: function(res) {
        var location = [
          res.address,
          res.name,
          res.latitude,
          res.longitude,
        ]
        that.setData({
          location: location
        })
      },
    })
  },
  //获取位置
  lisentLocationInput: function(e) {
    var location = this.data.location;
    location[1] = e.detail.value;
    this.setData({
      location: location
    });
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
    var tips_obj = this.data.tips_obj;
    var is_empty = app.judgeEmpty(data, tips_obj);
    if (is_empty) {
      return;
    }
    var business_type = this.data.business_type;
    data['business_type'] = business_type;
    data['location'] = this.data.location;
    var img_list = this.data.imglist;
    if (img_list.length === 0) {
      app.alert({
        'content': "至少要提交一张图片"
      });
      return;
    }
    data['img_list'] = img_list;
    var url = "/goods/create";
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
        that.uploadImage(id, img_list, img_list_status);
      },
      fail: function(res) {
        app.serverBusy();
        return;
      },
      complete: function(res) {

      },
    });
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
          url: app.buildUrl('/goods/update-pics'),
          method: 'POST',
          header: app.getRequestHeader(),
          data: {
            id: id,
            img_url: img_list[i - 1]
          },
          success: function(res) {
            // var resp = res.data;
            // if (resp.code != 200) {
            //   app.alert({
            //     'content': resp.msg
            //   });
            //   return;
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
      } else {
        //图片不存在存在，则重新上传
        wx.uploadFile({
          url: app.buildUrl('/goods/add-pics'), //接口地址
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
    wx.request({
      url: app.buildUrl("/goods/end-create"),
      method: 'POST',
      header: app.getRequestHeader(),
      data: {
        id: id
      },
      success: function(res) {
        console.log('success');
        var resp = res.data;
        if (resp.code !== 200) {
          app.alert({
            'content': resp.msg
          });
          return
        }
        that.setInitData();
        wx.showToast({
          title: '提交成功',
          icon: 'success',
          duration: 2000
        });
        var business_type=that.data.business_type;
        wx.navigateTo({
          url: '../../Find/Find?business_type='+business_type,
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
    var location = app.globalData.location; //用于让别人帮忙寄回物品
    var business_type = this.data.business_type;
    if (business_type == 1) {
      var summary_placeholder = "添加物品描述：拾到物品的时间、地点以及物品上面的其他特征如颜色、记号等...";
      var imglist = [];
      var tips_obj = {
        "goods_name": "物品",
        "owner_name": "失主姓名",
        "location": "物品放置位置",
        "summary": "描述",
        "mobile": "联系电话",
      };
      var items = [{
          name: "goods_name",
          placeholder: "例:校园卡",
          label: "物品名称",
          icons: "/images/icons/goods_name.png",
        },
        {
          name: "owner_name",
          placeholder: "例:可可",
          label: "失主姓名",
          icons: "/images/icons/discount_price.png",
          value: "未知",
        },
        {
          name: "mobile",
          placeholder: "高危非必填",
          value: "无",
          label: "联系电话",
          icons: "/images/icons/goods_type.png",
        }
      ];
    } else {
      var tips_obj = {
        "goods_name": "物品",
        "owner_name": "失主姓名",
        "owener_location": "居住地址",
        "summary": "描述",
        "mobile": "联系电话",
      };
      var items = [{
          name: "goods_name",
          placeholder: "例:校园卡",
          label: "物品名称",
          icons: "/images/icons/goods_name.png",
        },
        {
          name: "owner_name",
          placeholder: "例:可可",
          label: "姓名",
          icons: "/images/icons/discount_price.png",
        },
        {
          name: "mobile",
          placeholder: "高危非必填",
          label: "联系电话",
          value: "高危非必填",
          icons: "/images/icons/goods_type.png",
        },
      ];
      var summary_placeholder = "添加寻物描述：物品丢失大致时间、地点，记号等...";
      var imglist = ['/images/icons/wanted.png'];
    }
    var summary_value = "";
    this.setData({
      imglist: imglist,
      count: imglist.length,
      pic_status: true,
      loadingHidden: true,
      business_type: business_type,
      items: items,
      summary_placeholder: summary_placeholder,
      summary_value: summary_value,
      tips_obj: tips_obj,
    })
  },
});