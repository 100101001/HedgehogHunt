const navigate = require("template/navigate-bar1/navigate-bar1-template.js");
const utils = require('../utils/util.js');
const app = getApp();

Page({
  data: {
    indicatorDots: true,
    autoplay: true,
    interval: 3000,
    duration: 1000,
    loadingHidden: false, // loading
    swiperCurrent: 0,
    categories: [],
    activeCategoryId: 0,
    goods: [],
    scrollTop: "0",
    loadingMoreHidden: true,
    searchInput: '',
    p: 1,
    processing: false,
    items: [
      {  //搜索输入表单
        name: 'product_name',
        placeholder: '商品名',
        icons: 'search_icon',
        show_clean: false,
        value: '',
        is_focus: false
      },
    ]
  },
  onLoad: function () {
    wx.setNavigationBarTitle({
      title: app.globalData.shopName
    });
    //设置底部导航栏
    let [isSelecteds, urls] = utils.onNavigateTap(0);
    this.setData({
      isSelecteds: isSelecteds
    })
  },
  //解决切换不刷新维内托，每次展示都会调用这个方法
  onShow: function () {
    this.getBannerAndCat();
  },
  searchBoxInput: function (e) {
    let idx = e.currentTarget.dataset.id;
    let items = this.data.items;
    items[idx].value = e.detail.value;
    this.setData({
      changed: true,
      items: items
    });
  },
  searchBoxFocus: function (e) {
    let idx = e.currentTarget.dataset.id;
    let items = this.data.items;
    items[idx].is_focus = true;
    this.setData({
      items: items
    })
  },
  searchBoxBlur: function (e) {
    let idx = e.currentTarget.dataset.id;
    let items = this.data.items;
    items[idx].show_clean = items[idx].value.length > 0;
    items[idx].is_focus = false;
    this.setData({
      items: items
    });
    this.search();
  },
  searchBoxClean: function (e) {
    let idx = e.currentTarget.dataset.id;
    let items = this.data.items;
    items[idx].show_clean = false;
    items[idx].value = '';
    this.setData({
      changed: true,
      items: items
    });
    this.search();
  },
  search: function () {
    if (this.data.changed) {
      this.toSearch();
      this.setData({
        changed: false
      })
    }
  },
  //事件处理函数
  swiperchange: function (e) {
    this.setData({
      swiperCurrent: e.detail.current * 1
    })
  },
  listenerSearchInput: function (e) {
    this.setData({
      searchInput: e.detail.value
    });
  },
  toSearch: function (e) {
    this.setData({
      p: 1,
      goods: [],
      loadingMoreHidden: true
    });
    this.getProductList();
  },
  tapBanner: function (e) {
    let id = e.currentTarget.dataset.id * 1;
    if (id !== 0) {
      wx.navigateTo({
        url: "./info?id=" + id
      });
    }
  },
  toDetailsTap: function (e) {
    wx.navigateTo({
      url: "./info?id=" + e.currentTarget.dataset.id
    });
  },
  getBannerAndCat: function () {
    wx.request({
      url: app.buildUrl("/product/index"),
      header: app.getRequestHeader(),
      data: {
        campus: app.globalData.campus_id
      },
      success: (res) => {
        let resp = res.data;
        if (resp['code'] !== 200) {
          app.alert({content: resp['msg']});
          return;
        }
        this.setData({
          banners: resp['data']['banner_list'],
          categories: resp['data']['cat_list']
        });
        this.getProductList();
      }
    });
  },
  catClick: function (e) {
    let old_id = this.data.activeCategoryId;
    let new_id = e.currentTarget.id * 1;
    this.setData({
      activeCategoryId: new_id
    });
    if (new_id !== old_id) {
      this.setData({
        loadingMoreHidden: true,
        p: 1,
        goods: []
      });
      this.getProductList();
    }
  },
  onReachBottom: function () {
    setTimeout(this.getProductList, 500);
  },
  getProductList: function () {
    if (this.data.processing || !this.data.loadingMoreHidden) {
      return;
    }
    this.setData({
      processing: true
    });
    wx.request({
      url: app.buildUrl("/product/search"),
      header: app.getRequestHeader(),
      data: {
        cat_id: this.data.activeCategoryId,
        mix_kw: this.data.items[0].value,
        p: this.data.p,
        campus: app.globalData.campus_id
      },
      success: (res) => {
        let resp = res.data;
        if (resp['code'] !== 200) {
          app.alert({content: resp['msg']});
          return;
        }
        this.setData({
          goods: this.data.goods.concat(resp['data'].list),
          p: this.data.p + 1,
          processing: false,
          loadingMoreHidden: resp['data'].has_more
        });
      },
      fail: (res) => {
        app.serverBusy()
      }
    });
  },
  //点击导航
  onNavigateTap: function (event) {
    navigate.onNavigateTap(event, this)
  }
});
