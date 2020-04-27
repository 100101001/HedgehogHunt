const useBalance = require("../../template/use-balance/use-balance");
const app = getApp();
const globalData = app.globalData;
const util = require("../../../utils/util");


/**
 * 用于检测内容是否真的被编辑了
 */
// Warn if overriding existing method
if (Array.prototype.equals)
  console.warn("Overriding existing Array.prototype.equals. Possible causes: New API defines the method, there's a framework conflict or you've got double inclusions in your code.");
// attach the .equals method to Array's prototype to call it on any array
Array.prototype.equals = function (array) {
  // if the other array is a falsy value, return
  if (!array)
    return false;

  // compare lengths - can save a lot of time
  if (this.length != array.length)
    return false;

  for (let i = 0, l = this.length; i < l; i++) {
    // Check if we have nested arrays
    if (this[i] instanceof Array && array[i] instanceof Array) {
      // recurse into the nested arrays
      if (!this[i].equals(array[i]))
        return false;
    } else if (this[i] != array[i]) {
      // Warning - two different object instances will never be equal: {x:20} != {x:20}
      return false;
    }
  }
  return true;
};
// Hide method from for-in loops
Object.defineProperty(Array.prototype, "equals", {enumerable: false});

/**
 * topCharge
 * 置顶下单并支付
 * @param pay_price 支付金额
 * @param cb_success 回调函数
 * @param that 页面指针
 */
const topCharge = function (pay_price= globalData.goodsTopPrice, cb_success=()=>{}, that) {
  wx.request({
    url: app.buildUrl('/goods/top/order'),
    header: app.getRequestHeader(),
    data: {
      price: pay_price
    },
    method: 'POST',
    success: res => {
      let resp = res.data;

      //下单失败提示后返回
      if (resp['code'] !== 200) {
        app.alert({
          content: resp['msg']
        });
        that.setData({
          submitDisable: false
        });
        return
      }

      //下单成功调起支付
      let pay_data = resp['data'];
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
      app.serverBusy();
      that.setData({
        submitDisable: false
      })
    }
  })
};

/**
 * changeUserBalance
 * 扣除(改变)用户余额
 * @param unit 改变量
 * @param cb_success 回调函数
 */
const changeUserBalance = function (unit = 0, cb_success = () => {}) {
  wx.showLoading({
    title: "扣除余额中"
  });
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
};


Page({
  data: {
    loadingHidden: true,
    edit: true
  },
  onLoad: function (options) {
    //从详情页进入编辑，info是原来的帖子数据
    let info = JSON.parse(options.info);
    this.setData({
      origin_info: info
    });
    this.onLoadSetData(info);

    if (options.top) {
      //从详情页去置顶过来的，页面将直接滚动到置顶部分，供用户进行后续操作
      setTimeout(()=>{
        util.goToPoint('#top')
      }, 200)
    }
  },
  onShow: function() {},
  /**
   * 获取位置按钮，先授权，然后可以获取用户位置
   * @param e
   */
  getLocation: function (e) {
    wx.showLoading({
      title: '正在获取位置'
    });
    let loc_id = e.currentTarget.dataset.loc * 1; // string转成number
    wx.getSetting({
      success: (res) => {
        if (!res.authSetting['scope.userLocation']) {
          // 获取定位授权
          wx.authorize({
            scope: 'scope.userLocation',
            success: (res)=> {
              this.chooseLocation(loc_id);
            },
            fail: (errMsg) => {
              app.alert({content: '授权失败，将无法成功编辑信息'})
            },
            complete: (res)=> {
              wx.hideLoading()
            }
          })
        } else {
          //已经获取了授权，直接选择地址
          wx.hideLoading();
          this.chooseLocation(loc_id);
        }
      },
      fail: (res) => {
        wx.hideLoading();
        app.alert({content: '网络开小差了，请稍后再试'});
      }
    })
  },
  chooseLocation: function (loc_id = 1) {
    wx.chooseLocation({
      success: (res) => {
        let loc = [
          res.address,
          res.name,
          res.latitude,
          res.longitude,
        ];
        //判断设置的捡拾
        if (loc_id === 1) {
          this.setData({
            location: loc
          })
        } else {
          this.setData({
            os_location: loc
          })
        }
      }
    })
  },
  /**
   * 位置选取后修正精确地址描述
   * @param e
   */
  listenLocationInput: function (e) {
    let loc_id = e.currentTarget.dataset.loc * 1; // string转成number
    if (loc_id === 1) {
      let location = this.data.location;
      location[1] = e.detail.value;
      this.setData({
        location: location
      });
    } else {
      let os_location = this.data.os_location;
      os_location[1] = e.detail.value;
      this.setData({
        os_location: os_location
      });
    }
  },
  /**
   * onLoadSetData 页面一加载就设置表单数据{@see setEditFormInitData}和置顶组件
   * @param info
   */
  onLoadSetData: function(info) {
    this.setEditFormInitData(info);
    //寻物启事且原来不是置顶帖需要的置顶信息
    if (!info.business_type && !info.top) {
      this.setTopAndBalanceUseInitData()
    }
  },
  /**
   * setEditFormInitData 编辑的表单数据初始化
   * @param info
   */
  setEditFormInitData(info={}) {
    // 输入框，地址选择，图片上传框数据
    let business_type = info.business_type;
    let tips_obj = {
      "goods_name": "物品名称",
      "os_location": business_type? "发现位置": "丢失位置",
      "owner_name": business_type ? "失主姓名" : "姓名",
      "location": business_type ? "物品放置位置" : "居住地址",
      "summary": "描述",
      "mobile": "联系电话",
    };
    let items = [{
      name: "goods_name",
      placeholder: "例:校园卡",
      label: tips_obj['goods_name'],
      icons: "/images/icons/goods_name.png",
      value: info.goods_name
    },
      {
        name: "owner_name",
        placeholder: "例:可可",
        label: tips_obj['owner_name'],
        icons: "/images/icons/discount_price.png",
        value: info.owner_name,
      },
      {
        name: "mobile",
        placeholder: "高危非必填",
        label: tips_obj['mobile'],
        icons: "/images/icons/mobile.png",
        value: info.mobile
      }
    ];
    let summary_placeholder = "";
    if (business_type) {
      summary_placeholder = "添加物品描述：拾到物品的时间、地点以及物品上面的其他特征如颜色、记号等...";
    } else {
      summary_placeholder = "添加寻物描述：物品丢失大致时间、地点，记号等...";
    }
    this.setData({
      imglist: info.pics.slice(),  ///为了比对编辑是否修改了内容，slice使得副本修改不影响原info
      loadingHidden: true,
      business_type: business_type,
      items: items,
      summary_placeholder: summary_placeholder,
      summary_value: info.summary,
      tips_obj: tips_obj,
      goods_id: info.id,
      location: info.location.slice(),  //为了比对编辑是否修改了内容，slice使得副本修改不影响原info
      os_location: info.os_location.slice(),  //为了比对编辑是否修改了内容，slice使得副本修改不影响原info
      top: info.top, //原来是否置顶
      submitDisable: false
    });
  },
  /**
   * setTopAndBalanceUseInitData 置顶组件数据初始化
   */
  setTopAndBalanceUseInitData: function(){
    //置顶开关
    this.setData({
      top_price: globalData.goodsTopPrice,
      top_days: globalData.goodsTopDays,
      isTop: false  //默认置顶开关关闭
    });
    //余额勾选框
    useBalance.initData(this, (total_balance)=>{
      //计算可用余额和折后价格
      if (total_balance >= this.data.top_price - 0.01){
        //余额足够
        this.setData({
          discount_price: 0.01, //使用余额，支付0.01元
          balance: Math.max(this.data.top_price-0.01, 0)
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
        balance_use_disabled: true, //默认置顶开关关闭，所以禁用勾选框
        use_balance: false
      })
    })
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
    this.setData({submitDisable: true});
    let data = e.detail.value;
    if (app.judgeEmpty(data, this.data.tips_obj)) {
      this.setData({submitDisable: false});
      return;
    }
    let img_list = this.data.imglist;
    if (img_list.length === 0) {
      app.alert({'content': "至少要提交一张图片"});
      this.setData({submitDisable: false});
      return;
    }
    data['status'] = this.data.origin_info.status;
    data['business_type'] = this.data.business_type;
    data['img_list'] = img_list;
    data['location'] = this.data.location;
    data['os_location'] = this.data.os_location;
    data['id'] = this.data.goods_id;
    // 原来非置顶/置顶过期，编辑后置顶，才算置顶操作
    data['is_top'] = this.data.isTop && !this.data.top ? 1 : 0;
    data['days'] = this.data.isTop && !this.data.top ? this.data.top_days : 0;

    // 编辑操作是否更改了匹配信息
    let origin_info = this.data.origin_info;
    let kw_modified = (data['owner_name'] !== origin_info.owner_name ||
      data['goods_name'] !== origin_info.goods_name || !data['os_location'].equals(origin_info.os_location));
    this.data.keyword_modified = kw_modified ? 1 : 0;  // python后端bool和js的boolean不兼容
    //编辑操作是否更改了信息
    let modified = this.data.keyword_modified || !origin_info.pics.equals(img_list)
      || !origin_info.location.equals(data['location']) || origin_info.summary !== data['summary'];
    this.data.modified = modified ? 1 : 0;  // python后端bool和js的boolean不兼容
    this.toUploadData(data)
  },
  /**
   * toUploadData 根据是否置顶进行收费后编辑帖子
   * @param data 上传数据
   */
  toUploadData: function (data) {
    if (data['is_top'] === 1) {
      this.confirmTop(data)
    } else {
      this.uploadData(data)
    }
  },
  /**
   * confirmTop 询问置顶
   */
  confirmTop: function(data){
    app.alert({
      title : '温馨提示',
      content: '置顶收费' + this.data.top_price + '元，确认置顶？',
      showCancel: true,
      cb_confirm:  () => {
        //topCharge(data, this)
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
   * toTopCharge 实际进行扣费的函数
   * @param data 发布数据
   */
  toTopCharge: function (data = {}) {
    let pay_price = this.data.top_price;
    if (this.data.use_balance) {
      //支付并扣除余额再发布
      pay_price = this.data.discount_price;
      topCharge(pay_price, ()=>{
        changeUserBalance(-this.data.balance, ()=>{
          this.uploadData(data)
        })
      }, this)
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
          app.alert({content: resp['msg']});
          this.setData({submitDisable: false});
          return
        }
        //获取商品的id,之后用于提交图片
        this.uploadImage(resp['id'], data['img_list'], resp['img_list_status']);
      },
      fail: (res) => {
        app.serverBusy();
        this.setData({submitDisable: false})
      }
    })
  },
  uploadImage: function(id, img_list, img_list_status) {
    this.setData({
      loadingHidden: false,
    });
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
    });
    wx.request({
      url: app.buildUrl('/goods/update-pics'),
      method: 'POST',
      header: app.getRequestHeader(),
      data: {
        id: id,
        img_url: img_list[i - 1]
      },
      success: (res) => {
        if (img_list.length === i) {
          this.endCreate(id);
        }
      },
      fail: (res) => {
        app.serverBusy();
        this.setData({submitDisable: false, loadingHidden: true})
      }
    })
  },
  addImage: function(id, img_list, i){
    this.setData({
      i: i
    });
    wx.uploadFile({
      url: app.buildUrl('/goods/add-pics'), //接口地址
      header: app.getRequestHeader(),
      filePath: img_list[i - 1], //文件路径
      formData: {
        'id': id
      },
      name: 'file', //文件名，不要修改，Flask直接读取
      success: (res) => {
        if (img_list.length === i) {
          this.endCreate(id);
        }
      },
      fail: (res) => {
        app.serverBusy();
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
        id: id,
        edit: 1,
        keyword_modified: this.data.keyword_modified,
        modified: this.data.modified
      },
      success: (res) => {
        let resp = res.data;
        if (resp['code'] !== 200) {
          app.alert({content: resp['msg']});
          this.setData({submitDisable: false});
          return
        }
        wx.showToast({
          title: '编辑成功',
          icon: 'success',
          duration: 1000,
          success: res=>{
            setTimeout( wx.navigateBack, 800)
          }
        })
      },
      fail: (res) => {
        app.serverBusy();
        this.setData({submitDisable: false})
      }
    })
  },
  /**
   * changSetTop 改变置顶开关
   */
  changSetTop: function () {
    let isTop = this.data.isTop;
    this.setData({
      isTop: !isTop,
      balance_use_disabled: isTop, //注意这里的isTop是改变开关前的置顶开关状态(原来开着代表现在用户关了所以禁用余额勾选框)
      use_balance: isTop? false: this.data.use_balance //原来开着，说明关闭置顶，就必定false；反之开着选项则按原来的用户勾选
    })
  },
  /**
   * changeUseBalance 改变了勾选余额垫付框的状态
   * @param e
   */
  changeUseBalance: function (e) {
    useBalance.changeUseBalance(e, () => {
      this.setData({
        use_balance: e.detail.value.length === 1
      })
    })
  }
});