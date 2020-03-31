const navigate = require("../template/navigate-bar/navigate-bar-template.js")
const util = require("../../utils/util.js");
const app = getApp();
Page({
  data: {
    banners: ["/images/logo.jpg"],
    activeCategoryId: -1,
    categories: [{
      id: -1,
      name: '全部',
    },
    {
      id: 0,
      name: '待认领'
    },
    {
      id: 1,
      name: '预认领'
    },
    {
      id: 2,
      name: '已认领'
    },
    ],
  },
  onLoad: function (options) {
    //如果没有页面参数，则默认跳转失物招领页面
    var business_type = options.business_type ? options.business_type : 1;
    if (business_type == 1) {
      var categories = [{
        id: -1,
        name: '全部',
      },
      {
        id: 1,
        name: '待认领'
      },
      {
        id: 2,
        name: '预认领'
      },
      {
        id: 3,
        name: '已认领'
      },
      ]
    } else {
      wx.setNavigationBarTitle({
        title: '寻物启事',
      })

      var categories = [{
        id: -1,
        name: '全部',
      },
      {
        id: 1,
        name: '待寻回'
      },
      {
        id: 2,
        name: '预寻回'
      },
      {
        id: 3,
        name: '已寻回'
      },
      ]
    };
    this.setData({
      filter_address: '',
      business_type: business_type,
      categories: categories,
      goods_name: '',
      owner_name: '',
      filter_address: '',
      loadingMoreHidden: true
    });
  },
  //轮播图变化
  swiperchange: function (e) {
    this.setData({
      swiperCurrent: e.detail.current
    })
  },
  onShow: function () {
    this.setData({
      regFlag: app.globalData.regFlag
    })
    this.setInitData()
    this.onPullDownRefresh()
  },
  catClick: function (e) {
    //选择一次分类时返回选中值
    this.setData({
      activeCategoryId: e.currentTarget.id,
    })
    this.onPullDownRefresh()
  },
  //点击信息卡查看详情
  onDetailTap: function (event) {
    let id = event.currentTarget.dataset.id
    app.globalData.op_status = 2
    wx.navigateTo({
      url: 'info/info?goods_id=' + id,
    })
  },
  //刷新
  onPullDownRefresh: function (event) {
    this.setData({
      p: 1,
      goods_list: [],
      loadingMoreHidden: true
    });
    this.getGoodsList();
  },
  //点击导航图标
  onNavigateTap: function (event) {
    navigate.onNavigateTap(event, this)
  },
  onShareAppMessage: function (Options) {
    return {
      title: '我在【闪寻-失物招领】找东西，你也快来看看吧~',
      path: '/pages/index/index',
      success: function (res) {
        wx.request({
          url: app.buildUrl('/member/share'),
          success: function (res) {
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
          fail: function (res) {
            app.serverBusy();
            return;
          }
        })
      }
    }
  },
  scroll: function (e) {
    var that = this,
      scrollTop = that.data.scrollTop;
    that.setData({
      scrollTop: e.detail.scrollTop
    });
  },
  //查看导航栏信息
  goAdvInfo: function (e) {
    var adv_id = e.currentTarget.dataset.id;
    console.log(adv_id);
    wx.navigateTo({
      url: '../adv/info/adv-info?id=' + adv_id,
    })
  },
  //举报按钮
  toReport: function (e) {
    var regFlag = app.globalData.regFlag;
    if (!regFlag) {
      app.loginTip();
      return;
    }
    var id = e.currentTarget.dataset.id;
    var that = this;
    wx.showModal({
      title: "违规举报",
      content: "为维护平台环境，欢迎举报色情及诈骗、恶意广告等违规信息！同时，恶意举报将会被封号，请谨慎操作，确认举报？",
      success: function (res) {
        if (res.confirm) { //点击确定,获取操作用户id以及商品id,从用户token里面获取id
          wx.showLoading({
            title: '信息提交中..'
          });
          wx.request({
            url: app.buildUrl("/goods/report"),
            header: app.getRequestHeader(),
            data: {
              id: id,
              record_type: 1,
            },
            success: function (res) {
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
            fail: function (res) {
              wx.hideLoading();
              wx.showToast({
                title: '系统繁忙，反馈失败，还是感谢！',
                duration: 2000
              });
            },
            complete: function () {
              wx.hideLoading();
              that.onPullDownRefresh();
            }
          });
        }
      }
    });
  },
  setInitData: function () {
    this.setData({
      goods_list: [],
      loadingMoreHidden: true,
      p: 1,
      activeCategoryId: this.data.activeCategoryId,
      loadingHidden: true, // loading
      swiperCurrent: 0,
      goods: [],
      scrollTop: "0",
      processing: false,
      items: [{
        name: 'owner_name',
        placeholder: '姓名',
        icons: 'search_icon',
        act: "listenerNameInput",
      },
      {
        name: "goods_name",
        placeholder: "物品",
        act: "listenerGoodsNameInput",
      },
      {
        name: "filter_address",
        placeholder: "地址",
        act: "listenerAddressInput",
      }
      ]
    });
  },
  //获取轮播图
  getBanners: function () {
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
      url: app.buildUrl("/adv/search"),
      success: function (res) {
        var resp = res.data;
        if (resp.code !== 200) {
          app.alert({
            'content': resp.msg
          });
          return
        }
        var banners = resp.data.list;
        that.setData({
          banners: banners,
        });
      },
      fail: function (res) {
        app.serverBusy();
        return;
      },
      complete: function (res) {
        that.setData({
          processing: false,
          loadingHidden: true
        });
        //获取商品信息
        that.getGoodsList();
      },
    })
  },
  onReachBottom: function (e) {
    var that = this;
    //延时500ms处理函数
    setTimeout(function () {
      that.setData({
        loadingHidden: true
      });
      that.getGoodsList();
    }, 500);
  },
  listenerNameInput: function (e) {
    this.setData({
      owner_name: e.detail.value
    });
  },
  listenerGoodsNameInput: function (e) {
    this.setData({
      goods_name: e.detail.value
    });
  },
  listenerAddressInput: function (e) {
    this.setData({
      filter_address: e.detail.value
    });
  },
  formSubmit: function (e) {
    var data = e.detail.value
    this.setData({
      owner_name: data['owner_name'],
      goods_name: data['goods_name'],
      filter_address: data['filter_address']
    })
    this.onPullDownRefresh();
  },
  //获取信息列表
  getGoodsList: function (e) {
    var that = this;
    if (!that.data.loadingMoreHidden || that.data.processing) {
      return;
    }
    that.setData({
      processing: true,
      loadingHidden: false
    });
    wx.request({
      url: app.buildUrl("/goods/search"),
      data: {
        status: that.data.activeCategoryId,
        mix_kw: that.data.goods_name,
        owner_name: that.data.owner_name,
        p: that.data.p,
        business_type: that.data.business_type,
        filter_address: that.data.filter_address
      },
      success: function (res) {
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
      fail: function (res) {
        app.serverBusy();
        return;
      },
      complete: function (res) {
        that.setData({
          processing: false,
          loadingHidden: true
        });
      },
    })
  },
  closeQrcodeHint: function (e) {
    navigate.closeQrcodeHint(this)
  },
  //点击预览图片
  previewImage: function (e) {
    wx.previewImage({
      current: this.data.infos.info.pics[e.currentTarget.dataset.index], // 当前显示图片的http链接
      urls: this.data.info.info.pics // 需要预览的图片http链接列表
    })
  },
})