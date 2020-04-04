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
      filter_address: '',  // 搜索栏的地址
      business_type: business_type,
      categories: categories,  // 类别
      goods_name: '',  // 物品名
      owner_name: '',  // 物主名
      filter_address: '',  // 搜索栏的地址关键词
      loadingMoreHidden: true,  // 更多数据未加载
      goods_category: ['全部'].concat(app.globalData.goodsCategories), // 分类栏数据
      filter_good_category: 0, // 默认是全部类型的物品
      open: false //侧边栏折叠
    })
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
  /**
   * catClick 如果切换了状态栏，就加载新的数据
   * @param e
   */
  catClick: function (e) {
    //选择一次分类时返回选中值
    let old_status = this.data.activeCategoryId
    let new_status = e.currentTarget.id
    this.setData({
      activeCategoryId: new_status,
    })
    if (old_status != new_status) {
      this.onPullDownRefresh()
    }
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
    let that = this;
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
    //延时500ms处理函数
    setTimeout( () => {
      this.setData({
        loadingHidden: true
      })
      this.getGoodsList();
    }, 500)
  },
  listenerNameInput: function (e) {
    this.setData({
      owner_name: e.detail.value
    })
  },
  listenerGoodsNameInput: function (e) {
    this.setData({
      goods_name: e.detail.value
    })
  },
  listenerAddressInput: function (e) {
    this.setData({
      filter_address: e.detail.value
    });
  },
  formSubmit: function (e) {
    let data = e.detail.value
    this.setData({
      owner_name: data['owner_name'],
      goods_name: data['goods_name'],
      filter_address: data['filter_address']
    })
    this.onPullDownRefresh();
  },
  //获取信息列表
  getGoodsList: function (e) {
    let that = this
    if (!that.data.loadingMoreHidden || that.data.processing) {
      return
    }
    that.setData({
      processing: true,
      loadingHidden: false
    })
    wx.request({
      url: app.buildUrl("/goods/search"),
      data: {
        status: that.data.activeCategoryId,
        mix_kw: that.data.goods_name,
        owner_name: that.data.owner_name,
        p: that.data.p,
        business_type: that.data.business_type,
        filter_address: that.data.filter_address,
        filter_good_category: this.data.filter_good_category,
      },
      success: function (res) {
        let resp = res.data;
        if (resp['code'] !== 200) {
          app.alert({content: resp['msg']})
          return
        }
        let goods_list = resp['data'].list
        goods_list = app.cutStr(goods_list) //概要，切去各个字符串属性过长的部分
        that.setData({
          goods_list: that.data.goods_list.concat(goods_list),
          p: that.data.p + 1,
        })
        if (resp.data.has_more === 0) {
          that.setData({
            loadingMoreHidden: false,
          })
        }
      },
      fail: function (res) {
        app.serverBusy()
      },
      complete: function (res) {
        that.setData({
          processing: false,
          loadingHidden: true
        })
      },
    })
  },
  //点击预览图片
  previewImage: function (e) {
    wx.previewImage({
      current: this.data.banners[e.currentTarget.dataset.index], // 当前显示图片的http链接
      urls: [this.data.banners[e.currentTarget.dataset.index]] // 需要预览的图片http链接列表
    })
  },
  /**
   * tapDrag 手指拖动中，记录新x坐标
   * @param e
   */
  tapDrag: function(e){
    this.data.newmark = e.touches[0].pageX;
  },
  /**
   * tapEnd 手指拖动结束
   */
  tapEnd: function(){
    if(this.data.mark + app.globalData.windowWidth * 0.4 < this.data.newmark){
      this.setData({
        open : true
      });
    }else{
      this.setData({
        open : false
      });
    }
    this.data.mark = 0;
    this.data.newmark = 0;
  },
  /**
   * tapStart 手指开始拖动
   * @param e
   */
  tapStart:function(e){
    console.log(e)
    this.data.mark = this.data.newmark = e.touches[0].pageX;
  },
  /**
   * selectGoodsCat 切换物品类别时重新加载数据
   * @param e
   */
  selectGoodsCat: function (e) {
    let name = e.currentTarget.dataset.name
    let old_cat = this.data.filter_good_category
    let new_cat = this.data.goods_category.indexOf(name)
    this.setData({
      open: false,
      filter_good_category: new_cat
    })
    if (old_cat != new_cat) {
      //换了新的类别
      this.onPullDownRefresh()
    }
  },
})