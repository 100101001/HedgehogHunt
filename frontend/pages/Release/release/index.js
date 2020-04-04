const useBalance = require("../../template/use-balance/use-balance")
const util = require("../../../utils/util")
const app = getApp()  //不能修改app,但可以修改app的属性
const globalData = app.globalData


/**
 * getSubscribeTmpIds 发布不同类型的物品帖，需要订阅的消息不同
 * @param business_type
 * @returns {[]}
 */
const getSubscribeTmpIds = function (business_type=0) {
  let tmpIds = []
  if (business_type == globalData.business_type.found){ //失物招领
    tmpIds = [
      globalData.subscribe.thanks,
      globalData.subscribe.finished.found
    ]
  } else {  // 寻物启事
    tmpIds = [
      globalData.subscribe.recommend,
      globalData.subscribe.finished.lost
    ]
  }
  return tmpIds
}

/**
 * topCharge
 * 置顶下单并支付
 * @param pay_price 支付金额
 * @param cb_success 回调函数
 * @param that 页面指针
 */
const topCharge = function (pay_price=globalData.goodsTopPrice, cb_success=()=>{}, that) {
  wx.request({
    url: app.buildUrl('/goods/top/order'),
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
        success: res => {
          //支付成功，继续发布
          cb_success()
        },
        fail: res => {
          app.alert({title: '支付失败', content: '重新发布或取消置顶'})
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
 * @param cb_fail 回调函数 TODO
 */
const changeUserBalance = function (unit = 0, cb_success = () => {}, cb_fail=()=>{}) {
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
    fail: res=> {
      cb_fail()
    },
    complete: res => {
      wx.hideLoading()
    }
  })
}


Page({
  data: {
    loadingHidden: true, //上传图片时的loading图标是否隐藏
    imglist: [], //发布图片列表
    dataReady: false, //页面数据是否已加载
    submitDisable: false, //是否禁按提交发布按钮
    isTop: false, //是否置顶
    use_balance: false, //使用余额
    balance_got: false, //数据正确加载，向用户显示勾选框
    balance_use_disabled: true, //禁用勾选框
    balance: 0.00, //用户可垫付余额
    total_balance: 0.00,  //用户余额
    category_arr: [] // 仅仅用于最后结束创建加入推荐列表，不用来进行通知(通知做防重处理)
  },
  /**
   * 1、扫码发布(失物招领)
   * 2、归还发布(失物招领)
   * 3、常规发布(需选择)
   * @param options
   */
  onLoad: function (options) {
    let auther_id = options.auther_id == undefined ? "" : options.auther_id
    if (globalData.isScanQrcode) { //扫码发布
      this.setData({
        business_type: 1,
        location: [],
        dataReady: true
      });
      this.setInitData()
    } else {
      if (auther_id) { //归还
        this.setData({
          auther_id: auther_id,
          business_type: 1,
          location: [],
          dataReady: true,
          info: JSON.parse(options.info)
        });
        this.setInitData()
      }
      else { //常规发布
        wx.showActionSheet({
          itemList: ['寻物启事', '失物招领'],
          success: res => {
            this.setData({
              business_type: res.tapIndex,
              location: [],
              dataReady: true
            })
            this.setInitData()
          },
          fail: (res) => {
            wx.navigateBack()
          }
        })
      }
    }
  },
  //获取位置的方法
  getLocation: function (e) {
    var that = this;
    wx.getSetting({
      success(res) {
        // 获取定位授权
        if (!res.authSetting['scope.userLocation']) {
          wx.authorize({
            scope: 'scope.userLocation',
            success() {
              that.chooseLocation();
            },
            fail(errMsg) {
              wx.showToast({ title: JSON.stringify(errMsg), icon: 'none' })
            }
          })
        } else {
          that.chooseLocation();
        }
      }
    })
  },
  chooseLocation: function () {
    wx.chooseLocation({
      success:  (res) => {
        this.setData({
          location: [
            res.address,
            res.name,
            res.latitude,
            res.longitude,
          ]
        })
      }
    })
  },
  //获取位置
  listenLocationInput: function (e) {
    let location = this.data.location;
    location[1] = e.detail.value;
    this.setData({
      location: location
    });
  },
  //预览图片
  previewImage: function (e) {
    this.setData({
      flush: false,
    });
    wx.previewImage({
      current: this.data.imglist[e.currentTarget.dataset.index], // 当前显示图片的http链接
      urls: this.data.imglist // 需要预览的图片http链接列表
    })
  },
  /**
   * 选择图片方法
   * @param e
   */
  chooseLoadPics: function (e) {
    //选择图片
    wx.chooseImage({
      count: 8 - this.data.imglist.length,
      sizeType: ['compressed'],
      sourceType: ['album', 'camera'],
      success:  (res) => {
        var tempFiles_ori = res.tempFiles;
        var imglist = this.data.imglist;
        imglist = app.addImages(tempFiles_ori, imglist);
        //显示
        this.setData({
          imglist: imglist,
          flush: false
        });
        if (imglist.length >= 9) {
          this.setData({
            pic_status: false,
          });
        } else {
          this.setData({
            pic_status: true,
          });
        }
      }
    })
  },
  // 删除图片
  deleteImg: function (e) {
    let index = e.currentTarget.dataset.index;
    let imglist = this.data.imglist;
    if (imglist.length === 1) {
      app.alert({
        'content': "删除失败，至少要提交一张图片"
      });
    } else {
      imglist.splice(index, 1);
      this.setData({
        imglist: imglist,
        flush: false,
      });
      if (imglist.length < 9) {
        this.setData({
          pic_status: true,
        });
      }
    }
  },
  /***
   * toRelease
   * 如果必填项为空，提示补上
   * 否则继续进行提交处理
   * @see handleRelease
   */
  toRelease: function () {
    this.setData({
      submitDisable: true
    })
    // 必填项判空
    let items = this.data.items
    // 需要判空的数据
    let data = {
      location: this.data.location.length? this.data.location[1] : "",
      goods_name: items[0].value,
      mobile: items[2].value,
      owner_name: items[1].value,
      summary: this.data.summary_value,
      category: this.data.category_index
    }
    if (app.judgeEmpty(data, this.data.tips_obj)) {
      this.setData({
        submitDisable: false
      })
      return
    }
    // 图片列表判空
    if (this.data.imglist.length === 0) {
      app.alert({
        'content': "至少要提交一张图片"
      });
      this.setData({
        submitDisable: false
      })
      return
    }
    //准备发布数据
    data['category'] += 1 // 因为数据库id从1开始计数
    data['business_type'] = this.data.business_type
    data['location'] = this.data.location
    data['img_list'] = this.data.imglist
    data['is_top'] = this.data.isTop ? 1 : 0
    data['days'] = this.data.isTop ? this.data.top_days : 0
    data['edit'] = 0 //标记是发布，匹配用
    this.handleRelease(data)
  },
  /**
   * handleRelease
   * 如果是无登陆发布，就不询问订阅消息，直接准备发布数据
   * 否则
   *   如果用户选择置顶先让用户确认置顶并付款，再继续发布
   *   否则先让用户选择订阅消息，然后再发布数据
   * @param data 包含发布所需数据
   * @link toRelease
   */
  handleRelease: function (data) {
    if (globalData.unLoggedRelease) {
      //无登录发布
      this.notifyAndRelease(data)
    } else {
      //根据是否勾选置顶继续订阅和发布
      if (data['is_top'] === 1) {
        //询问置顶，置顶收费并继续，取消置顶则不收费继续
        this.confirmTopAndSubNoteRelease(data)
      } else {
        //未置顶
        this.subscribeMsgAndNotifyRelease(data)
      }
    }
  },
  /**
   * confirmTopAndSubNoteRelease
   * 询问置顶
   * 如果取消重置置顶开关和余额勾选框状态以及解禁提交按钮
   * 否则就根据勾选框情况进行收费
   * @see toTopCharge
   */
  confirmTopAndSubNoteRelease: function(data){
    app.alert({
      title : '温馨提示',
      content: '置顶收费' + this.data.top_price + '元，确认置顶？',
      showCancel: true,
      cb_confirm:  () => {
        this.toTopCharge(data)
      },
      cb_cancel:  () => {
        //重置置顶开关和勾选框
        //解禁提交按钮
        this.setData({
          isTop: false,
          use_balance: false,
          balance_use_disabled: true,
          submitDisable: false
        })
      }
    })
  },
  /**
   * toTopCharge 置顶扣费后发布，失败则取消发布
   * @param data 发布数据
   * TODO 余额扣除失败，进行退钱
   */
  toTopCharge: function (data = {}) {
    let pay_price = this.data.top_price
    if (this.data.use_balance) {
      if (this.data.total_balance >= pay_price) {
        //扣除余额后发布
        changeUserBalance(-pay_price, ()=>{
          this.subscribeMsgAndNotifyRelease(data)
        })
      } else {
        //支付并扣除余额再发布
        pay_price = util.toFixed(pay_price - this.data.balance, 2)
        topCharge(pay_price, ()=>{
          changeUserBalance(-this.data.balance, ()=>{
            this.subscribeMsgAndNotifyRelease(data)
          })
        }, this)
      }
    } else {
      //支付后发布
      topCharge(pay_price, ()=>{
        this.subscribeMsgAndNotifyRelease(data)
      }, this)
    }
  },
  /**
   * subscribeMsgAndNotifyRelease
   * 先让用户订阅消息后，再继续通知失主和发布物品贴
   * @param data
   * @see getSubscribeTmpIds
   */
  subscribeMsgAndNotifyRelease: function (data) {
    wx.requestSubscribeMessage({
      tmplIds: getSubscribeTmpIds(this.data.business_type),
      complete: (res) => {
        this.notifyAndRelease(data)
      }
    })
  },
  /**
   * notifyAndRelease
   * 如果有通知用户的openid，就先通知
   * 然后继续发布物品
   * @param data 发布数据
   * @see sendNotification
   * @see uploadData
   */
  notifyAndRelease: function(data){
    //通知失主
    if (globalData.isScanQrcode) {
      this.sendNotification(data)
    }
    //上传数据
    this.uploadData(data)
  },
  /**
   * sendNotification 通知失主
   * @param data 失物数据
   * @see qrcodeNotified
   */
  sendNotification: function (data) {
    if (globalData.qrcodeOpenid) {
      wx.request({
        url: app.buildUrl('/qrcode/notify'),
        header: app.getRequestHeader(1),
        method: 'post',
        data: {
          'goods': data,
          'openid': globalData.qrcodeOpenid
        },
        complete: res => {
          //通知完毕
          app.qrcodeNotified()
        }
      })
    }
  },
  /**
   * @name releaseUnload
   * onUnload 一旦退出页面就将扫码相关全局标记重置
   * @see cancelQrcodeScan
   */
  onUnload: function () {
    if (globalData.isScanQrcode) {
      //清除扫码标记
      app.cancelQrcodeScan()
    }
  },
  /**
   * uploadData 创建帖子(填充除图片外的数据)
   * @param data 发帖数据(包含图片列表和地址)
   */
  uploadData: function (data) {
    wx.request({
      url: app.buildUrl("/goods/create"),
      method: 'POST',
      header: globalData.unLoggedRelease ? globalData.unLoggedReleaseToken : app.getRequestHeader(),
      data: data,
      success: (res) => {
        let resp = res.data;
        if (resp['code'] !== 200) {
          app.alert({
            'content': resp['msg']
          })
          this.setData({
            submitDisable: false
          })
          return
        }
        //获取商品的id,之后用于提交图片
        this.uploadImage(resp['id'], data['img_list'], resp['img_list_status']);
      },
      fail: (res) => {
        app.serverBusy();
        this.setData({
          submitDisable: false
        })
      }
    })
  },
  /**
   * uploadImage
   * 为物品贴上传图片,分为{覆盖编辑和新建两种场景}
   * 1.更新(原有图片，只需上传原图片在服务器上的文件名即可)，
   * 2.新增图片(需上传图片文件到服务器)
   * @param id 物品贴ID
   * @param img_list 图片列表
   * @param img_list_status 图片是否存于服务器
   */
  uploadImage: function (id, img_list, img_list_status) {
    this.setData({
      loadingHidden: false
    })
    for (let i = 1; i <= img_list.length; i++) {
      this.setData({
        i: i
      })
      if (img_list_status[i - 1]) {
        //图片存在，则更新
        this.updateImage(id, img_list, i)
      } else {
        //图片不存在存在，则重新上传
        this.addImage(id, img_list, i)
      }
    }
  },
  /***
   * updateImage 物品贴更新图片
   * @param id 物品贴ID
   * @param img_list 图片列表
   * @param i 第几张图
   */
  updateImage: function (id, img_list, i) {
    wx.request({
      url: app.buildUrl('/goods/update-pics'),
      method: 'POST',
      header: globalData.unLoggedRelease ? globalData.unLoggedReleaseToken : app.getRequestHeader(),
      data: {
        id: id,
        img_url: img_list[i - 1]
      },
      success: res => {
        if (img_list.length === i) {
          this.toEndCreate(id)
        }
      },
      fail: res => {
        app.serverBusy()
        this.setData({
          loadingHidden: true,
          submitDisable: false
        })
      }
    })
  },
  /***
   * addImage 物品贴新增图片
   * @param id 物品贴ID
   * @param img_list 图片列表
   * @param i 第几张图
   */
  addImage: function (id, img_list, i) {
    wx.uploadFile({
      url: app.buildUrl('/goods/add-pics'), //接口地址
      header: globalData.unLoggedRelease ? globalData.unLoggedReleaseToken : app.getRequestHeader(),
      filePath: img_list[i - 1], //文件路径
      formData: {
        'id': id
      },
      name: 'file', //文件名，不要修改，Flask直接读取
      success: (res) => {
        if (img_list.length == i) {
          this.toEndCreate(id)
        }
      },
      fail: (res) => {
        app.serverBusy()
        this.setData({
          loadingHidden: true,
          submitDisable: false
        })
      }
    })
  },
  /**
   * toEndCreate
   * 如果是归还发布的失物招领贴需要附带原寻物启事的信息
   * 否则只需传回失物招领贴ID，继续结束创建
   * @param id 结束创建的物品帖子ID
   */
  toEndCreate: function (id) {
    let auther_id = this.data.auther_id;
    let data = {}
    if (auther_id) {
      data = {
        id: id,
        auther_id: auther_id,
        target_goods_id: this.data.info.id
      }
    } else {
      data = {
        id: id
      }
    }
    data['notify_id'] = this.data.notify_id
    this.endCreate(data)
  },
  /**
   * endCreate 结束创建物品
   * @param data 结束创建参数
   */
  endCreate: function (data) {
    wx.request({
      url: app.buildUrl("/goods/end-create"),
      method: 'POST',
      header: globalData.unLoggedRelease ? globalData.unLoggedReleaseToken : app.getRequestHeader(),
      data: data,
      success: (res) => {
        let resp = res.data;
        if (resp['code'] !== 200) {
          app.alert({'content': resp['msg']})
          this.setData({
            submitDisable: false
          })
          return
        }
        //获取新的推荐匹配列表
        app.getNewRecommend()
        //初始化本地数据和全局数据
        this.setInitData();
        //用户提示
        wx.showToast({
          title: '提交成功',
          icon: 'success',
          duration: 2000,
          success: res => {
            setTimeout(() => {
              wx.redirectTo({
                url: '../../Find/Find?business_type=' + this.data.business_type,
              })
            }, 1500)
          }
        });
      },
      fail:  (res) => {
        app.serverBusy()
        this.setData({
          submitDisable: false
        })
      },
      complete: res => {
        this.setData({
          loadingHidden: true
        })
      }
    })
  },
  /**
   * 初始化页面表单{@see setFormInitData}和置顶组件数据{@see setTopAndBalanceUseInitData}
   */
  setInitData: function () {
    //发布信息表单数据初始化
    this.setFormInitData()
    //寻物启事需要的置顶信息
    if (!this.data.business_type) {
      this.setTopAndBalanceUseInitData()
    }
  },
  /**
   * setFormInitData 在初始化页面数据{@link setInitData}时，置空表单数据
   */
  setFormInitData() {
    //获取物品类别数据
    wx.request({
      url: app.buildUrl('/goods/category/all'),
      success: (res) => {
        this.setData({
          category_arr: res.data['data']['cat_list'],  //可选物品所属类别的列表
          category_default_goods: res.data['data']['cat_default']  //各物品类别下的默认填充物品名
        });
      }
    });
    // 输入框，地址选择，图片上传框数据
    let info = this.data.info;  //如果因点击归还寻物而进入发布页，info就是原寻物启事的表单数据(用于初始化发布页表单)，否则是undefined
    let business_type = this.data.business_type;
    //发布前data内需要判空的属性，对应属性缺失时，向用户显示的属性的提示语。比如data的category为空，就弹出提示“物品类别为空”
    let tips_obj = {
      "category": "物品类别",
      "goods_name": "物品名称",
      "owner_name": business_type ? "失主姓名" : "姓名",
      "location": business_type ? "物品放置位置" : "居住地址",
      "summary": "描述",
      "mobile": "联系电话"
    };
    //发布页面输入信息项的初始化（输入框占位符，输入默认值，输入框代表什么含义，icon等）
    let items = [{
      name: "goods_name",
      placeholder: "例:校园卡",
      label: tips_obj['goods_name'],
      icons: "/images/icons/goods_name.png",
      value: business_type && info ? info.goods_name : "",  //归还帖自动填充归还的物品名
    }, {
      name: "owner_name",
      placeholder: "例:可可",
      label: tips_obj['owner_name'],
      icons: "/images/icons/discount_price.png",
      value: business_type && info ? info.owner_name : "" //归还帖自动填充归还物品的失主名
    },
      {
        name: "mobile",
        placeholder: "高危非必填",
        value: "高危非必填",
        label: tips_obj['mobile'],
        icons: "/images/icons/mobile.png",
      }
    ];
    let summary_placeholder = "";
    //表单
    if (business_type) {
      summary_placeholder = "添加拾物描述：拾到物品的时间、地点以及物品上面的其他特征如颜色、记号等..."
    } else {
      summary_placeholder = "添加寻物描述：物品丢失大致时间、地点，记号等..."
    }
    this.setData({
      category_index: info ? info.category - 1 : null, //数据库的物品id是从1开始计数的，所以这里需要-1符合数组下表索引从0开始
      imglist: business_type ? [] : ['/images/icons/wanted.png'],  //寻物启事有一张默认的寻物图(图片列表)
      count: 1 - business_type,  //失物招领时business_type==1，图片为0。寻物启事时business_type==0，图片为1。图片数量
      pic_status: true,  //是否可以继续加图
      loadingHidden: true, //上传图片时的loading图标是否隐藏
      business_type: business_type, //失物招领or寻物启事标识
      items: items, //表单项
      summary_placeholder: summary_placeholder, //描述填写提示
      summary_value: "", //描述内容
      tips_obj: tips_obj, //表单项填写提示
      info_owner_name: info ? info.owner_name : "", //归还帖自动填充归还物品的失主名
      location: info ? info.location : [], //归还帖自动填充归还物品的放置地址(就近放置)
      notify_id: globalData.isScanQrcode ? globalData.qrcodeOpenid : ""  //记录通知ID，供最后把该帖子加到二维码码主的匹配推荐列表中去
    })
  },
  /**
   * setTopAndBalanceUseInitData 在 {@link setInitData} 初始化置顶组件
   */
  setTopAndBalanceUseInitData: function () {
    //置顶开关
    this.setData({
      top_price: globalData.goodsTopPrice,
      top_days: globalData.goodsTopDays,
      isTop: false
    })
    //余额勾选框
    useBalance.initData(this, (total_balance) => {
      //计算可用余额和折后价格
      if (total_balance >= this.data.top_price) {
        //余额足够
        this.setData({
          discount_price: 0, //使用余额，支付0元
          balance: this.data.top_price //可用于垫付的余额
        })
      } else {
        //余额不足
        this.setData({
          discount_price: util.toFixed(this.data.top_price - total_balance, 2), //使用余额支付的价格
          balance: total_balance  //可用于垫付的余额
        })
      }
      //默认
      this.setData({
        balance_use_disabled: true, //默认置顶开关关闭，所以禁用勾选框
        use_balance: false
      })
    })
  },
  listenerInput: function (e) {
    let idx = e.currentTarget.dataset.id
    let items = this.data.items
    items[idx].value = e.detail.value
    this.setData({
      items: items
    })
  },
  listenSummaryInput: function (e) {
    this.setData({
      summary_value: e.detail.value
    })
  },
  /**
   * changSetTop
   * 置顶开关，如果关闭禁用使用余额的选项盒子
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
   * 设置使用余额开关
   * @param e
   */
  changeUseBalance: function (e) {
    useBalance.changeUseBalance(e, () => {
      this.setData({
        use_balance: e.detail.value.length == 1
      })
    })
  },
  bindCategoryChange: function (e) {
    let index = e.detail.value
    this.setData({
      category_index: index
    })
    let items = this.data.items
    let default_goods = this.data.category_default_goods
    let input_good_name = items[0].value
    // 如果是用户输入则不随类型变化而设置类型默认物品
    items[0].value = input_good_name && default_goods.indexOf(input_good_name) == -1 ? input_good_name : default_goods[index]
    this.setData({
      items: items
    })
  }
})