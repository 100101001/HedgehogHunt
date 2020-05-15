const useBalance = require("../../template/use-balance/use-balance");
const util = require("../../../utils/util");
const app = getApp();  //不能修改app,但可以修改app的属性
const globalData = app.globalData;


/**
 * getSubscribeTmpIds 发布不同类型的物品帖，需要订阅的消息不同
 * @param business_type
 * @returns {[]}
 */
const getSubscribeTmpIds = function (business_type = 0) {
  let tmpIds = [];
  if (business_type === globalData.business_type.found) { //失物招领
    tmpIds = [
      globalData.subscribe.finished.found,
      globalData.subscribe.thanks
    ]
  } else if (business_type === globalData.business_type.lost) {  // 寻物启事
    tmpIds = [
      globalData.subscribe.recommend,
      globalData.subscribe.return
    ]
  } else { //归还贴和扫码归还
    tmpIds = [
      globalData.subscribe.finished.return,
      globalData.subscribe.thanks
    ]
  }
  return tmpIds
};

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
        success: res => {
          //支付成功，继续发布
          cb_success()
        },
        fail: res => {
          app.alert({title: '支付失败', content: '重新发布或取消置顶'});
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
 * @param cb_fail 回调函数 TODO
 */
const changeUserBalance = function (unit = 0, cb_success = () => {}, cb_fail=()=>{}) {
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
    fail: res=> {
      cb_fail()
    },
    complete: res => {
      wx.hideLoading()
    }
  })
};

/**
 * onFailContactTech 置顶付款后，扣除余额失败
 * @param title
 * @param content
 */
const onFailContactTech = function (title = "跳转提示", content = '服务出错了，为避免您的利益损失，将跳转联系技术支持') {
  app.alert({
    title: title,
    content: content,
    cb_confirm: () => {
      wx.navigateTo({
        url: '/pages/Mine/connect/index?only_tech_contact='+ 1
      })
    }
  })
};

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
    category_arr: [], // 仅仅用于最后结束创建加入推荐列表，不用来进行通知(通知做防重处理)
    location: [],
    os_location: [],
    textArray: {
      text1: "重要证件号可只给头尾，*号替代中间部分！",
      text2: "重要身份证件照片可做部分打码处理！",
      text3: "真实姓名仅用于系统筛选，不会对外公开！",
    }
  },
  /**
   * 1、扫码发布(失物招领)
   * 2、归还发布(失物招领)
   * 3、常规发布(需选择)
   * @param options
   */
  onLoad: function (options) {
    let info = options.info;
    if (globalData.isScanQrcode) {
      //扫码归还
      this.setData({
        notify_id: globalData.qrcodeOpenid,  //用于归还帖的链接
        business_type: 2, //归还贴
        dataReady: true
      });
      this.setInitData()
    } else {
      if (info) {
        //寻物归还
        this.setData({
          info: JSON.parse(info),  //用于归还贴信息智能填充，以及归还贴与原寻物贴链接
          business_type: 2, //归还帖
          dataReady: true
        });
        this.setInitData()
      } else {
        //常规发布
        wx.showActionSheet({
          itemList: ['寻物启事', '失物招领'],
          success: res => {
            this.setData({
              business_type: res.tapIndex,
              dataReady: true
            });
            this.setInitData()
          },
          fail: (res) => {
            wx.navigateBack()
          }
        })
      }
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
   * 对不知道怎么操作直接输入位置的用户进行提示
   * @param e
   */
  toInputGetLocation: function (e) {
    let loc_id = e.currentTarget.dataset.loc * 1;
    if (this.data.os_location.length === 0 && loc_id === 2 || this.data.location.length === 0 && loc_id === 1) {
      let content;
      if (this.data.business_type === 0) {
        content = loc_id === 2 ? '不知道可留空': '可留空'
      } else if ((this.data.business_type === 1 || this.data.business_type === 2) && loc_id ===1) {
        content = '与发现地一样可留空'
      }
      app.alert({
        title: '请点击橙色按钮获取位置',
        content: content
      })
    }
  },
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
        let loc_auth = res.authSetting['scope.userLocation'];
        if (!loc_auth) {
          // 获取定位授权
          if (loc_auth === false) {
            wx.hideLoading();
            app.alert({
              title: '请求授权',
              content: '鲟回失物招领请求获取你的位置信息',
              cb_confirm: ()=>{
                wx.openSetting({
                  success: (res) => {
                    if (res.authSetting['scope.userLocation']) {
                      wx.showToast({
                        title: '授权成功',
                        success: (res) => {
                          setTimeout(()=>{this.chooseLocation(loc_id);}, 300)
                        }
                      });
                    } else {
                      app.alert({content: '授权失败，将无法成功发布信息'})
                    }
                  },
                  fail: (res) => {
                    app.alert({content: '授权失败，将无法成功发布信息'})
                  }
                })
              }
            });
          } else {
            wx.authorize({
              scope: 'scope.userLocation',
              success: (res)=> {
                this.chooseLocation(loc_id);
              },
              fail: (errMsg) => {
                app.alert({content: '授权失败，将无法成功发布信息'})
              },
              complete: (res)=> {
                wx.hideLoading()
              }
            })
          }
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
    if (loc_id === 1){
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
   * 上传的图片点击进入预览
   * @param e
   */
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
   * 上传图片
   * @param e
   */
  chooseLoadPics: function (e) {
    //选择图片
    wx.chooseImage({
      count: 8 - this.data.imglist.length,
      sizeType: ['compressed'],
      sourceType: ['album', 'camera'],
      success:  (res) => {
        let imglist = this.data.imglist;
        imglist = app.addImages(res.tempFiles, imglist);
        //显示
        this.setData({
          imglist: imglist,
          flush: false,
          pic_status: imglist.length < 9,
        });
      }
    })
  },
  /**
   * deleteImg 删除上传图片
   * @param e
   */
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
  /**
   * 必填信息的数据，后续判空用
   * @param items
   * @returns {*}
   */
  getEssentialData: function (items = []) {
    let data;
    let business_type = this.data.business_type;
    if (business_type === 1) {
      // 失物招领必须填写发现地点
      data = {
        os_location: this.data.os_location.length ? this.data.os_location[1] : "",  //
        goods_name: items[0].value,
        mobile: items[2].value,
        owner_name: items[1].value,
        summary: this.data.summary_value
      };
    } else if (business_type === 0) {
      // 寻物启事必须填写居住地点
      data = {
        // location: this.data.location.length ? this.data.location[1] : "",
        goods_name: items[0].value,
        mobile: items[2].value,
        owner_name: items[1].value,
        summary: this.data.summary_value
      };
    } else {
      // 归还寻物贴
      if (!globalData.isScanQrcode) {
        // 寻物归还所有必填
        data = {
          os_location: this.data.os_location.length ? this.data.os_location[1] : "",  //
          // location: this.data.location.length ? this.data.location[1] : "",
          goods_name: items[0].value,
          mobile: items[2].value,
          owner_name: items[1].value,
          summary: this.data.summary_value
        };
      } else {
        // 扫码发布可不填失主信息和
        data = {
          os_location: this.data.os_location.length ? this.data.os_location[1] : "",
          goods_name: items[0].value,
          mobile: items[1].value,
          summary: this.data.summary_value
        };
      }
    }
    return data;
  },
  /***
   * toRelease
   * 如果必填项为空，提示补上
   * 否则继续进行提交处理
   * @see handleRelease
   */
  toRelease: function () {
    //防止重复地点击
    this.setData({
      submitDisable: true
    });
    // 获得需要判空的数据
    let data = this.getEssentialData(this.data.items);
    // 必填项判空
    if (app.judgeEmpty(data, this.data.tips_obj)) {
      this.setData({
        submitDisable: false
      });
      return
    }
    // 图片列表判空
    if (this.data.imglist.length === 0) {
      app.alert({
        content: "至少要提交一张图片"
      });
      this.setData({
        submitDisable: false
      });
      return
    }
    let location = this.data.location;
    let business_type = this.data.business_type;
    if (location.length === 0 && (business_type === 1 || business_type ===2 && globalData.isScanQrcode)) {
      //失物招领发帖时，再三询问是否真的一致，确保信息正确
      this.confirmEmptiness(data)
    } else if (business_type === 2 && !globalData.isScanQrcode && (location.equals(this.data.info.location) || location.length === 0)){
      //是归还帖，并且放置位置和失主住址一样或者留空了
      this.confirmReturnPutLocUnchanged(data,  location.length !== 0)
    } else {
      this.continueToRelease(data);
    }
  },
  confirmReturnPutLocUnchanged: function (data) {
    this.confirmEmptiness(data, true);
  },
  confirmEmptiness: function(data, is_return=false) {
    app.alert({
      title: '发布提示',
      content: '放置地点是很重要的取物线索，确认放置地点' + (is_return ? '就是失主所在位置？' : '与发现地点一致？'),
      showCancel: true,
      cb_confirm: () => {
        //准备发布数据
        this.continueToRelease(data);
      },
      cb_cancel: () => {
        //滚动到事发地点位置
        setTimeout(() => {
          this.setData({
            submitDisable: false
          });
          util.goToPoint('#to-make-up-location')
        }, 200)
      }
    })
  },
  /**
   * 发布信息通过校验{@link toRelease}后继续发帖
   */
  continueToRelease: function(data={}){
    data['os_location'] = this.data.os_location;
    data['business_type'] = this.data.business_type;
    data['location'] = this.data.location;
    data['img_list'] = this.data.imglist;
    data['is_top'] = this.data.isTop ? 1 : 0;
    data['days'] = this.data.isTop ? this.data.top_days : 0;
    data['edit'] = 0; //标记是发布，匹配用
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
      this.releaseGoods(data)
    } else {
      //根据是否勾选置顶继续订阅和发布
      if (data['is_top'] === 1) {
        //询问置顶，置顶收费并继续，取消置顶则不收费继续
        this.confirmTopAndSubRelease(data)
      } else {
        //未置顶
        this.subscribeMsgAndRelease(data)
      }
    }
  },
  /**
   * confirmTopAndSubRelease
   * 询问置顶
   * 如果取消重置置顶开关和余额勾选框状态以及解禁提交按钮
   * 否则就根据勾选框情况进行收费
   * @see toTopCharge
   */
  confirmTopAndSubRelease: function(data){
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
    if (this.data.use_balance) {
      //支付并扣除余额再发布
      let pay_price = this.data.discount_price;
      topCharge(pay_price, ()=>{
        changeUserBalance(-this.data.balance, ()=>{
          this.subscribeMsgAndRelease(data)
        }, onFailContactTech)
      }, this)
    } else {
      //支付后发布
      let pay_price = this.data.top_price;
      topCharge(pay_price, ()=>{
        this.subscribeMsgAndRelease(data)
      }, this)
    }
  },
  /**
   * subscribeMsgAndRelease
   * 先让用户订阅消息后，再继续通知失主和发布物品贴
   * @param data
   * @see getSubscribeTmpIds
   */
  subscribeMsgAndRelease: function (data) {
    wx.requestSubscribeMessage({
      tmplIds: getSubscribeTmpIds(this.data.business_type),
      complete: (res) => {
        this.releaseGoods(data)
      }
    })
  },
  /**
   * releaseGoods
   * 继续发布物品
   * @param data 发布数据
   * @see uploadData
   */
  releaseGoods: function(data){
    //上传数据
    this.uploadData(data)
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
          });
          this.setData({
            submitDisable: false
          });
          return
        }
        //获取商品的id,之后用于提交图片
        this.uploadImage(resp['data']['id'], data['img_list'], resp['data']['img_list_status']);
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
    });
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
    let info = this.data.info;
    let notify_id = this.data.notify_id;
    let data;
    if (info) {
      //寻物归还
      data = {
        id: id,
        target_goods_id: this.data.info.id
      }
    } else if (notify_id) {
      //扫码归还
      data = {
        id: id,
        notify_id: notify_id  //归还的对象
      }
    } else {
      //单纯发布失物招领和寻物启事
      data = {
        id: id,
        business_type: this.data.business_type
      }
    }
    this.endCreate(data)
  },
  /**
   * @name releaseEndCreate
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
          app.alert({'content': resp['msg']});
          this.setData({
            submitDisable: false
          });
          return
        }
        //初始化表单数据
        this.setFormInitData();
        //用户提示
        this.endCreateSuccess();
      },
      fail:  (res) => {
        app.serverBusy();
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
   * endCreateSuccess 创建成功后需要提示信息和跳转
   * @link endCreate
   */
  endCreateSuccess: function(){
    let msg;
    let navigate;
    if(this.data.business_type!==2){
      //非归还帖
      msg = "提交成功";
      navigate = ()=>{wx.redirectTo({
        url: '../../Find/Find?business_type='+ this.data.business_type,
      })}
    } else {
      //归还帖
      if(this.data.info){
        //寻物归还
        msg = "归还成功";
        navigate = wx.navigateBack
      } else {
        //扫码归还
        msg = "扫码归还成功";
        navigate = () => {
          wx.redirectTo({
            url: '/pages/Mine/Mine'
          })
        }
      }
    }
    this.showEndCreateToast(msg, navigate)
  },
  /**
   * showEndCreateToast 通用的显示提示和跳转代码结构
   * @link releaseEndCreate
   * @param msg
   * @param navigate
   */
  showEndCreateToast: function(msg = "", navigate=()=>{}){
    wx.showToast({
      title: msg,
      icon: 'success',
      duration: 1000,
      success: res => {
        setTimeout(navigate, 800)
      }
    });
  },
  /**
   * 初始化页面表单{@see setFormInitData}和置顶组件数据{@see setTopAndBalanceUseInitData}
   */
  setInitData: function () {
    //发布信息表单数据初始化
    this.setFormInitData();
    //寻物启事需要的置顶信息
    if (!this.data.business_type) {
      this.setTopAndBalanceUseInitData()
    }
  },
  /**
   * setFormInitData 在初始化页面数据{@link setInitData}时，置空表单数据
   */
  setFormInitData() {
    // 输入框，地址选择，图片上传框数据
    let info = this.data.info;  //如果因点击归还寻物而进入发布页，info就是原寻物启事的表单数据(用于初始化发布页表单)，否则是undefined
    let business_type = this.data.business_type;
    //发布前data内需要判空的属性，对应属性缺失时，向用户显示的属性的提示语。比如data的category为空，就弹出提示“物品类别为空”
    let tips_obj = {
      "goods_name": "物品名称",
      "owner_name": business_type ? "失主姓名" : "姓名",
      "os_location": business_type ? "发现位置" : "丢失位置",
      "location": business_type ? "物品放置位置" : "居住地址",
      "summary": "描述",
      "mobile": "联系电话"
    };
    //发布页面输入信息项的初始化（输入框占位符，输入默认值，输入框代表什么含义，icon等）
    let items = [{
      name: "goods_name",
      placeholder: "例:校园卡",
      kb_type: 'text',
      label: tips_obj['goods_name'],
      icons: "/images/icons/goods_name.png",
      value: business_type === 2  && info ? info.goods_name : "",  //归还帖自动填充归还的物品名
    }, {
      name: "owner_name",
      // hints: business_type === 0? '您失物上附有的姓名，用于筛选推荐和拾者归还': '物品上附有的物主身份信息，方便失主寻物',
      placeholder: "例:可可" + (business_type===1?'，若没有请填无。': '') ,
      kb_type: 'text',
      label: business_type ? "失主姓名": "姓名",
      icons: "/images/icons/discount_price.png",
      value: business_type === 2 && info ? info.owner_name : "" //归还帖自动填充归还物品的失主名
    },
      {
        name: "mobile",
        placeholder: business_type !== 0? "寄放处电话": "高危可填无",
        kb_type: 'text',
        // hints: business_type !== 0? '寄放处的办公电话。否则可填客服号，代理致电您注册手机。': '谨防诈骗和骚扰电话。可留客服号，代理致电您注册手机。',
        value: "",
        label: "电话",
        icons: "/images/icons/mobile.png"
      }
    ];
    if (globalData.isScanQrcode) {
      //如果是扫码不需要失主姓名，后台自动填充
      items.splice(1, 1);
      delete tips_obj.owner_name
    }
    let summary_placeholder = "";
    //表单
    if (business_type) {
      summary_placeholder = "添加拾物描述：拾到物品的时间、地点以及物品上面的其他特征如颜色、记号等..."
    } else {
      summary_placeholder = "添加寻物描述：物品丢失大致时间、地点，记号等..."
    }
    this.setData({
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
      location: info && !info.location.equals(globalData.default_loc) ? info.location.slice() : [], //归还帖自动填充归还物品的放置地址(就近放置)
      os_location: info && !info.os_location.equals(globalData.default_loc)? info.os_location.slice(): [] //归还帖自动填充归还物品的发现地址
    })
  },
  // copyClientMobile: function(e){
  //   let idx = e.currentTarget.dataset.id;
  //   let items = this.data.items;
  //   if (!items[idx].value) {
  //     wx.setClipboardData({
  //       data: globalData.client_mobile,
  //       success: (res) => {
  //         wx.showToast({
  //           title: '客服号已复制',
  //           duration: 500
  //         })
  //       }
  //     })
  //   }
  // },
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
      if (total_balance >= this.data.top_price - 0.01) {
        //余额足够
        this.setData({
          discount_price: 0.01, //使用余额，支付0元
          balance: Math.max(this.data.top_price-0.01, 0) //可用于垫付的余额
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
    let idx = e.currentTarget.dataset.id;
    let items = this.data.items;
    items[idx].value = e.detail.value;
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
  }
})