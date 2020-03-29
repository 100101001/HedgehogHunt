//app.js
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
    shopName: "闪寻-失物招领",
    //domain: "http://127.0.0.1:8999/api",
    //domain: "http://192.168.0.116:8999/api",
    domain: "https://ciwei.opencs.cn/api",
    static_file_domain: "https://ciwei.opencs.cn",
    //static_file_domain: "http://192.168.0.116:8999",
    member_status: 1, //用户状态
    op_status: 2,
    indexPage: null, //首页（扫码进入控制“逛一逛”按钮显示）
    isScanQrcode: false, //是否扫码进入
    qrcodeOpenid: "", //二维码用户ID
    unLoggedRelease: false, //扫码用户未注册仍继续发布
    unLoggedReleaseToken: null, //扫码用户未注册仍继续发布使用的用户token
    qrcodePrice: 2, //闪寻码的价格
    qrcodeProductId: 15, //闪寻码产品ID
    goodsTopPrice: 100, // 置顶发布价格
    goodsTopDays: 1, //置顶天数
    smsProductId: 16, //短信按量计费产品ID
    smsProductPrice: 1, //短信按量购买价格
    smsPkgProductId: 17, //短信包量产品ID
    smsPkgProductPrice: 5, //短信包量产品价格
    buyQrCodeFreeSmsTimes: 5, //购买二维码免费赠送的通知次数
    subscribe: {  //订阅消息的模板ID
      recommend: 'ecym_eXCQjpxYgG3ov95r6OrWernCO3QKqsN1qcx7Yc', //给寻物启事发帖者发送匹配通知
      finished: {
        found: '_dAjVN6DHEewP_z01WhKXlZ7xY9nfs_OEtVbnBC88MU',  //各失物招领发布者发送被取回的通知
        lost: 'bHZTF62ciS-03u8MmGe0cA7YMVHdGpwH-bY9wrmfDfY'  //给寻物启事发布者发送物品被归还通知
      },
      thanks: 'MxeBoTL5FcGb8DGtQtsoesFS5VmEd67KlRtMAQj8hoI'  //给失物招领发帖者发送答谢通知
    },
    business_type: { //失物招领与寻物启事的标记
      found: 1, //失物招领
      lost: 0 //寻物启事
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
    showHintQrcode: true //用户未关闭提示浮窗
  },
  onLaunch: function () {
    //获取后端二维码产品价格和产品ID
    wx.request({
      url: this.buildUrl('/special/info'),
      success: res => {
        let data = res.data
        this.globalData.qrcodePrice = data['qrcode'].price
        this.globalData.qrcodeProductId = data['qrcode'].id
        this.globalData.smsProductId = data['sms'].id
        this.globalData.smsProductPrice = data['sms'].price
        this.globalData.smsPkgProductId = data['sms_pkg'].id
        this.globalData.smsPkgProductPrice = data['sms_pkg'].price
        this.globalData.goodsTopPrice = data['top'].price
        this.globalData.goodsTopDays = data['top'].days
        this.globalData.buyQrCodeFreeSmsTimes = data['free_sms'].times
      }
    })
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
      })
      return false
    } else {
      return true
    }
  },
  /**
   *
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
            params.cb_confirm();
          }
        } else { //点击否
          if (params.hasOwnProperty('cb_cancel') && typeof (params.cb_cancel) == "function") {
            params.cb_cancel();
          }
        }
      }
    })
  },
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
  console: function (msg) {
    console.log(msg);
  },
  getRequestHeader: function (content_type = 0) {
    var that = this
    if (content_type === 0) {
      return {
        'content-type': 'application/x-www-form-urlencoded',
        'Authorization': that.getCache("token")
      }
    } else {
      return {
        'content-type': 'application/json',
        'Authorization': that.getCache("token")
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
   * getCache 异步设置缓存
   * @param key
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
   * 判断json对象中属性是否有空的
   * @param json_obj json对象
   * @param tips_obj 属性对应的用户显示map
   * @returns {boolean}
   */
  judgeEmpty: function (json_obj, tips_obj) {
    for (let key in json_obj) {
      if (json_obj[key].length === 0) {
        this.alert({
          content: tips_obj[key] + "不能为空"
        })
        return true
      }
    }
    return false
  },
  /**
   * 服务器忙提示
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
   * getNewRecommend
   * 向后台获取新收到的答谢和匹配推荐计数，类似新消息的图标会展示在导航栏
   */
  getNewRecommend: function () {
    wx.request({
      url: this.buildUrl('/member/get-new-recommend'),
      header: this.getRequestHeader(),
      method: 'GET',
      data: {},
      success: (res) => {
        let resp = res.data
        if (resp['code'] !== 200) {
          return;
        }
        let data = resp['data']
        this.globalData.total_new = data.total_new;
        this.globalData.recommend_new = data.recommend_new;
        this.globalData.thanks_new = data.thanks_new;
        this.globalData.recommend = data.recommend;
      }
    })
  },
  /**
   * checkLogin
   * 一打开小程序就会执行的登录函数(如果注册了缓存用户状态信息，否则什么都不做)
   * 根据小程序内登录标记regFlag和缓存的登录用户的认证信息token，进行防重
   */
  checkLogin: function () {
    //已登录就不再重复登录
    if (this.globalData.regFlag && this.getCache("token") != "") {
      //已登录
      if(this.globalData.isScanQrcode){
        //已登录用户扫码
        this.qrCodeNavigate()
      }
      return
    }
    this.doCheckLogin()
  },
  /***
   * doCheckLogin 前端登录向后台传递code，
   * 后台利用code在微信登录后获得用户的openid，判断openid对应的用户是否已经注册、如果已经注册了是否是管理员，以及是否有二维码等用户状态信息
   * 成功后，先缓存数据，再根据是否扫码进行页面跳转(扫码)或者成功登录提示(非扫码)
   */
  doCheckLogin: function(){
    wx.login({
      success: (res) => {
        let code = res.code
        if (!code) {
          //没有拿到登录用的code
          app.alert({content: '网络开小差了，请稍后再试'})
          return
        }
        //成功拿到code
        wx.request({
          url: this.buildUrl('/member/check-reg'),
          header: {
            'content-type': 'application/x-www-form-urlencoded'
          },
          method: 'POST',
          data: {
            code: code
          },
          success: (res) => {
            let resp = res.data
            if (resp['code'] !== 200) {
              //非注册用户
              if (resp['code'] == -2) {
                //缓存session-key和openid（用于注册）
                this.setCache("loginInfo", resp['data'])
              }
              if (this.globalData.isScanQrcode) {
                //未注册用户扫码
                this.qrCodeNavigate()
              }
              return
            }
            //成功获取用户状态信息，进行全局缓存
            this.onLoginSuccessSetData(res)
            if (this.globalData.isScanQrcode) {
              //已注册用户(扫码时未登录，刚登录)扫码
              this.qrCodeNavigate()
            } else {
              //登陆成功的用户提示
              this.onLoginSuccessShowToast('登录成功')
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
   * onLoginSuccessSetData
   * 在checkLogin成功获取到注册用户状态信息后，缓存到小程序的全局数据
   * @param res
   */
  onLoginSuccessSetData: function (res) {
    let data = res.data.data
    this.setCache("token", data.token)
    this.globalData.is_adm = data.is_adm
    this.globalData.is_user = data.is_user
    this.globalData.has_qrcode = data.has_qrcode
    this.globalData.member_status = data.member_status
    this.globalData.id = data.id
    this.globalData.openid = data.token.split("#")[0]
    this.globalData.regFlag = true
  },
  /**
   * onLoginSuccessShowToast
   * 在checkLogin成功获取到注册用户身份信息后，缓存到小程序的全局数据
   * @param content
   */
  onLoginSuccessShowToast: function (content, back_delta=1) {
    wx.showToast({
      title: content,
      icon: 'success',
      duration: 1500,
      success:  (res) => {
        if (getCurrentPages().length > 1) {
          setTimeout(function () {
            wx.navigateBack({delta: back_delta})
          }, 1000)
        }
      }
    })
  },
  /**
   * login
   * 解析出授权获取到的微信用户公开信息和手机号，可用于后台注册或者直接登录
   * 如果授权失败则返回
   * @param userInfo
   */
  login: function (userInfo) {
    if (this.globalData.regFlag && this.getCache('token') != '') {
      //已经登陆过
      wx.navigateBack() //回到授权登录之前的页面
    }
    if (!userInfo) {
      //授权失败
      this.alert({content: '登录失败，请再次登录～～'})
      return
    }
    this.doLoginOrReg(userInfo)
  },
  /**
   * doLoginOrReg
   * 真正用于向后台请求登录或注册的函数
   * @param userInfo 微信用户手机号和公开信息
   */
  doLoginOrReg: function(userInfo={}){
    wx.login({
      success:  (res) => {
        let code = res.code
        if (!code) {
          this.alert({content: '登录失败，请再次登录～～'})
          return
        }
        userInfo['code'] = code
        wx.request({
          url: this.buildUrl('/member/login'),
          header: this.getRequestHeader(),
          method: 'POST',
          data: userInfo,
          success:  (res) => {
            let resp = res.data
            if (resp['code'] != 200) {
              this.alert({content: resp['msg']})
              return
            }
            this.onLoginSuccessSetData(res)
            if (this.globalData.isScanQrcode) {
              //注册用户是扫码进入注册的，继续去发布
              wx.reLaunch({
                url: '/pages/Release/release/index'
              })
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
   * qrCodeNavigate
   * 根据扫码解析的二维码主OPENID和扫码者的OPENID（登录获取）判断是否是同一人
   * 如果是同一人，那么询问是绑定手机还是随便扫扫
   * 如果不是同一人
   * 如果扫码者未注册，那么询问注册，确认注册后跳转发布页面
   * 如果扫码者已注册，那么直接进行发布
   */
  qrCodeNavigate: function () {
    let openid = this.globalData.qrcodeOpenid
    if (openid == this.globalData.openid) {
      //自己扫码
      this.selfScanQrcode()
    } else {
      //别人扫码
      if (!this.globalData.regFlag) {
        //扫码用户未注册
        this.askToReg()
      } else{
        //扫码用户已注册
        wx.redirectTo({
          url: "/pages/Release/release/index"
        })
      }
    }
  },
  /**
   * selfScanQrcode
   * 自己扫码，选择绑定手机或者随便扫扫
   */
  selfScanQrcode: function () {
    let page = this.globalData.indexPage
    wx.showActionSheet({
      itemList: ['绑定手机号', '随便扫扫'],
      success: (res) => {
        if (res.tapIndex == 0) {
          //绑定手机号
          wx.redirectTo({
            url: "/pages/Qrcode/Mobile/index"
          })
        } else {
          //随便扫扫
          page.setData({
            isScanQrcode: false
          })
          this.globalData.isScanQrcode = false
          this.globalData.qrcodeOpenid = ""
        }
      },
      fail: (res) => {
        //取消
        page.setData({
          isScanQrcode: false
        })
        this.globalData.isScanQrcode = false
        this.globalData.qrcodeOpenid = ""
      }
    })
  },
  askToReg: function () {
    wx.showModal({
      title: '是否注册?',
      content: '注册用户可得失主的答谢金',
      success: res => {
        if (res.confirm) {
          //前往注册
          wx.navigateTo({
            url: '/pages/login/index',
          })
        } else if (res.cancel) {
          //前往发布
          this.globalData.unLoggedReleaseToken = {
            'content-type': 'application/x-www-form-urlencoded',
            'Authorization': 'opLxO5fubMUl7GdPFgZOUaDHUik8#100001'
          }
          this.globalData.unLoggedRelease = true
          wx.redirectTo({
            url: "/pages/Release/release/index?business_type=1&openid=" + openid
          })
        }
      }
    })
  }
})