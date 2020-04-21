//index.js
//获取应用实例
var app = getApp();

Page({
  data: {
    autoplay: true,
    interval: 3000,
    duration: 1000,
  },
  onLoad: function (options) {
    var adv_id =options.id;
    var that = this;
    that.setData({
      show_qr_code: true,
    });
    this.getAdvsInfo(adv_id);
  },
  onShow: function () {
    var regFlag = app.globalData.regFlag;
    this.setData({
      regFlag: regFlag
    });

  },
  getAdvsInfo: function (id) {
    var that = this;
    that.setData({
      loadingHidden: false
    });
    wx.request({
      url: app.buildUrl("/adv/info"),
      header: app.getRequestHeader(),
      data: {
        id: id,
      },
      success: function (res) {
        var resp = res.data;
        if (resp.code !== 200) {
          app.alert({
            'content': resp.msg
          });
          return;
        }
        var info = resp.data.info;
        info['is_adm'] = app.globalData.is_adm;
        that.setData({
          info:info
        });
      },
      fail: function (res) {
        app.serverBusy();
        return;
      },
      complete: function (res) {
        that.setData({
          loadingHidden: true
        });
      },
    })
  },
  //事件处理函数
  goHome: function (e) {
    wx.switchTab({
      url: "../../goods/index",
    })
  },
  goRelease: function (e) {
    wx.switchTab({
      url: '../../my/connect/index',
    })
  },
  showQrCode: function () {
    var regFlag = app.globalData.regFlag;
    if (regFlag) {
      var show_qr_code = !this.data.show_qr_code;
      this.setData({
        show_qr_code: show_qr_code
      })
    } else {
      app.loginTip();
    }
  },
  //预览图片
  previewImage: function (e) {
    var current = e.target.dataset.src;
    wx.previewImage({
      current: current, // 当前显示图片的http链接
      urls: this.data.info.qr_code_list,
    })
  },
  previewItemImage: function (e) {
    var index = e.currentTarget.dataset.index;
    wx.previewImage({
      current: this.data.info.pics[index], // 当前显示图片的http链接
      urls: this.data.info.pics // 需要预览的图片http链接列表
    })
  },
  toDelete: function (e) {
    //选择操作的用户id
    var that = this;
    var adv_id = this.data.info.id;
    wx.showModal({
      title: '操作提示',
      content: '确认删除？',
      success: function (res) {
        wx.request({
          url: app.buildUrl("/adv/delete"),
          header: app.getRequestHeader(),
          data: {
            id: adv_id,
          },
          success: function (res) {
            wx.hideLoading();
            wx.showToast({
              title: '删除广告成功！',
              icon: 'success',
              duration: 2000
            });
            wx.switchTab({
              url: '../../goods/index',
            })
          },
          fail: function (res) {
            wx.hideLoading();
            wx.showToast({
              title: '系统繁忙，拉黑失败！',
              duration: 2000
            });
          }
        });
      }
    });
  },
});