//获取应用实例
const util = require('../../../utils/util');
const useBalance = require("../../../pages/template/use-balance/use-balance.js");
const app = getApp();

/**
 * hasQrcode 设置用户是否有二维码
 * @param cb_success
 * @link orderIndexOnload
 */
const hasQrcode = function (cb_success=(has_qr_code)=>{}) {
  wx.request({
    url: app.buildUrl("/member/has/qrcode"),
    header: app.getRequestHeader(),
    success: res => {
      let resp = res.data
      if (resp['code'] !== 200) {
        app.alert({content: '服务器开小差了，请稍后重试', cb_confirm: ()=>{wx.navigateBack()}})
        return
      }
      cb_success(resp['data']['has_qr_code'])
    }
  })
}

/**
 * 创建订单
 * @param data
 * @param cb_success
 * @param that
 * @link doCreateOrder
 */
const createOrder = function(data={}, cb_success = ()=>{}, that){
  that.setData({
    createOrderDisabled: true
  })
  wx.showLoading({
    mask: true,
    title: '正在下单'
  })
  wx.request({
    url: app.buildUrl("/order/create"),
    header: app.getRequestHeader(),
    method: 'POST',
    data: data,
    success: (res) => {
      let resp = res.data;
      if (resp['code'] != 200) {
        app.alert({content: resp['msg']})
        that.setData({
          createOrderDisabled: false
        })
        return
      }
      //下单成功前去订单列表，进行支付
      cb_success()
    },
    fail: (res) => {
      app.serverBusy()
      that.setData({
        createOrderDisabled: false
      })
    },
    complete: function (res) {
      wx.hideLoading()
    }
  })
}
/**
 * 创建订单成功后回调
 * 根据有无余额折扣进行余额扣除{@see changeUserBalance}
 * @param balance_discount
 */
const onCreateOrderSuccess = function (balance_discount) {
  if (balance_discount) {
    changeUserBalance(-balance_discount, () => {
      wx.redirectTo({
        url: "/mall/pages/my/order_list"
      })
    })
  } else {
    wx.redirectTo({
      url: "/mall/pages/my/order_list"
    })
  }
}
/**
 * 用户余额扣除
 * @param unit 余额变化
 * @param cb_success 回调函数
 * @link onCreateOrderSuccess 成功创建订单后立即扣除余额
 */
const changeUserBalance = function (unit = 0, cb_success = () => {}) {
  wx.showLoading({
    title: "扣除余额中"
  })
  wx.request({
    url: app.buildUrl("/member/balance/change"),
    header: app.getRequestHeader(),
    data: {
      unit: unit,
      note: "在线购物"
    },
    success: res => {
      cb_success()
    },
    complete: res => {
      wx.hideLoading()
    }
  })
}


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
   * @name orderIndexOnload
   * onLoad 加载订单详情页
   * 如果用户没有二维码{@see hasQrcode}且订单项中没有二维码则需随单加购二维码{@see requireOrderQrcode}
   * 否则正常加载订单详细信息，用户进行核对下单{@see getOrderInfo}
   * @param e 下单产品列表和下单来源
   */
  onLoad: function (e) {
    this.setData({
      params: JSON.parse(e.data)
    })
    hasQrcode((has_qr_code) => {
      if (has_qr_code) {
        this.getOrderInfo();
      } else {
        //判断商品列表中有无二维码
        let goods = this.data.params['goods']
        let index = goods.findIndex(item => item.id === app.globalData.qrcodeProductId)
        if (index === -1) {
          //没有二维码要求加购
          this.requireOrderQrcode();
        } else {
          //有二维码正常获取订单信息
          this.getOrderInfo();
        }
      }
    })
  },
  /***
   * onShow 订单详情页显示
   */
  onShow: function () {
  },
  /***
   * toCreateOrder 确认下单的入口
   * 收货地址判非空后，继续进行订单创建{@see doCreateOrder}
   */
  toCreateOrder: function (e) {
    if (!this.data.default_address) {
      app.alert({
        'title': '温馨提示',
        'content': '请增加收货地址！'
      })
      return
    }
    this.doCreateOrder()
  },
  /**
   * doCreateOrder 创建订单
   * 先创建订单 {@see createOrder} , 成功后扣除余额{@see changeUserBalance}
   * @link toCreateOrder
   */
  doCreateOrder: function() {
    let data = {
      type: this.data.params.type, //根据type后端会扣除购物车商品
      goods: JSON.stringify(this.data.params.goods), //订单所有商品(其数量和价格)
      express_address_id: this.data.default_address.id, //订单收货地址(后端存为快递信息)
      discount_price: this.data.use_balance ? this.data.balance : 0, //余额折扣
      discount_type: this.data.use_balance? '账户余额': ''//折扣类型
    }
    createOrder(data, () => {
      onCreateOrderSuccess(data.discount_price)
    }, this)
  },
  /**
   * addressSet 无地址前往增加地址
   */
  addressSet: function () {
    wx.navigateTo({
      url: "/mall/pages/my/addressSet?id=0"
    })
  },
  /**
   * selectAddress 有地址，前往选择其他地址
   */
  selectAddress: function () {
    wx.navigateTo({
      url: "/mall/pages/my/addressList"
    })
  },
  /***
   * requireOrderQrcode 征得用户同意后随单加购二维码，然后继续核对订单信息{@see getOrderInfo}。否则不能下单
   * @link orderIndexOnload
   */
  requireOrderQrcode: function () {
    let qrcodePrice = app.globalData.qrcodePrice
    app.alert({
      title: '温馨提示',
      content: '您还没有闪寻码无法下单，是否加' + qrcodePrice + '元随单购买？',
      showCancel: true,
      cb_confirm:  () => {
        //将二维码加入订单产品列表
        let params = this.data.params
        params['goods'].push({
          "id": app.globalData.qrcodeProductId,
          "price": qrcodePrice,
          "number": 1
        })
        this.setData({
          params: params
        })
        this.getOrderInfo()
      },
      cb_cancel: function () {
        //回退
        wx.navigateBack()
      }
    })
  },
  /***
   * getOrderInfo 根据订单列表的产品ID，获取详细的产品信息，并计算出支付价格
   * 初始化余额垫付框
   */
  getOrderInfo: function () {
    wx.request({
      url: app.buildUrl("/order/info"),
      header: app.getRequestHeader(),
      method: 'POST',
      data: {
        type: this.data.params.type,
        goods: JSON.stringify(this.data.params.goods)
      },
      success:  (res) => {
        let resp = res.data
        if (resp['code'] != 200) {
          app.alert({"content": resp['msg']});
          return
        }
        let data = resp['data']
        this.setData({
          goods_list: data.goods_list,
          default_address: data.default_address,
          yun_price: parseFloat(data.yun_price),
          pay_price: parseFloat(data.pay_price),
          total_price: parseFloat(data.total_price),
          dataReady: true
        })

        //初始化余额勾选框
        useBalance.initData(this, (total_balance)=>{
          if(total_balance >= this.data.pay_price){ //运费不进行抵扣
            //余额够花，至少要支付0.01元
            this.setData({
              balance: util.toFixed(this.data.pay_price - 0.01, 2), //可用于折扣的余额
              low_total_price: util.toFixed(this.data.yun_price + 0.01, 2)
            })
          }else{
            //余额不够花
            this.setData({
              balance: util.toFixed(total_balance, 2), //可用于折扣的余额
              low_total_price: util.toFixed(this.data.total_price - total_balance, 2)
            })
          }
          //如果可用金额为0元，那么就禁用勾选框(余额不一定为0)
          this.setData({
            balance_use_disabled: this.data.balance <= 0
          })
        })

        if (this.data.default_address) {
          this.setData({
            express_address_id: this.data.default_address.id
          })
        }
      }
    })
  },
  /**
   * changeUseBalance 用户操作了使用余额的勾选框
   * 动态更新视图中合计价格，折扣价格
   * @param e
   */
  changeUseBalance: function (e) {
    useBalance.changeUseBalance(e, () => {
        this.setData({
          use_balance: e.detail.value.length == 1
        })
      }
    )
  }
})
