//app.js
App({
  globalData: {
    debug: true,
    adv_info: {},
    info: {},
    is_adm: false,
    is_user: false,
    has_qrcode: false,
    qr_code_list: [],
    location: '',
    has_info: false,
    userInfo: null,
    memberInfo: null,
    version: "1.0",
    regFlag: false,
    shopName: "刺猬寻物",
    // domain: "http://127.0.0.1:8999/api",
    domain: "http://192.168.0.116:8999/api",
    //domain: "http://192.168.1.12:8999/api",
    member_id: null,
    member_status: 1,
    is_adm: true,
    op_status: 2,
    subscribe: {
      recommend: 'zSCF_j0kTfRvPe8optyb5sx8F25S3Xc9yCvvObXFCh4',
      finished: 'Vx58nqU-cfi07bu4mslzCFhFyGTT52Xk4zlsrwC-MVA',
      thanks: 'gBSM-RF5b3L_PoT3f1u8ibxZMz-qzAsNSZy2LSBPsG8'
    },
    business_type: {
      found: 1,
      lost: 0
    },
    campus_id: -1, //学校id
    campus_name: "", //学校名
    showHintQrcode: true //用户未关闭提示浮窗
  },
  onLaunch: function () {
    // 展示本地存储能力
    var logs = wx.getStorageSync('logs') || []
    logs.unshift(Date.now())
    wx.setStorageSync('logs', logs)
    // 登录
    // wx.login({
    //   success: res => {
    //     // 发送 res.code 到后台换取 openId, sessionKey, unionId
    //   }
    // })
    // 获取用户信息
    var that = this
    wx.getSetting({
      success: res => {
        if (res.authSetting['scope.userInfo']) {
          // 已经授权，可以直接调用 getUserInfo 获取头像昵称，不会弹框
          wx.getUserInfo({
            success: res => {
              // 可以将 res 发送给后台解码出 unionId
              that.globalData.userInfo = res.userInfo
              // 由于 getUserInfo 是网络请求，可能会在 Page.onLoad 之后才返回
              // 所以此处加入 callback 以防止这种情况
              if (that.userInfoReadyCallback) {
                that.userInfoReadyCallback(res)
              }
            }
          })
        }
      }
    })
  },
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
      return false;
    } else {
      return true;
    }
  },
  tip: function (params) {
    var that = this;
    var title = params.hasOwnProperty('title') ? params['title'] : '提示信息';
    var content = params.hasOwnProperty('content') ? params['content'] : '';
    wx.showModal({
      title: title,
      content: content,
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
            params.cb_confirm(params.cb_confirm_param);
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
    var url = this.globalData.domain + path;
    var _paramUrl = "";
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
  getCache: function (key) {
    var value = undefined;
    try {
      value = wx.getStorageSync(key);
    } catch (e) {

    }
    return value;
  },
  setCache: function (key, value) {
    wx.setStorage({
      key: key,
      data: value
    });
  },
  getFilename: function (filepath) {
    // 为了避免转义反斜杠出问题，这里将对其进行转换
    var re = /(\\+)/g;
    var filename = filepath.replace(re, "#");
    var fileArray = filename.split("#");
    var fileName = fileArray[fileArray.length - 1];
    return fileName;
  },
  addImages: function (ori_img_list, img_list) {
    for (var i in ori_img_list) {
      var filepath = ori_img_list[i].path;
      var fileName = this.getFilename(filepath);
      var suffixName = fileName.split(".");
      var ext = suffixName[suffixName.length - 1];
      var tp = "jpg,bmp,png,jpeg,JPG,PNG,BMP,JPEG";
      var rs = tp.indexOf(ext);
      if (rs >= 0) {
        img_list.push(filepath);
      } else {
        this.alert({
          'content': "图片类型不在许可范围:" + tp
        });
        continue;
      }
    }
    return img_list;
  },
  //判断json对象中是否有空的字段
  judgeEmpty: function (json_obj, tips_obj) {
    for (var key in json_obj) {
      if (json_obj[key].length === 0) {
        this.alert({
          'content': tips_obj[key] + "不能为空"
        });
        return true;
      }
    }
    return false;
  },
  serverBusy: function () {
    this.alert({
      'content': '服务器响应超时，请稍后重试'
    });
    return;
  },
  serverInternalError: function () {
    this.alert({
      'content': '服务器内部异常，请稍后重试'
    });
    return;
  },
  getNewRecommend: function () {
    var that = this;
    wx.request({
      url: that.buildUrl('/member/get-new-recommend'),
      header: that.getRequestHeader(),
      method: 'GET',
      data: {},
      success: function (res) {
        if (res.data.code !== 200) {
          return;
        }
        that.globalData.total_new = res.data.data.total_new;
        that.globalData.recommend_new = res.data.data.recommend_new;
        that.globalData.thanks_new = res.data.data.thanks_new;
        that.globalData.recommend = res.data.data.recommend;
      }
    });
  },
  checkLogin: function (callback = undefined, qrcode_openid = undefined) {
    //已登录就不再重复登录
    if (this.globalData.regFlag && this.getCache("token") != "") {
      return
    }
    var that = this;
    wx.login({
      success: function (res) {
        if (!res.code) {
          app.alert({
            'content': '登录失败，请再点击～～'
          });
          return;
        }
        wx.request({
          url: that.buildUrl('/member/check-reg'),
          header: that.getRequestHeader(),
          method: 'POST',
          data: {
            code: res.code
          },
          success: function (res) {
            if (res.data.code !== 200) {
              return;
            }
            that.setCache("token", res.data.data.token);
            that.globalData.is_adm = res.data.data.is_adm;
            that.globalData.is_user = res.data.data.is_user;
            that.globalData.has_qrcode = res.data.data.has_qrcode;
            that.globalData.qr_code_list = res.data.data.qr_code_list;
            that.globalData.location = res.data.data.location;
            that.globalData.member_status = res.data.data.member_status;
            that.globalData.id = res.data.data.id;
            that.globalData.openid = res.data.data.token.split("#")[0]
            that.globalData.regFlag = true;
            that.globalData.memberInfo = res.data.data.member_info
            if (callback != undefined) {
              callback(qrcode_openid)
            } else {
              wx.showToast({
                title: '登录成功',
                icon: 'success',
                duration: 1500,
                success: function (res) {
                  var pages = getCurrentPages()
                  if (pages.length == 1) {
                    return
                  }
                  setTimeout(function () {
                    wx.navigateBack({})
                  }, 1000);
                }
              })
            }
          },
          fail: function (res) {
            that.serverBusy();
            return;
          },
          complete: function (res) { },
        });
      }
    });
  },
  login: function (e, callback = null) {
    var that = this;
    if (!e.detail.userInfo) {
      that.alert({
        'content': '登录失败，请再次登录～～'
      });
      return;
    }
    var data = e.detail.userInfo;
    wx.login({
      success: function (res) {
        if (!res.code) {
          that.alert({
            'content': '登录失败，请再次登录～～'
          });
          return;
        }
        data['code'] = res.code;
        //用wx.request方法来提交数据，类似于ajax
        wx.request({
          url: that.buildUrl('/member/login'),
          header: that.getRequestHeader(),
          method: 'POST',
          data: data,
          success: function (res) {
            if (res.data.code != 200) {
              that.alert({
                'content': res.data.msg
              });
              return;
            }
            that.setCache("token", res.data.data.token);
            that.checkLogin();
            // that.alert({
            //   'content': '登录成功,5秒后自动返回之前页面，欢迎继续使用～'
            // });
            // setTimeout(function () {
            //   wx.navigateBack({})
            // }, 5000);
          },
          fail: function (res) {
            that.serverBusy();
            return;
          },
          complete: function (res) { },
        });
      }
    });
  }
})