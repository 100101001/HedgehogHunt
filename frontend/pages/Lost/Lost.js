var goodsData = require("../../data/posts-data.js");
var util = require("../../utils/util.js");
var app = getApp();
Page({
  data: {
    banners: ["/images/goods/book.jpg", "/images/goods/ear_phone.jpg"],
    activeCategoryId: -1,
    categories: [
      {
        id: -1,
        name: '全部',
      },
      {
        id: 0,
        name: '待找回'
      },
      {
        id: 1,
        name: '预找回'
      },
      {
        id: 2,
        name: '已找回'
      },
    ],
  },

  onLoad: function (options) {
    var goodsList = goodsData.goodsList;
    //截取前14个字当做概况
    for (var i in goodsList) {
      goodsList[i].content = goodsList[i].summary.substring(0, 27) + "...";
    }
    //设置底部导航栏
    var [isSelecteds, urls] = util.onNavigateTap(3);
    this.setData({
      isSelecteds: isSelecteds,
      goodsList: goodsList
    })
  },
  //事件处理函数
  swiperchange: function (e) {
    this.setData({
      swiperCurrent: e.detail.current
    })
  },
  catClick: function (e) {
    //选择一次分类时返回选中值
    this.setData({
      activeCategoryId: e.currentTarget.id,
      p: 1,
      goods_list: [],
      loadingMoreHidden: true
    });
    // this.getGoodsList();
  },

  onBindConfirm: function (event) {
    util.showMessage('获取值', this.data.searchName + "和" + this.data.searchGoodsType);
  },

  //点击信息卡查看详情
  onDetailTap: function (event) {
    var id = event.currentTarget.dataset.id;
    wx.navigateTo({
      url: '../Find/info/info',
    })
  },
  //下拉刷新
  onPullDownRefresh: function (event) {
    util.showMessage("下拉刷新函数", "已经写好");
    wx.stopPullDownRefresh();
  },

  //上滑加载
  onReachBottom: function (event) {
    util.showMessage("上滑加载", "已经写好");
  },

  //点击导航图标
  onNavigateTap: function (event) {
    var id = event.currentTarget.dataset.id * 1;//乘1强制转换成数字
    var [isSelecteds, urls] = util.onNavigateTap(id, 2);
    this.setData({
      isSelecteds: isSelecteds
    })
    wx.redirectTo({
      url: urls[id],
    })
  },
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
              id: id
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
})