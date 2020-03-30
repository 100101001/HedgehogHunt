//获取应用实例
const util = require('../../../utils/util')
const useBalance = require("../../../pages/template/use-balance/use-balance.js")
const app = getApp()

/**
 * hasQrcode 设置用户是否有二维码
 * @param cb_success
 */
const hasQrcode = function (cb_success=(has_qr_code)=>{}) {
  wx.request({
    url: app.buildUrl("/member/has-qrcode"),
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
   *
   * 需要balance和用户has_qrcode所以
     * 如果用户没有二维码且订单项中没有二维码则需随单加购二维码（不同意则终止核对下单流程）
     * 否则正常加载订单详细信息，用户进行核对下单
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
    })
    wx.request({
      url: app.buildUrl("/order/create"),
      header: app.getRequestHeader(),
      method: 'POST',
      data: {
        type: this.data.params.type,
        goods: JSON.stringify(this.data.params.goods),
        express_address_id: this.data.default_address.id,
        discount_price: this.data.use_balance ? this.data.balance : 0//余额折扣
      },
      success: (res) => {
        let resp = res.data;
        if (resp['code'] != 200) {
          app.alert({content: resp['msg']})
          return
        }
        //下单成功前去订单列表，进行支付
        wx.redirectTo({
          url: "/mall/pages/my/order_list"
        })
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
    })
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
   * requireOrderQrcode 征得用户同意后随单加购二维码，否则不能下单
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
