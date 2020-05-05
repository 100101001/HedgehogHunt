//app.js

const BloomFilter = require('./utils/bloomfilter').BloomFilter;

/**
 * 在扫码引导前判断扫码合理性
 * @param qrcode_openid
 * @param that
 * @param cb_success
 */
const judgeScanFrequency = function (qrcode_openid="", that=undefined, cb_success=()=>{}) {
  wx.request({
    url: that.buildUrl('/qrcode/scan/freq'),
    header: that.getRequestHeader(),
    data: {
      openid: qrcode_openid
    },
    success: res => {
      let resp = res.data;
      if (resp['code'] !== 200) {
        that.alert({content: resp['msg']});
        that.cancelQrcodeScan();
        return;
      }
      cb_success(resp['data'])
    },
    fail: res => {
      that.serverBusy();
      that.cancelQrcodeScan();
    }
  })
};

App({
  globalData: {
    qrCodeDebug: false, //用于微信二维码获取无限个(false)的接口/有限个(true)的接口
    adv_info: {},
    info: {},
    is_adm: false,
    is_user: false, //唯一用于判断是否是管理员的标记
    has_qrcode: false, //唯一用于判定用户有无闪寻码的数据，只在新获取了闪寻码后被更新(勿删，首页浮窗显示的内容全靠这个变量)
    version: "1.0",
    id: null, //用户的id(首页goToIndex会用到)
    regFlag: false, //用于判断用户已注册(和缓存中的token一起代表用户已经登录)
    shopName: "鲟回-失物招领",
    domain: "http://192.168.0.116:8999/api",
    //domain: "https://ciwei.opencs.cn/api",
    //static_file_domain: "https://ciwei.opencs.cn",
    static_file_domain: "http://192.168.0.116:8999",
    member_status: 1, //用户状态
    op_status: 2,
    showHintQrcode: true, //导航栏上方的提示浮窗，标记是否显示浮窗，用户可关闭
    navigateUrls: [
      "/pages/Homepage/homepage",
      "/pages/Find/Find?business_type=1",
      "/pages/Release/release/index",
      "/pages/Find/Find?business_type=0",
      "/pages/Mine/Mine",
    ],
    indexPage: null, //首页（扫码进入控制“逛一逛”按钮显示）
    isScanQrcode: false, //是否扫码进入
    isFreqScanQrcode: false, //他人是否涉嫌频繁扫码
    qrcodeOpenid: "", //二维码用户ID
    qrcodeName: "", //二维码用户名字
    unLoggedRelease: false, //扫码用户未注册仍继续发布
    unLoggedReleaseToken: {}, //扫码用户未注册仍继续发布使用的用户token
    qrcodePrice: 2.5, //闪寻码的价格
    qrcodeProductId: 15, //闪寻码产品ID
    goodsTopPrice: 20, // 置顶发布价格
    goodsTopDays: 7, //置顶天数
    smsProductId: 16, //短信按量计费产品ID
    smsProductPrice: 1, //短信按量购买价格
    smsPkgProductId: 17, //短信包量产品ID
    smsPkgProductPrice: 5, //短信包量产品价格
    buyQrCodeFreeSmsTimes: 5, //购买二维码免费赠送的通知次数
    subscribe: {  //订阅消息的模板ID
      recommend: 'eT6wS62k3KzRNagqnZOd_Fuui0As0GBX7fYfpUSyi0Y', //给寻物启事发帖者发送匹配通知
      finished: {
        found: '_dAjVN6DHEewP_z01WhKXlZ7xY9nfs_OEtVbnBC88MU',  //向失物招领发布者发送被取回的通知
        return: '4JEcTuWKyXwYQM2kYbQoPkG8WBB52cKdsP9FxiSSqEY'  //归还者归还时订阅，如果对方确认或者取回了，发送
      },
      return: 'bHZTF62ciS-03u8MmGe0cA7YMVHdGpwH-bY9wrmfDfY', //给寻物启事发帖者，如果有人归还就通知
      thanks: 'MxeBoTL5FcGb8DGtQtsoesFS5VmEd67KlRtMAQj8hoI'  //给失物招领发帖者发送答谢通知
    },
    business_type: { //失物招领与寻物启事的标记
      found: 1, //失物招领
      lost: 0, //寻物启事
      return: 2 //扫码和寻物归还帖
    },
    kd100 :{   // 快递100的常数
      appId: "wx6885acbedba59c14",
      paths: {
        query: "pages/index/index?source=third_xcx",  //查询页面
        result: "pages/result/result?com=&querysource=third_xcx&nu="
      }
    },
    campus_id: -1, //学校id
    campus_name: "", //学校名
    read_goods: new BloomFilter(32*256, 16), //用户查阅过的物品ID，用于阅读量计数
    unRegUserInfo: {
      "has_qr_code": false,
      "avatar": "/images/more/un_reg_user.png",
      "nickname": "请登录",
      "level": 0
    }
  },
  onLaunch: function () {
    // 获取后端二维码产品价格和产品ID
    wx.request({
      url: this.buildUrl('/special/info'),
      success: res => {
        let data = res.data;
        this.globalData.qrcodePrice = data['qrcode'].price;
        this.globalData.qrcodeProductId = data['qrcode'].id;
        this.globalData.smsProductId = data['sms'].id;
        this.globalData.smsProductPrice = data['sms'].price;
        this.globalData.smsPkgProductId = data['sms_pkg'].id;
        this.globalData.smsPkgProductPrice = data['sms_pkg'].price;
        this.globalData.goodsTopPrice = data['top'].price;
        this.globalData.goodsTopDays = data['top'].days;
        this.globalData.buyQrCodeFreeSmsTimes = data['free_sms'].times;
      },
      fail: res => {
        this.serverBusy()
      }
    });
  },
  /**
   * loginTip 用户点击了需要登录的功能按键时进入该函数
   * 用户未登录时，函数会对外部调用的函数拦截，并导向登录页面
   * @returns {boolean}
   */
  loginTip: function () {
    //返回值：是否已登录过
    //操作：没登录过就登录，否则什么都不做。
    if (!this.globalData.regFlag || this.getCache("token") == "") {
      wx.showModal({
        title: '提示',
        content: '该功能需要授权登录！请授权登录',
        success(res) {
          if (res.confirm) {
            wx.navigateTo({
              url: '/pages/login/index',
            })
          } else if (res.cancel) { }
        }
      });
      return false
    } else {
      return true
    }
  },
  /**
   * tip 会弹出模态框，显示提示文字
   * @param params
   */
  tip: function (params) {
    var title = params.hasOwnProperty('title') ? params['title'] : '提示信息';
    var content = params.hasOwnProperty('content') ? params['content'] : '';
    wx.showModal({
      title: title,
      content: content,
      showCancel: params.showCancel == undefined ? false : params.showCancel,
      success: function (res) {
        if (res.confirm) { //点击确定
          if (params.hasOwnProperty('cb_confirm') && typeof (params.cb_confirm) == "function") {
            params.cb_confirm()
          }
        } else { //点击否
          if (params.hasOwnProperty('cb_cancel') && typeof (params.cb_cancel) == "function") {
            params.cb_cancel()
          }
        }
      }
    })
  },
  /**
   * tip 和tips类似会弹出模态框，显示提示文字
   * @param params
   */
  alert: function (params) {
    var title = params.hasOwnProperty('title') ? params['title'] : '提示信息';
    var content = params.hasOwnProperty('content') ? params['content'] : '';
    wx.showModal({
      title: title,
      content: content,
      showCancel: params.showCancel == undefined ? false : params.showCancel,
      success: function (res) {
        if (res.confirm) { //用户点击确定
          if (params.hasOwnProperty('cb_confirm') && typeof (params.cb_confirm) == "function") {
            params.cb_confirm();
          }
        } else {
          if (params.hasOwnProperty('cb_cancel') && typeof (params.cb_cancel) == "function") {
            params.cb_cancel();
          }
        }
      }
    })
  },
  getRequestHeader: function (content_type = 0) {
    if (content_type === 0) {
      return {
        'content-type': 'application/x-www-form-urlencoded',
        'Authorization': this.getCache("token")
      }
    } else {
      return {
        'content-type': 'application/json',
        'Authorization': this.getCache("token")
      }
    }
  },
  //切字符
  cutStr: function (items) {
    //截取前14个字当做概况
    for (var i in items) {
      var item = items[i];
      if (item.auther_name && item.auther_name.length > 16) {
        item.auther_name = item.auther_name.substring(0, 15) + "...";
      }
      if (item.owner_name && item.owner_name.length > 4) {
        item.owner_name = item.owner_name.substring(0, 4) + "...";
      }
      if (item.goods_name && item.goods_name.length > 6) {
        item.goods_name = item.goods_name.substring(0, 4) + "...";
      }
      if (item.summary && item.summary.length > 27) {
        item.summary = item.summary.substring(0, 27) + "...";
      }
      items[i] = item;
    }
    return items;
  },
  buildUrl: function (path, params) {
    let url = this.globalData.domain + path;
    let _paramUrl = "";
    if (params) {
      //循环params里面的变量，取key为变量k，然后将k与其对应的值用等号链接起来
      //如果params={a:'b',c:'d'}
      //拼接结果的格式如a=b&c=d,GET方法都是使用‘=’来区分的
      _paramUrl = Object.keys(params).map(function (k) {
        return [encodeURIComponent(k), encodeURIComponent(params[k])].join("=");
      }).join("&");
      _paramUrl = "?" + _paramUrl
    }
    return url + _paramUrl;
  },
  /**
   * getCache 同步获取缓存（非异步）
   * @param key
   */
  getCache: function (key) {
    let value = undefined;
    try {
      value = wx.getStorageSync(key);
    } catch (e) {

    }
    return value;
  },
  /**
   * setCache 异步设置缓存
   * @param key
   * @param value
   */
  setCache: function (key, value) {
    wx.setStorage({
      key: key,
      data: value
    })
  },
  getFilename: function (filepath) {
    // 为了避免转义反斜杠出问题，这里将对其进行转换
    let re = /(\\+)/g;
    let filename = filepath.replace(re, "#");
    let fileArray = filename.split("#");
    let fileName = fileArray[fileArray.length - 1];
    return fileName;
  },
  /**
   * addImages 根据文件名后缀判断文件是否是图片，将不是图片的文件筛出去，并提示用户
   * @param ori_img_list 原图片列表
   * @param img_list 筛选后的图片列表
   * @returns {*}
   */
  addImages: function (ori_img_list, img_list) {
    for (let i in ori_img_list) {
      let filepath = ori_img_list[i].path
      let fileName = this.getFilename(filepath);
      let suffixName = fileName.split(".");
      let ext = suffixName[suffixName.length - 1];
      let tp = "jpg,bmp,png,jpeg,JPG,PNG,BMP,JPEG";
      if (tp.indexOf(ext) >= 0) {
        img_list.push(filepath);
      } else {
        this.alert({
          content: "图片类型不在许可范围:" + tp
        })
        continue
      }
    }
    return img_list
  },
  /**
   * judgeEmpty 判断json对象中属性是否有空的
   * @param json_obj json对象
   * @param tips_obj 属性对应的用户显示map
   * @returns {boolean}
   */
  judgeEmpty: function (json_obj, tips_obj) {
    for (let key in json_obj) {
      if (json_obj[key]==undefined || json_obj[key] == null || json_obj[key].length === 0) {
        this.alert({
          content: tips_obj[key] + "不能为空"
        })
        return true
      }
    }
    return false
  },
  /**
   * serverBusy 服务器忙提示
   * @param cb_confirm 用户点击确定关闭提示框后的回调函数
   */
  serverBusy: function (cb_confirm=()=>{}) {
    this.alert({
      content: '服务器响应超时，请稍后重试',
      cb_confirm: cb_confirm
    })
  },
  serverInternalError: function () {
    this.alert({
      content: '服务器内部异常，请稍后重试'
    })
  },
  /**
   * getNewRecommend 更新新消息计数
   * 向后台获取新收到的答谢和匹配推荐计数，类似新消息的图标会展示在导航栏
   */
  getNewRecommend: function () {
    wx.request({
      url: this.buildUrl('/member/new/hint'),
      header: this.getRequestHeader(),
      method: 'GET',
      data: {},
      success: (res) => {
        let resp = res.data;
        if (resp['code'] !== 200) {
          return;
        }
        let data = resp['data'];
        this.globalData.total_new = data.total_new;
        this.globalData.recommend_new = data.recommend_new;
        this.globalData.thanks_new = data.thanks_new;
        this.globalData.recommend = data.recommend;
      }
    })
  },
  /**
   * Login 一打开小程序会执行的登录注册判定函数（注册过的用户就直接登录），用户可能通过扫码打开的小程序
   * 根据小程序内登录标记regFlag和缓存的登录用户的认证信息token，进行防重
   * @see doLogin 进行判定注册登录函数
   * @see qrCodeNavigate 扫码处理
   */
  login: function () {
    //已登录就不再重复登录
    // if (this.globalData.regFlag && this.getCache("token") != "") {
    //   //已登录
    //   util.checkMemberStatus()
    //   if(this.globalData.isScanQrcode){
    //     //已登录用户扫码
    //     this.qrCodeNavigate();
    //   } else {
    //     this.onLoginSuccessShowToast('已登录');
    //   }
    // }
    this.doLogin()
  },
  /***
   * doLogin 一打开小程序会执行的登录注册判定函数（注册过的用户就直接登录），用户可能通过扫码打开的小程序。
   * 发生任何请求失败，就置空扫码状态
   * 扫码打开的，进入下一步操作
   * @see login 调用者
   * @see cancelQrcodeScan 置空扫码状态
   * @see qrCodeNavigate 扫码处理
   */
  doLogin: function(){
    let isScanQrcode = this.globalData.isScanQrcode;
    wx.login({
      success: (res) => {
        let code = res.code;
        if (!code) {
          //没有拿到登录用的code
          this.alert({content: '网络开小差了，请稍后再试'});
          if (isScanQrcode) {
            //扫码失败
            this.cancelQrcodeScan()
          }
          return
        }
        //成功拿到code
        wx.request({
          url: this.buildUrl('/member/login'),
          header: {
            'content-type': 'application/x-www-form-urlencoded'
          },
          method: 'POST',
          data: {
            code: code
          },
          success: (res) => {
            let resp = res.data;
            if (resp['code'] === -2) {
              //未注册

              this.onLoginUnRegSetData(resp['data']);
              return
            }
            if (resp['code'] !== 200) {
              //其他情况
              this.alert({content: resp['msg']});
              return
            }
            //已注册，获取了用户数据，进行全局设置
            this.onLoginSuccessSetData(res);
            if (isScanQrcode) {
              //扫码，另行判断
              this.qrCodeNavigate()
            } else {
              //不扫码就提示一下登录了
              this.onLoginSuccessShowToast('登录成功')
            }
          },
          fail: (res) => {
            this.serverBusy();
            this.loginComplete();
            if (isScanQrcode) {
              this.cancelQrcodeScan();
            }
          }
        })
      },
      fail: res => {
        this.alert({content: '网络开小差了，请稍后再试'})
      }
    })
  },
  onLoginUnRegSetData: function(data) {
    this.globalData.openid = data.openid;
    this.globalData.session_key = data.session_key;
    // this.setCache("loginInfo", data);
    this.loginComplete();
    if (this.globalData.isScanQrcode) {
      //未注册用户扫码
      this.qrCodeNavigate()
    }
  },
  /**
   * 首次登录检查完用户状态，首页才显示逛一逛
   */
  loginComplete: function() {
    this.globalData.indexPage.setData({
      isLogging: false
    });
    if (!this.globalData.isScanQrcode) {
      this.globalData.indexPage = null;
    }
  },
  /**
   * onLoginSuccessSetData 用户注册or登录后设置全局数据
   * @param res 登录响应体
   * @see doLogin 调用者
   * @see doRegister 调用者
   */
  onLoginSuccessSetData: function (res) {
    let data = res.data.data;
    this.setCache("token", data.token);
    this.globalData.is_adm = data.is_adm;
    this.globalData.is_user = data.is_user;
    this.globalData.has_qrcode = data.has_qrcode;
    this.globalData.member_status = data.member_status;
    this.globalData.id = data.id;
    this.globalData.openid = data.openid;
    this.globalData.regFlag = true;
    this.loginComplete();
  },
  /**
   * onLoginSuccessShowToast 向非扫码登录的用户显示登陆成功的提示信息
   * 对于通过注册登录的用户，自动关闭注册页面
   * @param content
   * @param back_delta
   * @see doLogin 调用者
   * @see doRegister 调用者
   */
  onLoginSuccessShowToast: function (content, back_delta=1) {
    wx.showToast({
      title: content,
      icon: 'success',
      duration: 1500,
      success:  (res) => {
        let pages = getCurrentPages()
        //只有当登陆是发生在登录界面的时候才会回退
        if (pages.length > 1 && pages[pages.length-1].route=='pages/login/index') {
          setTimeout(function () {
            wx.navigateBack({delta: back_delta})
          }, 1000)
        }
      }
    })
  },
  /**
   * @name appRegister
   * register 新用户的注册入口函数
   * 如果微信用户信息授权失败则返回，
   * 否则继续调用 doRegister 进行注册
   * @param userInfo 用户授权获取到的微信用户公开信息和手机号，授权失败为空
   * @link registerHandler 调用者
   * @see doRegister 进行注册的函数
   */
  register: function (userInfo) {
    if (this.globalData.regFlag && this.getCache('token') != '') {
      //已经注册登录的
      wx.navigateBack({delta: 2}) //回到授权登录之前的页面
    }
    if (!userInfo) {
      //授权失败
      this.alert({content: '登录失败，请再次登录～～'})
      return
    }
    this.doRegister(userInfo)
  },
  /**
   * doRegister 向后台传入用户授权信息和code请求注册
   * 将注册成功返回的数据设置到全局变量中
   * 如果注册用户正在扫码，就继续扫码处理
   * @param userInfo 微信用户手机号和公开信息
   * @link appRegister 调用者
   * @see continueScanQrcodeAfterReg 注册后继续扫码
   * @see onLoginSuccessSetData 注册成功后设置数据
   * @see onLoginSuccessShowToast 注册成功后提示信息和页面导航
   */
  doRegister: function (userInfo = {}) {
    let isScanQrcode = this.globalData.isScanQrcode
    wx.login({
      success: (res) => {
        let code = res.code
        if (!code) {
          this.alert({content: '登录失败，请再次登录～～'})
          return
        }
        userInfo['code'] = code
        wx.request({
          url: this.buildUrl('/member/register'),
          header: this.getRequestHeader(),
          method: 'POST',
          data: userInfo,
          success: (res) => {
            let resp = res.data;
            if (resp['code'] !== 200) {
              this.alert({content: resp['msg']});
              return
            }
            this.onLoginSuccessSetData(res);
            if (isScanQrcode) {
              //注册用户是扫码进入注册的，继续去发布
              this.continueScanQrcodeAfterReg()
            } else {
              this.onLoginSuccessShowToast('登录成功', 2)
            }
          },
          fail: (res) => {
            this.serverBusy()
          }
        })
      }
    })
  },
  /**
   * cancelQrcodeScan 置空扫码状态
   * 除了用户主动的取消扫码，手机绑定页，发布失物信息页退出时都需要调用此方法
   * @link mobileUnload 调用者
   * @link releaseUnload 调用者
   * @link doLogin 调用者
   * @link toConfirmUnRegRelease 调用者
   * @link selfScanQrcode 调用者
   * @link otherScanQrcode 调用者
   */
  cancelQrcodeScan: function () {
    if (this.globalData.indexPage) {
      //显示首页的逛一逛按钮
      this.globalData.indexPage.setData({
        isScanQrcode: false
      });
      this.globalData.indexPage = null;
    }
    //标记清空
    this.globalData.isScanQrcode = false;
    this.globalData.isFreqScanQrcode = false;
    this.globalData.qrcodeOpenid = "";
    this.globalData.unLoggedRelease = false;
    this.globalData.unLoggedReleaseToken = {};
  },
  /**
   * qrcodeNotified 防止重复通知，通知一次后，就将通知对象置空
   * @link sendNotification 调用者
   */
  qrcodeNotified: function(){
    this.globalData.qrcodeOpenid = ""
  },
  /**
   * qrCodeNavigate
   * 根据扫码解析的二维码主OPENID和扫码者的OPENID判断是否是同一人
   * @link doLogin 调用者
   * @see judgeScanFrequency 判断扫码合理性
   * @see selfScanQrcode 自己扫码
   * @see otherScanQrcode 其他用户扫码
   */
  qrCodeNavigate: function () {
    let is_self_scan = this.globalData.qrcodeOpenid === this.globalData.openid;
    judgeScanFrequency(this.globalData.qrcodeOpenid, this, (data) => {
      if (data) {
        if (is_self_scan) {
          //自己扫码提示不能更换手机
          this.alert({
            title: '扫码提示',
            content: '您在' + data['phone_change_time'] + '更绑过手机，一个月内只能更换一次手机号！',
            cb_confirm: this.cancelQrcodeScan
          })
        } else {
          //别人扫码提示扫码归还是否重复
          this.globalData.isFreqScanQrcode = true;
          this.alert({
            title: '防恶意扫码提示',
            content: '贴有本二维码的' + data['goods_name'] + '在' + data['found_time'] + '被拾到后扫码归还！如果你归还的物品重复请取消，否则确定继续。',
            showCancel: true,
            cb_confirm: this.freqOtherScanQrcode, //必须注册，操作留痕
            cb_cancel: this.cancelQrcodeScan
          })
        }
      } else {
        //走原来的流程
        if (is_self_scan) {
          //自己扫码
          this.selfScanQrcode()
        } else {
          //别人扫码
          this.otherScanQrcode()
        }
      }
    });
  },
  /**
   * freqOtherScanQrcode 别人涉嫌频繁扫码
   * @see cancelQrcodeScan
   * @see regScanQrcode
   */
  freqOtherScanQrcode: function(){
    if (!this.globalData.regFlag) {
      //扫码用户未注册
      this.unRegFreqScanQrcode()
    } else {
      //扫码用户已注册
      this.regScanQrcode()
    }
  },
  /**
   * selfScanQrcode 自己扫码，选择绑定手机或者随便扫扫
   * @link qrCodeNavigate 调用者
   * @see cancelQrcodeScan
   */
  selfScanQrcode: function () {
    wx.showActionSheet({
      itemList: ['绑定手机号', '随便扫扫'],
      success: (res) => {
        if (res.tapIndex === 0) {
          //绑定手机号
          wx.navigateTo({
            url: "/pages/Qrcode/Mobile/index"
          })
        } else {
          //随便扫扫 == 取消扫码
          this.cancelQrcodeScan()
        }
      },
      fail: (res) => {
        //取消扫码
        this.cancelQrcodeScan()
      }
    })
  },
  /**
   * otherScanQrcode 处理别人扫码
   * @link qrCodeNavigate 调用者
   * @see unRegScanQrcode
   * @see regScanQrcode
   * @see cancelQrcodeScan
   */
  otherScanQrcode: function(){
    this.alert({
      title: '扫码提示',
      content: '填写拾物信息去通知失主获取答谢金',
      showCancel: true,
      cb_confirm: () => {
        if (!this.globalData.regFlag) {
          //扫码用户未注册
          this.unRegScanQrcode()
        } else {
          //扫码用户已注册
          this.regScanQrcode()
        }
      },
      cb_cancel: () => {
        //取消扫码发布信息
        this.cancelQrcodeScan()
      }
    })
  },
  /**
   * regScanQrcode 用户已注册，扫了别人的码，直接跳转发布页面去发布拾物信息
   * @link otherScanQrcode 调用者
   */
  regScanQrcode: function(){
    wx.navigateTo({
      url: "/pages/Release/release/index"
    })
  },
  /**
   * unRegScanQrcode 未注册者扫码
   * 可选择先注册再发布信息，也可直接发布
   * @link otherScanQrcode 调用者
   * @see toConfirmUnRegRelease 选择不注册
   */
  unRegScanQrcode: function () {
    this.alert({
      title: '是否注册?',
      content: '注册用户可得失主的答谢金',
      cb_confirm: ()=>{
        //前往注册
        wx.navigateTo({
          url: '/pages/login/index',
        })
      },
      cb_cancel: this.toConfirmUnRegRelease
    })
  },
  /**
   * unRegFreqScanQrcode 非注册用户涉嫌过度频繁扫码
   */
  unRegFreqScanQrcode: function () {
    this.alert({
      title: '注册提示',
      content: '您必须注册后才能继续扫码归还，确定继续，取消终止归还。',
      showCancel: true,
      cb_confirm: () => {
        wx.navigateTo({
          url: '/pages/login/index',
        })
      },
      cb_cancel: this.cancelQrcodeScan
    })
  },
  /**
   * toConfirmUnRegRelease 不注册发布
   * 除了选择不注册，选择注册但注册中途终止回退也会触发询问是否要不注册发布
   * @link registerUnload 调用者
   * @link unRegScanQrcode 调用者
   * @see cancelQrcodeScan
   */
  toConfirmUnRegRelease: function(){
    this.alert({
      title: '扫码提示',
      content: '继续发布拾物信息？',
      showCancel: true,
      cb_confirm: () => {
        //前往发布
        this.globalData.unLoggedReleaseToken = {
          'content-type': 'application/x-www-form-urlencoded',
          'Authorization': 'opLxO5fubMUl7GdPFgZOUaDHUik8#100001'
        }
        this.globalData.unLoggedRelease = true;
        wx.navigateTo({
          url: "/pages/Release/release/index"
        })
      },
      cb_cancel: () => {
        //终止扫码
        this.cancelQrcodeScan()
      }
    })
  },
  /**
   * continueScanQrcodeAfterReg 注册后继续扫码的处理
   * @link doRegister 调用者
   */
  continueScanQrcodeAfterReg: function () {
    wx.navigateBack({
      delta: 2,
      success: res => {
        wx.navigateTo({
          url: '/pages/Release/release/index'
        })
      }
    })
  },
  /**
   * getUserOpenId 未登录和登录用户的openid获取，实在获取不到就是空字符串
   * @returns {string|undefined|*}
   */
  getUserOpenId: function () {
    let openid = this.globalData.openid;
    if (openid) {
      return openid;
    } else {
      let token = this.getCache("token");
      if (token) {
        return token.split('#')[0];
      } else {
        let loginInfo = this.getCache("loginInfo");
        return loginInfo ? loginInfo.openid : "";
      }
    }
  },
  /**
   * getUserMemberId 获取用户会员ID
   * @returns {null|*}
   */
  getUserMemberId: function () {
    let id = this.globalData.id;
    if (id) {
      return id;
    } else {
      let token = this.getCache("token");
      return token ? token.split('#')[1] : "";
    }
  }
});