//index.js
//获取应用实例
const app = getApp();
const WxParse = require('../wxParse/wxParse.js');
const utils = require('../utils/util.js');

Page({
  data: {
    autoplay: true,
    interval: 3000,
    duration: 1000,
    swiperCurrent: 0,
    hideShopPopup: true,
    buyNumber: 1,
    buyNumMin: 1,
    buyNumMax: 1,
    canSubmit: false, //  选中时候是否允许加入购物车
    shopCarInfo: {},
    shopType: "addShopCar",//购物类型，加入购物车或立即购买，默认为加入购物车,
    id: 0,
    shopCarNum: 0,
    commentCount: 2,
    notInCart: [],
    infos: [],
    info: {},
    selected_id: 0,
    dataReady: false
  },
  onLoad: function (options) {
    this.setData({
      id: options.id * 1
    });
  },
  onShow: function () {
    this.getInfo();
    this.getComments();
  },
  goShopCar: function () {
    if (!app.loginTip()) {
      return;
    }
    wx.redirectTo({
      url: "/mall/pages/cart/index"
    });
  },
  toAddShopCar: function () {
    if (!app.loginTip()) {
      return;
    }
    this.setData({
      shopType: "addShopCar"
    });
    this.bindGuiGeTap();
  },
  tobuy: function () {
    if (!app.loginTip()) {
      return;
    }
    this.setData({
      shopType: "tobuy"
    });
    this.bindGuiGeTap();
  },
  addShopCar: function () {
    if (!app.loginTip()) {
      return
    }
    if (this.data.shopCarNum >= 99) {
      app.alert({content: "购物车已满，请清空购物车后重试"});
      this.setData({
        hideShopPopup: true
      });
      return
    }
    let notInCart = this.data.notInCart;
    let idx = notInCart.indexOf(this.data.info.id);
    wx.request({
      url: app.buildUrl("/cart/add"),
      header: app.getRequestHeader(),
      method: 'POST',
      data: {
          "id": this.data.info.id,
          "number": this.data.buyNumber
      },
      success:  (res) => {
        let resp = res.data;
        app.alert({content: resp['msg']});
        this.setData({
          hideShopPopup: true,
          shopCarNum: idx >= 0 ? this.data.shopCarNum + 1 : this.data.shopCarNum
        });
        if (idx >= 0) {
          notInCart.splice(idx, idx + 1);
          this.setData({
            notInCart: notInCart
          })
        }
      }
    });
  },
  buyNow: function () {
    let data = {
      goods: [
        {
          "id": this.data.info.id,
          "price": this.data.info.price,
          "number": this.data.buyNumber
        }
      ]
    };
    this.setData({
      hideShopPopup: true
    });
    wx.navigateTo({
      url: "/mall/pages/order/index?data=" + JSON.stringify(data)
    });
  },
  /**
   * 规格选择弹出框
   */
  bindGuiGeTap: function () {
    this.setData({
      hideShopPopup: false
    });
  },
  /**
   * 规格选择弹出框隐藏
   */
  closePopupTap: function () {
    this.setData({
      hideShopPopup: true
    })
  },
  numJianTap: function () {
    if (this.data.buyNumber <= this.data.buyNumMin) {
      return;
    }
    this.setData({
      buyNumber: this.data.buyNumber - 1
    });
  },
  numJiaTap: function () {
    if (this.data.buyNumber >= this.data.buyNumMax) {
      return;
    }
    this.setData({
      buyNumber: this.data.buyNumber + 1
    });
  },
  //事件处理函数
  swiperchange: function (e) {
    this.setData({
      swiperCurrent: e.detail.current
    })
  },
  getInfo: function () {
    wx.request({
      url: app.buildUrl("/product/info"),
      header: app.getRequestHeader(),
      data: {
        id: this.data.id
      },
      success:  (res) => {
        let resp = res.data;
        if (resp['code'] !== 200) {
          app.alert({content: resp['msg'], cb_confirm:wx.navigateBack});
          return;
        }
        let data = resp['data'];
        let selected_id = this.data.selected_id;
        this.setData({
          selected_id: selected_id === 0 ? 0 : selected_id,
          info: data.info[selected_id],
          infos: data.info,
          buyNumMax: data.info.stock,
          shopCarNum: data['cart_number'],
          notInCart: data['not_in_cart'],
          dataReady: true
        });
        WxParse.wxParse('article', 'html', data.info[0].summary, this, 5);
      }
    });
  },
  getComments: function () {
    wx.request({
      url: app.buildUrl("/product/comments"),
      header: app.getRequestHeader(),
      data: {
        id: this.data.id
      },
      success:  (res) => {
        let resp = res.data;
        if (resp['code'] !== 200) {
          app.alert({content: resp['msg']});
          return;
        }
        let data = resp['data'];
        this.setData({
          commentList: data.list,
          commentCount: data.count,
        });
      }
    });
  },
  onShareAppMessage: function () {
    return {
      title: this.data.info.name,
      path: '/mall/pages/info?id=' + this.data.info.id,
      success:  (res) => {
        // 转发成功
        wx.request({
          url: app.buildUrl("/member/share"),
          header: app.getRequestHeader(),
          method: 'POST',
          data: {
            url: utils.getCurrentPageUrlWithArgs()
          },
          success:  (res) => {

          },
          complete: (res) => {
              wx.showToast({title: '积分加5'})
          }
        });
      },
      fail:  (res) => {
        // 转发失败
      }
    }
  },
  //点击预览图片
  previewImage: function (e) {
    let img = this.data.info['main_image'];
    wx.previewImage({
      current: img, // 当前显示图片的http链接
      urls: [img] // 需要预览的图片http链接列表
    })
  },
  //切换商品规格
  setOption: function (e) {
    let idx = e.currentTarget.dataset.id * 1;
    let info = this.data.infos[idx];
    this.setData({
      info: info,
      selected_id: idx
    });
    WxParse.wxParse('article', 'html', info.summary, this, 5);
  }
});
