const app = getApp();
const util = require("../../utils/util.js");
const navigate = require("../template/navigate-bar/navigate-bar-template.js");
Page({
  data: {
    banners: ["/images/logo.jpg"],
    activeCategoryId: 1,
    categories: null,
    hasQrcode: false
  },
  onLoad: function (options) {
    wx.getSystemInfo({
      success:  (res) => {
        let X = res.windowWidth * 0.8;
        let Y= res.windowHeight * 0.4;
        this.setData({
          x: X,
          y: Y
        });
      }
    });
    //如果没有页面参数，则默认跳转失物招领页面
    this.onLoadSetData(options.business_type ? parseInt(options.business_type) : 1)
  },
  onLoadSetData: function (business_type = 0) {
    let categories = business_type ? [{id: 0, name: '全部'}] : [];
    let verb = business_type ? '认领' : '寻回';
    categories = categories.concat([
      {
        id: 1,
        name: '待' + verb
      },
      {
        id: 2,
        name: '预' + verb
      },
      {
        id: 3,
        name: '已' + verb
      },
      {
        id: 4,
        name: '已答谢'
      }
    ]);
    if (business_type === 0) {
      categories.splice(1,1);
    }
    wx.setNavigationBarTitle({
      title: business_type? '失物招领' : '寻物启事',
    });
    this.setData({
      member_id: app.globalData.id, //用户的ID，没有注册就是0
      business_type: business_type,
      categories: categories,  // 类别
      activeCategoryId: 1-business_type, // 失物招领是0全部，拾物是1
      goods_name: '',  // 物品名
      owner_name: '',  // 物主名
      filter_address: '',  // 搜索栏的地址关键词
      loadingMore: true,  // 更多数据未加载
      hasQrcode: app.globalData.has_qrcode // 二维码
    });
  },
  //轮播图变化
  swiperchange: function (e) {
    this.setData({
      swiperCurrent: e.detail.current
    })
  },
  /**
   * onShow 页面显示初始化数据，加载第一页物品
   */
  onShow: function () {
    //加载第一页的物品数据
    this.setNavigationBar();
    this.setInitData();
    this.onPullDownRefresh();
  },
  setNavigationBar: function () {
    let [isSelecteds, urls] = util.onNavigateTap(this.data.business_type? 1: 3);  //不传值代表没有页被选中
    isSelecteds['showHintQrcode'] = app.globalData.showHintQrcode;  //用户有没有关闭
    isSelecteds['regFlag'] = app.globalData.regFlag;  //用户注册
    this.setData({
      isSelecteds: isSelecteds
    });
  },
  /**
   * catClick 如果切换了状态栏，就加载新的数据
   * @param e
   */
  catClick: function (e) {
    //选择一次分类时返回选中值
    let old_status = this.data.activeCategoryId;
    let new_status = e.currentTarget.id;
    this.setData({
      activeCategoryId: new_status,
    });
    if (old_status !== new_status) {
      //状态如若发生变化就像后端请求新数据,依赖 activeCategoryId，必须先设置再请求
      this.onPullDownRefresh()
    }
  },
  /**
   * onDetailTap 点击信息卡查看详情
   * @param e
   */
  onDetailTap: function (e) {
    wx.navigateTo({
      url: 'info/info?goods_id=' + e.currentTarget.dataset.id
    })
  },
  /**
   * 获取第一页物品数据
   */
  onPullDownRefresh: function () {
    this.setData({
      p: 1,
      goods_list: [],
      loadingMore: true
    });
    this.getGoodsList();
  },
  /**
   * 分享页面进入首页，加分
   * @param Options
   * @returns {{path: string, success: success, title: string}}
   */
  onShareAppMessage: function (Options) {
    return {
      title: '我在【鲟回-失物招领】找东西，你也快来看看吧~',
      path: '/pages/index/index',
      success:  (res) => {
        wx.request({
          url: app.buildUrl('/member/share'),
          success:  (res) => {
            let resp = res.data;
            if (resp['code'] !== 200) {
              app.alert({
                content: resp['msg']
              });
              return;
            }
            wx.showToast({
              title: '分享成功！',
              icon: 'success',
              content: '积分+5',
              duration: 1000
            })
          },
          fail:  (res) => {
            app.serverBusy();
          }
        })
      }
    }
  },
  scroll: function (e) {
    this.setData({
      scrollTop: e.detail.scrollTop
    })
  },
  /**
   * 查看轮播广告
   * @param e
   */
  goAdvInfo: function (e) {
    let adv_id = e.currentTarget.dataset.id;
    wx.navigateTo({
      url: '../adv/info/adv-info?id=' + adv_id
    })
  },
  /**
   * 实际举报物品
   * @param e
   */
  toReport: function (e) {
    if (!app.loginTip()) {
      return;
    }
    app.alert({
      title: "违规举报",
      content: "为维护平台环境，欢迎举报恶搞、诈骗、私人广告、色情等违规信息！同时，恶意举报将会被封号，请谨慎操作，确认举报？",
      showCancel: true,
      cb_confirm: () => {
        this.doReportGoods(e.currentTarget.dataset.id, e.currentTarget.dataset.status)
      }
    });
  },
  /**
   * 举报物品
   * @param id
   * @param goods_status
   */
  doReportGoods: function (id = -1, goods_status=0) {
    wx.showLoading({
      title: '信息提交中..'
    });
    let status = this.data.activeCategoryId;
    wx.request({
      url: app.buildUrl("/report/goods"),
      header: app.getRequestHeader(),
      data: {
        id: id,
        status: status? status: goods_status   //操作冲突检测，以及全部标签卡进行兼容
      },
      success: function (res) {
        let resp = res.data;
        if (resp['code'] !== 200) {
          app.alert({
            content: resp['msg']
          });
          return
        }
        wx.showToast({
          title: '举报成功，感谢！',
          icon: 'success',
          duration: 1000,
          success: (res) => {
            this.onPullDownRefresh()
          }
        });
      },
      fail: function (res) {
        app.serverBusy()
      },
      complete: (res) => {
        wx.hideLoading();
      }
    });
  },
  /**
   * setInitData 页面各个组件(搜索栏，状态栏，轮播图，帖子列表)的数据初始化
   */
  setInitData: function () {
    this.setData({
      goods_list: [],
      loadingMore: true,
      p: 1,
      activeCategoryId: this.data.activeCategoryId,  //选中的状态
      loadingHidden: true, // 加载图标
      swiperCurrent: 0,  //轮播图图片下标
      scrollTop: "0",
      processing: false,  //加载数据
      items: [{  //搜索输入表单
        name: 'owner_name',
        placeholder: '物主姓名',
        icons: 'search_icon',
        show_clean: false,
        value: '',
        is_focus: false
      },
        {
          name: "goods_name",
          placeholder: "物品名称",
          show_clean: false,
          value: '',
          is_focus: false
        },
        {
          name: "filter_address",
          placeholder: "遗失地址",
          show_clean: false,
          value: '',
          is_focus: false
        }
      ]
    })
  },
  //获取轮播图
  getBanners: function () {
    let that = this;
    if (!that.data.loadingMore) {
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
        let resp = res.data;
        if (resp['code'] !== 200) {
          app.alert({
            content: resp['msg']
          });
          return
        }
        that.setData({
          banners: resp['data'].list,
        });
      },
      fail: function (res) {
        app.serverBusy();
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
      });
      this.getGoodsList();
    }, 500)
  },
  searchBoxInput: function(e) {
    let idx = e.currentTarget.dataset.id;
    let items = this.data.items;
    items[idx].value = e.detail.value;
    this.setData({
      change: true,
      items: items
    });
  },
  searchBoxFocus: function(e) {
    let idx = e.currentTarget.dataset.id;
    let items = this.data.items;
    items[idx].is_focus = true;
    this.setData({
      items: items
    })
  },
  searchBoxBlur: function(e) {
    let idx = e.currentTarget.dataset.id;
    let items = this.data.items;
    items[idx].show_clean = items[idx].value.length > 0;
    items[idx].is_focus = false;
    this.setData({
      items: items
    });
    this.search();
  },
  searchBoxClean: function(e){
    let idx = e.currentTarget.dataset.id;
    let items = this.data.items;
    items[idx].show_clean = false;
    items[idx].value = '';
    this.setData({
      change: true,
      items: items
    });
    this.search();
  },
  search: function () {
    if (this.data.change) {
      this.onPullDownRefresh();
      this.setData({
        change: false
      })
    }
  },
  //获取信息列表
  getGoodsList: function (e) {
    if (!this.data.loadingMore || this.data.processing) {
      return
    }
    this.setData({
      processing: true,
      loadingHidden: false
    });
    let items = this.data.items;
    wx.request({
      url: app.buildUrl("/goods/search"),
      data: {
        status: this.data.activeCategoryId,
        mix_kw: items[1].value,
        owner_name: items[0].value,
        p: this.data.p,
        business_type: this.data.business_type,
        filter_address: items[2].value
      },
      success:  (res) => {
        let resp = res.data;
        if (resp['code'] !== 200) {
          app.alert({content: resp['msg']});
          return;
        }
        let data = resp['data'];
        let goods_list = data['list'];
        goods_list = app.cutStr(goods_list); //概要，切去各个字符串属性过长的部分
        this.setData({
          goods_list: this.data.goods_list.concat(goods_list),
          p: this.data.p + 1,
          loadingMore: data['has_more']
        })
      },
      fail:  (res) => {
        app.serverBusy()
      },
      complete:  (res) => {
        this.setData({
          processing: false,
          loadingHidden: true,
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
   * onPageScroll 目的：当页面滚动距离超过状态栏距离顶部的距离时，让状态栏吸附在顶部
   * @param e
   */
  onPageScroll(e) {
    // 页面滚动的距离 > 类别栏元素距离顶部的高度，让其吸附在搜索栏下方
    this.setData({
      tabFixed: e.scrollTop > this.data.aboveHeight
    })
  },
  /**
   * onReady 目的：获取状态栏距离顶部的距离，使状态栏能在下拉后仍然吸附在顶部
   */
  onReady() {
    const query = wx.createSelectorQuery();
    // 这里：获取轮播图的height 就是 状态切换栏的top(顶部坐标)
    query.select(".swiper-container").boundingClientRect((res) => {
      if (res) {
        this.setData({
          aboveHeight: res.height
        })
      }
    }).exec()
  },
  /**
   * businessTypeClick 点击浮球页面类别(wx.redirec)
   */
  businessTypeClick: function (e) {
    //刷新页面数据
    this.onLoadSetData(1-this.data.business_type)
    this.onShow()
  },
  //点击导航
  onNavigateTap: function (event) {
    let [isSelecteds, urls] = util.onNavigateTap( event.currentTarget.dataset.id * 1);
    this.setData({
      isSelecteds: isSelecteds
    })
    navigate.onNavigateTap(event, this)
  },
  tapOnHint: function (e) {
    navigate.tapOnHint(this)
  },
  closeQrcodeHint: function (e) {
    navigate.closeQrcodeHint(this)
  },
  toSeeQrcode: function () {
    navigate.toSeeQrcode(this)
  },
  toGetQrcode: function () {
    navigate.toGetQrcode(this)
  },
  toLogin: function () {
    navigate.toLogin(this)
  }
});

