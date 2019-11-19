//app.js
App({
  onLaunch: function () {
    // 展示本地存储能力
    var logs = wx.getStorageSync('logs') || []
    logs.unshift(Date.now())
    wx.setStorageSync('logs', logs)
    // 登录
    wx.login({
      success: res => {
        // 发送 res.code 到后台换取 openId, sessionKey, unionId
      }
    })
    // 获取用户信息
    wx.getSetting({
      success: res => {
        if (res.authSetting['scope.userInfo']) {
          // 已经授权，可以直接调用 getUserInfo 获取头像昵称，不会弹框
          wx.getUserInfo({
            success: res => {
              // 可以将 res 发送给后台解码出 unionId
              this.globalData.userInfo = res.userInfo

              // 由于 getUserInfo 是网络请求，可能会在 Page.onLoad 之后才返回
              // 所以此处加入 callback 以防止这种情况
              if (this.userInfoReadyCallback) {
                this.userInfoReadyCallback(res)
              }
            }
          })
        }
      }
    })
  },
  globalData: {
    userInfo: null,
    domain: "https://jmall.opencs.cn/api",
    objectArray: [{
      id: 0,
      name: '待认领'
    },
    {
      id: 1,
      name: '预认领'
    },
    {
      id: 2,
      name: '已认领'
    },
    ],
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
      showCancel: false,
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
  getRequestHeader: function () {
    return {
      'content-type': 'application/x-www-form-urlencoded',
      'Authorization': this.getCache("token")
    }
  },
  //切字符
  cutStr: function (items) {
    //截取前14个字当做概况
    for (var i in items) {
      var item = items[i];
      if (item.auther_name && item.auther_name.length > 6) {
        item.auther_name = item.auther_name.substring(0, 7) + "...";
      }
      if (item.location && item.location.length > 8) {
        item.location = item.location.substring(0, 8) + "...";
      }
      if (item.goods_name && item.goods_name.length > 8) {
        item.goods_name = item.goods_name.substring(0, 10) + "...";
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
  checkLogin: function () {
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
            that.globalData.regFlag = true;
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
  login: function (e) {
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
            that.alert({
              'content': '登录成功～'
            });
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