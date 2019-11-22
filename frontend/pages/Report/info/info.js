//index.js
//获取应用实例
var app = getApp();

Page({
  data: {
    autoplay: true,
    interval: 3000,
    duration: 1000,
    swiperCurrent: 0,
    loadingHidden: true,

    info: {
      "auther_name": "韦朝旭",
      "avatar": "https://wx.qlogo.cn/mmopen/vi_32/Q0j4TwGTfTJLMa7CuCcoXicK6SpMA9E0IHxPgLYibKFbeCkUo3IicyyDr8ssosTEaaptIL2Xjic6LXEC2OmjwmXMmQ/132",
      "business_type": 1, //捡到东西还是丢了东西，捡到是1，丢了是0
      "goods_name": "钱包",
      "onwer_name": "韦朝旭",
      "id": 23, //发布的记录的id
      "is_auth": false, //当前用户是否是消息的发布者
      "location": "图书馆",
      "main_image": "https://jmall.opencs.cn/static/upload/20191030/81f2f83ff3ea43e797a3cf6144e9afba.jpg", //主图
      "pics": [
        "https://jmall.opencs.cn/static/upload/20191030/81f2f83ff3ea43e797a3cf6144e9afba.jpg"
      ], //组图
      "summary": "\u5168\u65b0\uff0c\u57fa\u672c\u6ca1\u5199\u5b57", //详情介绍
      "updated_time": "2019-10-30 12:20:40", //更新时间
      "view_count": 39, //浏览量
    }

  },
  onLoad: function(options) {
    var goods_id = 23;
    var info = this.data.info;
    this.setData({
      infos: {
        info: info,
        loadingHidden: true,
        op_status: 2
      }
    });
    //this.getGoodsInfo(goods_id);
  },
  getReportInfo: function(id) {
    var that = this;
    that.setData({
      loadingHidden: false
    });
    wx.request({
      url: app.buildUrl("/report/info"),
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
          return;
        }
        that.setData({
          info: resp.data.info,
          report_auth_info: resp.data.report_auth_info,
          report_id: resp.data.report_id
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
    })
  },
  //顶部导航栏点击
  swiperchange: function(e) {
    this.setData({
      swiperCurrent: e.detail.current
    })
  },
  toReport: function(e) {
    app.alert({
      'content':"已经是举报过的信息，请处理！"
    });
  },
  //预览图片
  previewImage: function(e) {
    var current = e.target.dataset.src;
    wx.previewImage({
      current: current, // 当前显示图片的http链接
      urls: this.data.info.qr_code_list,
    })
  },
  previewItemImage: function(e) {
    var index = e.currentTarget.dataset.index;
    console.log(index);
    wx.previewImage({
      current: this.data.info.pics[index], // 当前显示图片的http链接
      urls: this.data.info.pics // 需要预览的图片http链接列表
    })
  },
  //拉黑举报者
  toBlockReporter: function(e) {
    //选择操作的用户id
    var that = this;
    var select_member_id = e.currentTarget.dataset.id;
    var auth_id = this.data.info.member_id;
    var report_member_id = this.data.report_auth_info.member_id;
    var goods_id = this.data.info.id;
    var report_id = this.data.report_id;
    wx.showModal({
      title: '操作提示',
      content: '确认拉黑？',
      success: function(res) {
        wx.request({
          url: app.buildUrl("/report/block"),
          header: app.getRequestHeader(),
          data: {
            select_member_id: select_member_id,
            goods_id: goods_id,
            report_id: report_id,
            auth_id: auth_id,
            report_member_id: report_member_id
          },
          success: function(res) {
            wx.hideLoading();
            wx.showToast({
              title: '拉黑用户成功！',
              icon: 'success',
              duration: 2000
            });
            wx.switchTab({
              url: '../record/index',
            })
          },
          fail: function(res) {
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
  //拉黑发布者
  toBlockMember: function (e) {
    //选择操作的用户id
    var that = this;
    var select_member_id = e.currentTarget.dataset.id;
    var auth_id = this.data.info.member_id;
    var report_member_id = this.data.report_auth_info.member_id;
    var goods_id = this.data.info.id;
    var report_id = this.data.report_id;
    wx.showModal({
      title: '操作提示',
      content: '确认拉黑？',
      success: function (res) {
        wx.request({
          url: app.buildUrl("/report/block"),
          header: app.getRequestHeader(),
          data: {
            select_member_id: select_member_id,
            goods_id: goods_id,
            report_id: report_id,
            auth_id: auth_id,
            report_member_id: report_member_id
          },
          success: function (res) {
            wx.hideLoading();
            wx.showToast({
              title: '拉黑用户成功！',
              icon: 'success',
              duration: 2000
            });
            wx.switchTab({
              url: '../record/index',
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
  //无违规
  noRule: function(e) {
    var id = this.data.info.id;
    var report_id = this.data.report_id;
    wx.request({
      url: app.buildUrl("/report/no-rule"),
      header: app.getRequestHeader(),
      data: {
        id: id,
        report_id: report_id
      },
      success: function(res) {
        wx.hideLoading();
        wx.showToast({
          title: '解放商品成功！',
          icon: 'success',
          duration: 2000
        });
        wx.switchTab({
          url: '../record/index',
        })
      },
      fail: function(res) {
        wx.hideLoading();
        wx.showToast({
          title: '系统繁忙，解放失败！',
          duration: 2000
        });
      }
    });
  },
});