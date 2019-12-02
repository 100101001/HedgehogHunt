//index.js
//获取应用实例
var app = getApp();
Page({
  data: {},
  onLoad: function() {
    var business_type = app.globalData.business_type;
    if (business_type == 1) {
      var radio_checked = true;
    } else {
      var radio_checked = false;
    }
    var cat_ori = [{
      id: -1,
      name: '全部'
    }];
    var cat_all = app.globalData.objectArray;
    var cats = cat_ori.concat(cat_all);
    wx.setNavigationBarTitle({
      title: app.globalData.shopName
    });
    this.setData({
      filter_address: '',
      business_type: business_type,
      radio_checked: radio_checked,
      filter_btn_tap: false,
      categories: cats,
      goods_list: [],
      banners: ["/images/more/Tips.png", "/images/more/OpenCS.png"],

    });
  },
  onShow: function() {
    var regFlag = app.globalData.regFlag;
    this.setData({
      regFlag: regFlag
    });
    this.setInitData();
    this.getGoodsList();
  },
  login: function(e) {
    app.login(e);
    var regFlag = app.globalData.regFlag;
    this.setData({
      regFlag: regFlag
    });
  },
  onShareAppMessage: function(Options) {
    return {
      title: '我在济人济市交易闲置，你也快来看看吧~',
      path: '/pages/jmall/index/index',
      success: function(res) {
        wx.request({
          url: app.buildUrl('/member/share'),
          success: function(res) {
            var resp = res.data;
            if (resp.code != 200) {
              app.alert({
                'content': resp.msg
              });
              return;
            }
            wx.showToast({
              title: '分享成功！',
              icon: 'success',
              content: '积分+5',
              duration: 3000
            })
          },
          fail: function(res) {
            app.serverBusy();
            return;
          }
        })
      }
    }
  },
  scroll: function(e) {
    var that = this,
      scrollTop = that.data.scrollTop;
    that.setData({
      scrollTop: e.detail.scrollTop
    });
  },
  //事件处理函数
  swiperchange: function(e) {
    this.setData({
      swiperCurrent: e.detail.current
    })
  },
  listenerSearchInput: function(e) {
    this.setData({
      searchInput: e.detail.value
    });
  },
  listenerLocationInput: function(e) {
    this.setData({
      filter_address: e.detail.value
    });
  },
  toSearch: function(e) {
    this.setData({
      p: 1,
      goods_list: [],
      loadingMoreHidden: true
    });
    this.getGoodsList();
  },
  previewImage: function(e) {
    var index = e.currentTarget.dataset.index;
    console.log(index);
    wx.previewImage({
      current: this.data.banners[index], // 当前显示图片的http链接
      urls: this.data.banners // 需要预览的图片http链接列表
    })
  },
  toDetailsTap: function(e) {
    var check_report = app.globalData.check_report;
    if (check_report) {
      wx.showModal({
        title: '操作提示',
        content: '检查举报模式下不能正常浏览，请先退出该模式'
      })
    } else {
      var goods_id = e.currentTarget.dataset.id;
      wx.navigateTo({
        url: "../goods/info?goods_id=" + goods_id
      });
    }
  },
  //举报按钮
  toReport: function(e) {
    var regFlag = app.globalData.regFlag;
    if (!regFlag) {
      app.alert({
        "content": "没有授权登录，不能举报！请授权登录"
      });
      return;
    }
    var id = e.currentTarget.dataset.id;
    var that = this;
    wx.showModal({
      title: "违规举报",
      content: "为维护平台环境，欢迎举报色情及诈骗、恶意广告等违规信息！同时，恶意举报将会被封号，请谨慎操作，确认举报？",
      success: function(res) {
        if (res.confirm) { //点击确定,获取操作用户id以及商品id,从用户token里面获取id
          wx.showLoading({
            title: '信息提交中..'
          });
          wx.request({
            url: app.buildUrl("/goods/report"),
            header: app.getRequestHeader(),
            data: {
              id: id
            },
            success: function(res) {
              var resp = res.data;
              if (resp.code != 200) {
                app.alert({
                  'content': resp.msg
                });
                return
              }
              wx.hideLoading();
              wx.showToast({
                title: '举报成功，感谢！',
                icon: 'success',
                duration: 2000
              });
            },
            fail: function(res) {
              wx.hideLoading();
              wx.showToast({
                title: '系统繁忙，反馈失败，还是感谢！',
                duration: 2000
              });
            },
            complete: function() {
              wx.hideLoading();
            }
          });
          that.setData({
            p: 1,
            goods_list: [],
            loadingMoreHidden: true
          });
          that.getGoodsList();
        }
      }
    });
  },
  setInitData: function() {
    this.setData({
      goods_list: [],
      loadingMoreHidden: true,
      p: 1,
      activeCategoryId: -1,
      indicatorDots: true,
      filter_btn_tap: false,
      autoplay: true,
      interval: 3000,
      duration: 1000,
      loadingHidden: true, // loading
      swiperCurrent: 0,
      goods: [],
      scrollTop: "0",
      searchInput: '',
      processing: false
    });
  },
  //筛选按钮的点击事件
  filterBtnTap: function() {
    var filter_btn_tap = !this.data.filter_btn_tap;
    this.setData({
      filter_btn_tap: filter_btn_tap
    })
  },
  //改变单选框的选择
  radioChange: function(e) {

    var radio_checked = this.data.radio_checked;
    if (radio_checked) {
      var business_type = 0;
      console.log(business_type);
    } else {
      var business_type = 1;
    }
    this.setData({
      radio_checked: !radio_checked,
      business_type: business_type,
      p: 1,
      goods_list: [],
      loadingMoreHidden: true
    });
    this.getGoodsList();
  },
  //直接从food/index.js中拷贝过来的文件
  getBannerAndCat: function() {},
  catClick: function(e) {
    //选择一次分类时返回选中值
    this.setData({
      activeCategoryId: e.currentTarget.id,
      p: 1,
      goods_list: [],
      loadingMoreHidden: true
    });
    this.getGoodsList();
  },
  onReachBottom: function(e) {
    var that = this;
    //延时500ms处理函数

    setTimeout(function() {
      that.setData({
        loadingHidden: true
      });
      that.getGoodsList();
    }, 500);
  },
  getGoodsList: function(e) {
    var that = this;
    if (!that.data.loadingMoreHidden) {
      return;
    }

    if (that.data.processing) {
      return;
    }
    that.setData({
      processing: true,
      loadingHidden: false
    });
    wx.request({
      url: app.buildUrl("/goods/search"),
      header: app.getRequestHeader(),
      data: {
        cat_id: that.data.activeCategoryId,
        mix_kw: that.data.searchInput,
        p: that.data.p,
        business_type: that.data.business_type,
        filter_address: that.data.filter_address
      },
      success: function(res) {
        var resp = res.data;
        if (resp.code !== 200) {
          app.alert({
            'content': resp.msg
          });
          return
        }
        var goods_list = resp.data.list;
        goods_list = app.cutStr(goods_list);
        that.setData({
          goods_list: that.data.goods_list.concat(goods_list),
          p: that.data.p + 1,
        });
        if (resp.data.has_more === 0) {
          that.setData({
            loadingMoreHidden: false,
          })
        }
      },
      fail: function(res) {
        app.serverBusy();
        return;
      },
      complete: function(res) {
        that.setData({
          processing: false,
          loadingHidden: true
        });
      },
    })
  },
});