//index.js
const app = getApp();
const navigate = require("../template/navigate-bar1/navigate-bar1-template.js");
const utils = require("../../utils/util.js");
Page({
  data: {
    dataReady: false,
    p: 1,
    list: [],
    loadingMoreHidden: false
  },
  onLoad: function () {
    //设置底部导航栏
    let [isSelecteds, urls] = utils.onNavigateTap(1);
    this.setData({
      isSelecteds: isSelecteds
    })
  },
  onShow: function () {
    this.setData({
      dataReady: false,
      p: 1,
      list: []
    });
    this.getCartList();
  },
  //每项前面的选中框
  selectTap: function (e) {
    let index = e.currentTarget.dataset.index;
    let list = this.data.list;
    if (index !== "" && index != null) {
      list[parseInt(index)].active = !list[parseInt(index)].active;
      this.setPageData(this.getSaveHide(), this.totalPrice(), this.allSelect(), this.noSelect(), list);
    }
  },
  /**
   * 计算是否全选了
   * @returns {boolean}
   */
  allSelect: function () {
    let list = this.data.list;
    let allSelect = true;
    for (let i = 0; i < list.length; i++) {
      if (!list[i].active) {
        allSelect = false;
        break;
      }
    }
    return allSelect;
  },
  /**
   * 计算是否都没有选
   * @returns {boolean}
   */
  noSelect: function () {
    let list = this.data.list;
    let noSelect = true;
    for (let i = 0; i < list.length; i++) {
      if (list[i].active) {
        noSelect = false;
        break;
      }
    }
    return noSelect;
  },
  /**
   * 点击全选按钮后，每个购物车项的选中与不选中
   */
  bindAllSelect: function () {
    let currentAllSelect = this.data.allSelect;
    let list = this.data.list;
    for (let i = 0; i < list.length; i++) {
      list[i].active = !currentAllSelect;
    }
    this.setPageData(this.getSaveHide(), this.totalPrice(), !currentAllSelect, this.noSelect(), list);
  },
  /**
   * 加选中的商品(数组index)数量
   * @param e
   */
  jiaBtnTap: function (e) {
    let index = e.currentTarget.dataset.index;
    let list = this.data.list;
    list[parseInt(index)].number++;
    this.setPageData(this.getSaveHide(), this.totalPrice(), this.allSelect(), this.noSelect(), list);
    this.setCart(list[parseInt(index)].product_id, list[parseInt(index)].number);
  },
  /**
   * 减去选中的商品(数组index)数量
   * @param e
   */
  jianBtnTap: function (e) {
    let index = e.currentTarget.dataset.index;
    let list = this.data.list;
    if (list[parseInt(index)].number > 1) {
      list[parseInt(index)].number--;
      this.setPageData(this.getSaveHide(), this.totalPrice(), this.allSelect(), this.noSelect(), list);
      this.setCart(list[parseInt(index)].product_id, list[parseInt(index)].number);
    }
  },
  /**
   * 开始和结束编辑默认全不选
   */
  editTap: function () {
    let list = this.data.list;
    for (let i = 0; i < list.length; i++) {
      list[i].active = false;
    }
    this.setPageData(!this.getSaveHide(), this.totalPrice(), this.allSelect(), this.noSelect(), list);
  },
  /**
   * 选中保存
   */
  saveTap: function () {
    let list = this.data.list;
    for (let i = 0; i < list.length; i++) {
      list[i].active = true;
    }
    this.setPageData(!this.getSaveHide(), this.totalPrice(), this.allSelect(), this.noSelect(), list);
  },
  getSaveHide: function () {
    return this.data.saveHidden;
  },
  /**
   * 计算总价
   * @returns {number}
   */
  totalPrice: function () {
    let list = this.data.list;
    let totalPrice = 0.00;
    for (let i = 0; i < list.length; i++) {
      if (!list[i].active) {
        continue;
      }
      totalPrice = totalPrice + parseFloat(list[i].price) * list[i].number;
    }
    return totalPrice;
  },
  /**
   * 设置页面数据
   * @param saveHidden 是否正在编辑
   * @param total
   * @param allSelect 是否全选
   * @param noSelect 是否全不选
   * @param list 购物车{id num}产品列表
   */
  setPageData: function (saveHidden, total, allSelect, noSelect, list) {
    this.setData({
      list: list,
      saveHidden: saveHidden,
      totalPrice: total,
      allSelect: allSelect,
      noSelect: noSelect,
      dataReady: true
    });
  },
  /**
   * 将页面勾选的商品组合成数组对象，去下单结算页面
   */
  toPayOrder: function () {
    let data = {
      type: "cart",
      goods: []
    };
    let list = this.data.list;
    for (let i = 0; i < list.length; i++) {
      if (!list[i].active) {
        continue;
      }
      data['goods'].push({
        "id": list[i].product_id,
        "price": list[i].price,
        "number": list[i].number
      });
    }
    wx.navigateTo({
      url: "/mall/pages/order/index?data=" + JSON.stringify(data)
    });
  },
  /**
   * 回进入页
   */
  toIndexPage: function () {
    let campus_name = app.globalData.campus_name;
    let campus_id = app.globalData.campus_id;
    wx.redirectTo({
      url: '/mall/pages/index?campus_id=' + campus_id +
        '&campus_name=' + encodeURIComponent(campus_name),
    })
  },
  //选中删除的数据
  deleteSelected: function () {
    let list = this.data.list;
    let goods = [];
    list = list.filter(function (item) {
      if (item.active) {
        goods.push({
          "id": item.product_id
        })
      }
      return !item.active;
    });
    this.setPageData(this.getSaveHide(), this.totalPrice(), this.allSelect(), this.noSelect(), list);
    //发送请求到后台删除数据
    wx.request({
      url: app.buildUrl("/cart/del"),
      header: app.getRequestHeader(),
      method: 'POST',
      data: {
        goods: JSON.stringify(goods)
      },
      fail: (res) => {
        app.serverBusy();
      }
    });
  },
  /**
   * 进入后获取用户购物中的商品项 {id, quantity}
   */
  getCartList: function () {
    wx.request({
      url: app.buildUrl("/cart/index"),
      data: {
        p: this.data.p
      },
      header: app.getRequestHeader(),
      success: (res) => {
        let resp = res.data;
        if (resp['code'] !== 200) {
          app.alert({content: resp['msg']});
          return;
        }
        let data = resp['data'];
        this.setData({
          list: this.data.list.concat(data['list']),
          saveHidden: true,
          totalPrice: 0.00,
          allSelect: true,
          noSelect: false,
          p: this.data.p + 1,
          loadingMoreHidden: data['has_more']
        });
        this.setPageData(this.getSaveHide(), this.totalPrice(), this.allSelect(), this.noSelect(), this.data.list);
      },
      fail: (res) => {
        app.serverBusy();
      }
    });
  },
  /**
   * 设置购物车某一项商品的数量
   * @param product_id
   * @param number
   */
  setCart: function (product_id, number) {
    let data = {
      id: product_id,
      number: number
    };
    wx.request({
      url: app.buildUrl("/cart/set"),
      header: app.getRequestHeader(),
      method: 'POST',
      data: data,
      fail: (res) => {
        app.serverBusy()
      }
    });
  },
  //点击导航
  onNavigateTap: function (event) {
    navigate.onNavigateTap(event, this)
  },
  /**
   * 如果还有就继续加载数据
   */
  onReachBottom: function () {
    if (!this.data.loadingMoreHidden) {
      setTimeout(this.getCartList, 500);
    }
  }
});
