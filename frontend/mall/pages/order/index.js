//获取应用实例
const useBalance = require("../../../pages/template/use-balance/use-balance.js")
const app = getApp();

Page({
  data: {
    goods_list: [],
    default_address: null,
    yun_price: 0.00,
    pay_price: 0.00,
    total_price: 0.00,
    params: null,
    express_address_id: 0,
    createOrderDisabled: false,
    dataReady: false,
    use_balance: false, //使用余额
    balance_got: false, //数据正确加载，向用户显示勾选框
    balance: 0.00, //用户可垫付余额
    total_balance: 0.00,  //用户余额
    discount_price: 0.00
  },
  /***
   * onLoad 加载订单详情页
   * @param e 下单产品列表和下单来源
   */
  onLoad: function (e) {
    var that = this;
    that.setData({
      params: JSON.parse(e.data)
    });
  },
  /***
   * onShow 订单详情页显示
   * 如果用户没有二维码且订单项中没有二维码则需随单加购二维码（不同意则终止核对下单流程）
   * 否则正常加载订单详细信息，用户进行核对下单
   */
  onShow: function () {
    this.doGetUserBalance()
    if (app.globalData.has_qrcode) {
      this.getOrderInfo();
    } else {
      //判断商品列表中有无二维码
      let goods = this.data.params['goods']
      let index = goods.findIndex(item => item.id === app.globalData.qrcodeProductId)
      if (index === -1) {
        this.requireOrderQrcode();
      } else {
        this.getOrderInfo();
      }
    }
  },
  doGetUserBalance: function () {
    useBalance.initData(this)
  },
  /***
   * toCreateOrder 确认下单的入口
   * 判断收货地址如果没有的话，提示用户操作增加
   * 否则，继续进行订单创建
   */
  toCreateOrder: function (e) {
    if (!this.data.default_address) {
      app.alert({
        'title': '温馨提示',
        'content': '请增加收货地址！'
      })
      return
    }
    this.createOrder(e)
  },
  /***
   * createOrder 根据订单列表创建订单
   */
  createOrder: function () {
    this.setData({
      createOrderDisabled: true
    })
    wx.showLoading({
      mask: true,
      title: '正在下单'
    });
    var that = this;
    var data = {
      type: this.data.params.type,
      goods: JSON.stringify(this.data.params.goods),
      express_address_id: this.data.default_address.id,
      discount_price: this.data.discount_price,
    };
    wx.request({
      url: app.buildUrl("/order/create"),
      header: app.getRequestHeader(),
      method: 'POST',
      data: data,
      success: (res) => {
        var resp = res.data;
        if (resp.code != 200) {
          app.alert({"content": resp.msg});
          return;
        }
        wx.redirectTo({
          url: "/mall/pages/my/order_list"
        });
      },
      fail: (res) => {
        app.serverBusy()
        this.setData({
          createOrderDisabled: false
        })
      },
      complete: function (res) {
        wx.hideLoading()
      }
    });
  },
  addressSet: function () {
    wx.navigateTo({
      url: "/mall/pages/my/addressSet?id=0"
    });
  },
  selectAddress: function () {
    wx.navigateTo({
      url: "/mall/pages/my/addressList"
    });
  },
  /***
   * requireOrderQrcode 征得用户同意后随单加购二维码，否则不能下单
   */
  requireOrderQrcode: function () {
    let qrcodePrice = app.globalData.qrcodePrice
    let that = this
    app.alert({
      title: '温馨提示',
      content: '您还没有闪寻码无法下单，是否加' + qrcodePrice + '元随单购买？',
      showCancel: true,
      cb_confirm: function () {
        //加入订单款项
        let params = that.data.params
        params['goods'].push({
          "id": app.globalData.qrcodeProductId,
          "price": qrcodePrice,
          "number": 1
        })
        that.setData({
          params: params
        })
        that.getOrderInfo()
      },
      cb_cancel: function () {
        //回退
        wx.navigateBack()
      }
    })
  },
  /***
   * getOrderInfo 根据订单列表的产品ID，获取详细的产品信息，并计算出支付价格
   */
  getOrderInfo: function () {
    var that = this
    var data = {
      type: this.data.params.type,
      goods: JSON.stringify(this.data.params.goods)
    };
    wx.request({
      url: app.buildUrl("/order/info"),
      header: app.getRequestHeader(),
      method: 'POST',
      data: data,
      success: function (res) {
        var resp = res.data;
        if (resp.code != 200) {
          app.alert({"content": resp.msg});
          return;
        }

        that.setData({
          goods_list: resp.data.goods_list,
          default_address: resp.data.default_address,
          yun_price: parseFloat(resp.data.yun_price),
          pay_price: parseFloat(resp.data.pay_price),
          total_price: parseFloat(resp.data.total_price),
          dataReady: true
        });

        if (that.data.default_address) {
          that.setData({
            express_address_id: that.data.default_address.id
          });
        }
      }
    });
  },
  changeUseBalance: function (e) {
    useBalance.changeUseBalance(e, () => {
        this.setData({
          use_balance: e.detail.value.length == 1
        })
        //用户显示（最终创建订单的价格仅根据订单列表）
        if (this.data.use_balance) {
          console.log("减价")
          let new_price = (this.data.pay_price - this.data.balance).toFixed(2)
          this.setData({
            discount_price: parseFloat(new_price <= 0 ? this.data.pay_price - 0.01 : this.data.balance),
            pay_price: parseFloat(new_price <= 0 ? 0.01 : new_price)
          })
          this.setData({
            total_price: this.data.pay_price + this.data.yun_price
          })
        } else {
          console.log("加价")
          this.setData({
            pay_price: parseFloat((this.data.pay_price + this.data.discount_price).toFixed(2)),
            discount_price: 0.00
          })
          this.setData({
            total_price: this.data.pay_price + this.data.yun_price
          })
        }
      }
    )
  }
});
