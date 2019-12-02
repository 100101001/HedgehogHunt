var app = getApp();
Page({
  data: {
    loadingHidden: true,
  },
  onLoad: function(options) {
    var info = app.globalData.info;
    this.onLoadSetData(info);
  },
  onShow: function() {},
  onLoadSetData: function(info) {
    var business_type = info.business_type;
    var imglist = info.pics;
    if (business_type == 1) {
      var summary_placeholder = "添加物品描述：拾到物品的时间、地点以及物品上面的其他特征如颜色、记号等...";
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
          value: info.goods_name,
          label: "物品名称",
          icons: "/images/icons/goods_name.png",
        },
        {
          name: "owner_name",
          placeholder: "例:可可",
          label: "失主姓名",
          icons: "/images/icons/discount_price.png",
          value: info.owner_name,
        },
        {
          name: "location",
          placeholder: "例:同济大学四平校区南楼301",
          label: "放置位置",
          value: info.location,
          icons: "/images/icons/location.png",
        },
        {
          name: "mobile",
          placeholder: "高危非必填",
          value: info.mobile,
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
          value: info.goods_name,
          label: "物品名称",
          icons: "/images/icons/goods_name.png",
        },
        {
          name: "owner_name",
          placeholder: "例:可可",
          value: info.owner_name,
          label: "姓名",
          icons: "/images/icons/discount_price.png",
        },
        {
          name: "location",
          placeholder: "例:同济大学四平校区西北三",
          label: "住址",
          value: info.location,
          icons: "/images/icons/location.png",
        },
        {
          name: "mobile",
          placeholder: "高危非必填",
          label: "联系电话",
          value: info.mobile,
          icons: "/images/icons/goods_type.png",
        }
      ];
      var summary_placeholder = "添加寻物描述：物品丢失大致时间、地点，记号等...";
    }
    var summary_value = info.summary;
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
      goods_id: info.id,
    })
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
          imglist: imglist
        })
      }
    })
  },
  // 删除图片
  deleteImg: function(e) {
    var index = e.currentTarget.dataset.index;
    var imglist = this.data.imglist;
    if (imglist.length === 1) {
      app.alert({
        'content': "删除失败，至少要提交一张图片"
      });
    } else {
      imglist.splice(index, 1);
      that.setData({
        imglist: imglist
      })
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
    var img_list = this.data.imglist;
    if (img_list.length === 0) {
      app.alert({
        'content': "至少要提交一张图片"
      });
      return;
    }
    data['img_list'] = img_list;
    var url = "/goods/edit";
    data['id'] = this.data.goods_id;
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
        app.globalData.info={};
        wx.showToast({
          title: '提交成功',
          icon: 'success',
          duration: 2000
        });
        wx.navigateTo({
          url: '../../Find/Find',
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
});