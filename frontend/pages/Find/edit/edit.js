const useBalance = require("../../template/use-balance/use-balance")
const app = getApp();



// /***
//  * topCharge
//  * 置顶下单并支付
//  * @param data 发布数据
//  * @param that 页面指针
//  */
// const topCharge = function (data, that) {
//   wx.request({
//     url: app.buildUrl('/goods/top/order'),
//     header: app.getRequestHeader(),
//     data: {
//       price: that.data.top_price
//     },
//     method: 'POST',
//     success: res => {
//       let resp = res.data
//
//       //下单失败提示后返回
//       if (resp['code'] !== 200) {
//         app.alert({content: resp['msg']})
//         that.setData({submitDisable: false})
//         return
//       }
//
//       //下单成功调起支付
//       let pay_data = resp['data']
//       wx.requestPayment({
//         timeStamp: pay_data['timeStamp'],
//         nonceStr: pay_data['nonceStr'],
//         package: pay_data['package'],
//         signType: pay_data['signType'],
//         paySign: pay_data['paySign'],
//         success: res => {
//           //支付成功，继续发布
//           if (res.errMsg == "requestPayment:ok") {
//             that.uploadData(data)
//           }
//           //支付失败，停止发布
//           if (res.errMsg == "requestPayment:fail cancel") {
//             that.setData({submitDisable: false})
//           }
//         },
//         fail: (res) => {
//           app.alert({'content': '微信支付失败，请稍后重试'})
//           that.setData({submitDisable: false})
//         }
//       })
//     },
//     fail: (res) => {
//       app.serverBusy()
//       that.setData({submitDisable: false})
//     }
//   })
// }
//
//

/**
 * topCharge
 * 置顶下单并支付
 * @param pay_price 支付金额
 * @param cb_success 回调函数
 * @param that 页面指针
 */
const topCharge = function (pay_price=app.globalData.goodsTopPrice, cb_success=()=>{}, that) {
  wx.request({
    url: app.buildUrl('/thank/order'),
    header: app.getRequestHeader(),
    data: {
      price: pay_price
    },
    method: 'POST',
    success: res => {
      let resp = res.data

      //下单失败提示后返回
      if (resp['code'] !== 200) {
        app.alert({
          content: resp['msg']
        })
        that.setData({
          submitDisable: false
        })
        return
      }

      //下单成功调起支付
      let pay_data = resp['data']
      wx.requestPayment({
        timeStamp: pay_data['timeStamp'],
        nonceStr: pay_data['nonceStr'],
        package: pay_data['package'],
        signType: pay_data['signType'],
        paySign: pay_data['paySign'],
        success: (res) => {
          //支付成功，继续发布
          cb_success()
        },
        fail: (res) => {
          that.setData({
            submitDisable: false
          })
        }
      })
    },
    fail: res => {
      app.serverBusy()
      that.setData({
        submitDisable: false
      })
    }
  })
}

/**
 * changeUserBalance
 * 扣除(改变)用户余额
 * @param unit 改变量
 * @param cb_success 回调函数
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
      note: "寻物置顶"
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
    loadingHidden: true,
  },
  onLoad: function(options) {
    this.onLoadSetData(app.globalData.info)
  },
  onShow: function() {},
  //获取位置的方法
  getLocation: function (e) {
    wx.chooseLocation({
      success: (res) => {
        this.setData({
          location: [
            res.address,
            res.name,
            res.latitude,
            res.longitude,
          ]
        })
      },
    })
  },
  //监听输入框
  lisentLocationInput: function (e) {
    let location = this.data.location;
    location[1] = e.detail.value;
    this.setData({
      location: location
    });
  },
  onLoadSetData: function(info) {
    var business_type = info.business_type
    if (business_type == 1) {
      var summary_placeholder = "添加物品描述：拾到物品的时间、地点以及物品上面的其他特征如颜色、记号等...";
      var tips_obj = {
        "goods_name": "物品",
        "owner_name": "失主姓名",
        "location": "物品放置位置",
        "summary": "描述",
        "mobile": "联系电话",
      };
      var items = [{
          name: "goods_name",
          placeholder: "例:校园卡",
          value: info.goods_name,
          label: "物品名称",
          icons: "/images/icons/goods_name.png",
        },
        {
          name: "owner_name",
          placeholder: "例:可可",
          label: "失主姓名",
          icons: "/images/icons/discount_price.png",
          value: info.owner_name,
        },
        {
          name: "mobile",
          placeholder: "高危非必填",
          value: info.mobile,
          label: "联系电话",
          icons: "/images/icons/goods_type.png",
        }
      ];
    } else {
      var tips_obj = {
        "goods_name": "物品",
        "owner_name": "失主姓名",
        "location": "居住地址",
        "summary": "描述",
        "mobile": "联系电话",
      };
      var items = [{
          name: "goods_name",
          placeholder: "例:校园卡",
          value: info.goods_name,
          label: "物品名称",
          icons: "/images/icons/goods_name.png",
        },
        {
          name: "owner_name",
          placeholder: "例:可可",
          value: info.owner_name,
          label: "姓名",
          icons: "/images/icons/discount_price.png",
        },
        {
          name: "mobile",
          placeholder: "高危非必填",
          label: "联系电话",
          value: info.mobile,
          icons: "/images/icons/goods_type.png",
        }
      ];
      var summary_placeholder = "添加寻物描述：物品丢失大致时间、地点，记号等...";
    }
    this.setData({
      imglist: info.pics,
      loadingHidden: true,
      business_type: business_type,
      items: items,
      summary_placeholder: summary_placeholder,
      summary_value: info.summary,
      tips_obj: tips_obj,
      goods_id: info.id,
      location: info.location,
      top: info.top, //原来是否置顶
      submitDisable: false
    })
    //寻物启事且原来不是置顶帖需要的置顶信息
    if (!business_type && !info.top) {
      //置顶开关
      this.setData({
        top_price: app.globalData.goodsTopPrice,
        top_days: app.globalData.goodsTopDays,
        isTop: false
      })
      //余额勾选框
      useBalance.initData(this, (total_balance)=>{
        //计算可用余额和折后价格
        if (total_balance > this.data.top_price){
          //余额足够
          this.setData({
            discount_price: 0, //使用余额，支付0元
            balance: this.data.top_price
          })
        } else {
          //余额不足
          this.setData({
            discount_price: util.toFixed(this.data.top_price - total_balance, 2), //使用余额支付的价格
            balance: total_balance
          })
        }
        //默认
        this.setData({
          balance_use_disabled: true //默认置顶开关关闭，所以禁用勾选框
        })
      })
    }
  },
  //预览图片
  previewImage: function(e) {
    this.setData({
      flush: false,
    });
    wx.previewImage({
      current: this.data.imglist[e.currentTarget.dataset.index], // 当前显示图片的http链接
      urls: this.data.imglist // 需要预览的图片http链接列表
    })
  },
  //选择图片方法
  chooseLoadPics: function(e) {
    var imglist = this.data.imglist;
    //选择图片
    wx.chooseImage({
      count: 8 - imglist.length,
      sizeType: ['compressed'],
      sourceType: ['album', 'camera'],
      success: (res) => {
        // TODO:图片查重
        imglist = app.addImages(res.tempFiles, imglist);
        //显示
        this.setData({
          imglist: imglist
        })
      }
    })
  },
  // 删除图片
  deleteImg: function(e) {
    var imglist = this.data.imglist;
    if (imglist.length === 1) {
      app.alert({
        'content': "删除失败，至少要提交一张图片"
      });
    } else {
      imglist.splice(e.currentTarget.dataset.index, 1);
      this.setData({
        imglist: imglist
      })
    }
  },
  //表单提交
  formSubmit: function (e) {
    this.setData({submitDisable: true})
    var data = e.detail.value
    if (app.judgeEmpty(data, this.data.tips_obj)) {
      this.setData({submitDisable: false})
      return
    }
    let img_list = this.data.imglist
    if (img_list.length === 0) {
      app.alert({'content': "至少要提交一张图片"})
      this.setData({submitDisable: false})
      return
    }
    data['business_type'] = this.data.business_type
    data['img_list'] = img_list
    data['location'] = this.data.location
    data['id'] = this.data.goods_id
    // 原来非置顶/置顶过期，编辑后置顶，才算置顶操作
    data['is_top'] = this.data.isTop && !this.data.top ? 1 : 0
    data['days'] = this.data.isTop && !this.data.top ? this.data.top_days : 0
    this.toUploadData(data)
  },
  /**
   * toUploadData 根据是否置顶进行收费后编辑帖子
   * @param data 上传数据
   */
  toUploadData: function(data){
    if(data['is_top'] == 1){
      this.confirmTopAndUpload(data)
    }else{
      this.uploadData(data)
    }
  },
  /**
   * confirmTopAndUpload
   * 询问置顶
   */
  confirmTopAndUpload: function(data){
    app.alert({
      title : '温馨提示',
      content: '置顶收费' + this.data.top_price + '元，确认置顶？',
      showCancel: true,
      cb_confirm:  () => {
        //topCharge(data, this)
        this.toTopCharge(data)
      },
      cb_cancel:  () => {
        this.setData({isTop: false})
        data['is_top'] = 0
        data['days'] = 0
        this.uploadData(data)
      }
    })
  },
  /**
   * toTopCharge 实际进行扣费的函数
   * @param data 发布数据
   */
  toTopCharge: function (data = {}) {
    let pay_price = this.data.top_price
    if (this.data.use_balance) {
      if (this.data.total_balance >= pay_price) {
        //扣除余额后发布
        changeUserBalance(-pay_price, ()=>{
          this.uploadData(data)
        })
      } else {
        //支付并扣除余额再发布
        pay_price -= this.data.balance
        topCharge(pay_price, ()=>{
          changeUserBalance(-this.data.balance, ()=>{
            this.uploadData(data)
          })
        }, this)
      }
    } else {
      //支付后发布
      topCharge(pay_price, ()=>{
        this.uploadData(data)
      }, this)
    }
  },
  //上传文件
  uploadData: function(data) {
    wx.request({
      url: app.buildUrl("/goods/edit"),
      method: 'POST',
      header: app.getRequestHeader(),
      data: data,
      success: (res) => {
        let resp = res.data;
        if (resp['code'] !== 200) {
          app.alert({content: resp['msg']})
          this.setData({submitDisable: false})
          return
        }
        //获取商品的id,之后用于提交图片
        this.uploadImage(resp['id'], data['img_list'], resp['img_list_status']);
      },
      fail: (res) => {
        app.serverBusy()
        this.setData({submitDisable: false})
      }
    })
  },
  uploadImage: function(id, img_list, img_list_status) {
    this.setData({
      loadingHidden: false,
    })
    for (let i = 1; i <= img_list.length; i++) {
      if (img_list_status[i - 1]) {
        //图片存在，则更新
        this.updateImage(id, img_list, i)
      } else {
        //图片不存在存在，则重新上传
        this.addImage(id, img_list, i)
      }
    }
  },
  updateImage: function(id, img_list, i){
    this.setData({
      i: i
    })
    wx.request({
      url: app.buildUrl('/goods/update-pics'),
      method: 'POST',
      header: app.getRequestHeader(),
      data: {
        id: id,
        img_url: img_list[i - 1]
      },
      success: (res) => {
        if (img_list.length == i) {
          this.endCreate(id);
        }
      },
      fail: (res) => {
        app.serverBusy()
        this.setData({submitDisable: false, loadingHidden: true})
      }
    })
  },
  addImage: function(id, img_list, i){
    this.setData({
      i: i
    })
    wx.uploadFile({
      url: app.buildUrl('/goods/add-pics'), //接口地址
      header: app.getRequestHeader(),
      filePath: img_list[i - 1], //文件路径
      formData: {
        'id': id
      },
      name: 'file', //文件名，不要修改，Flask直接读取
      success: (res) => {
        if (img_list.length == i) {
          this.endCreate(id);
        }
      },
      fail: (res) => {
        app.serverBusy()
        this.setData({submitDisable: false, loadingHidden: true})
      }
    })
  },
  endCreate: function(id) {
    wx.request({
      url: app.buildUrl("/goods/end-create"),
      method: 'POST',
      header: app.getRequestHeader(),
      data: {
        id: id
      },
      success: (res) => {
        let resp = res.data;
        if (resp['code'] !== 200) {
          app.alert({content: resp['msg']})
          this.setData({submitDisable: false})
          return
        }
        app.globalData.info={}
        wx.showToast({
          title: '提交成功',
          icon: 'success',
          duration: 2000,
          success: res=>{
            setTimeout(function(){
              wx.navigateBack()
            }, 1500)
          }
        })
      },
      fail: (res) => {
        app.serverBusy()
        this.setData({submitDisable: false})
      },
      complete: (res) => {
        this.setData({loadingHidden: true})
      },
    })
  },
  /**
   * changSetTop 改变置顶
   */
  changSetTop: function () {
    let isTop = this.data.isTop
    this.setData({
      isTop: !isTop,
      balance_use_disabled: isTop,
      use_balance: isTop? false: this.data.use_balance //原来开着，说明关闭置顶，就必定false；反之开着选项则按原来的用户勾选
    })
  },
  /**
   *
   * @param e
   */
  changeUseBalance: function (e) {
    useBalance.changeUseBalance(e, () => {
      this.setData({
        use_balance: e.detail.value.length == 1
      })
    })
  }
});