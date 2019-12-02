//app.js
App({
  onLaunch: function() {},
  globalData: {
    info: {},
    business_type: 1,
    check_report: false,
    is_adm: false,
    is_user: false,
    has_qrcode: false,
    qr_code_list: [],
    location: '',
    has_info: false,
    userInfo: null,
    version: "1.0",
    regFlag:false,
    shopName: "同济大学闲置交易平台",
    // domain: "http://0.0.0.0:8999/api",
    //domain: "http://192.168.31.66:8999/api",
    //domain: "http://100.68.70.139:8999/api",
    domain: "https://jmall.changshunlive.com:8999/api",
    objectArray: [{
        id: 0,
        name: '同济周边'
      },
      {
        id: 1,
        name: '电子数码'
      },
      {
        id: 2,
        name: '运动户外'
      },
      {
        id: 3,
        name: '书籍资料'
      },
      {
        id: 4,
        name: '个护美妆'
      },
      {
        id: 5,
        name: '交通工具'
      },
      {
        id: 6,
        name: '衣服鞋帽',
      },
      {
        id: 7,
        name: '生活电器',
      },
      {
        id: 9,
        name: '学习用品'
      },
      {
        id: 8,
        name: '其他闲置'
      }
    ],
  },
  tip: function(params) {
    var that = this;
    var title = params.hasOwnProperty('title') ? params['title'] : '提示信息';
    var content = params.hasOwnProperty('content') ? params['content'] : '';
    wx.showModal({
      title: title,
      content: content,
      success: function(res) {

        if (res.confirm) { //点击确定
          if (params.hasOwnProperty('cb_confirm') && typeof(params.cb_confirm) == "function") {
            params.cb_confirm();
          }
        } else { //点击否
          if (params.hasOwnProperty('cb_cancel') && typeof(params.cb_cancel) == "function") {
            params.cb_cancel();
          }
        }
      }
    })
  },
  alert: function(params) {
    var title = params.hasOwnProperty('title') ? params['title'] : '提示信息';
    var content = params.hasOwnProperty('content') ? params['content'] : '';
    wx.showModal({
      title: title,
      content: content,
      showCancel: false,
      success: function(res) {
        if (res.confirm) { //用户点击确定
          if (params.hasOwnProperty('cb_confirm') && typeof(params.cb_confirm) == "function") {
            params.cb_confirm();
          }
        } else {
          if (params.hasOwnProperty('cb_cancel') && typeof(params.cb_cancel) == "function") {
            params.cb_cancel();
          }
        }
      }
    })
  },
  console: function(msg) {
    console.log(msg);
  },
  getRequestHeader: function() {
    return {
      'content-type': 'application/x-www-form-urlencoded',
      'Authorization': this.getCache("token")
    }
  },
  //切字符
  cutStr: function(items) {
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
  buildUrl: function(path, params) {
    var url = this.globalData.domain + path;
    var _paramUrl = "";
    if (params) {

      //循环params里面的变量，取key为变量k，然后将k与其对应的值用等号链接起来
      //如果params={a:'b',c:'d'}
      //拼接结果的格式如a=b&c=d,GET方法都是使用‘=’来区分的
      _paramUrl = Object.keys(params).map(function(k) {
        return [encodeURIComponent(k), encodeURIComponent(params[k])].join("=");
      }).join("&");

      _paramUrl = "?" + _paramUrl
    }

    return url + _paramUrl;
  },
  getCache: function(key) {
    var value = undefined;
    try {
      value = wx.getStorageSync(key);
    } catch (e) {

    }
    return value;
  },
  setCache: function(key, value) {
    wx.setStorage({
      key: key,
      data: value
    });
  },
  getFilename: function(filepath) {
    // 为了避免转义反斜杠出问题，这里将对其进行转换
    var re = /(\\+)/g;
    var filename = filepath.replace(re, "#");
    var fileArray = filename.split("#");
    var fileName = fileArray[fileArray.length - 1];
    return fileName;
  },
  addImages: function(ori_img_list, img_list) {
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
  judgeEmpty: function(json_obj, tips_obj) {
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
  serverBusy: function() {
    this.alert({
      'content': '服务器响应超时，请稍后重试'
    });
    return;
  },
  checkLogin: function() {
    var that = this;
    wx.login({
      success: function(res) {
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
          success: function(res) {
            if (res.data.code !== 200) {
              return;
            }
            that.setCache("token", res.data.data.token);
            that.globalData.is_adm = res.data.data.is_adm;
            that.globalData.is_user = res.data.data.is_user;
            that.globalData.has_qrcode = res.data.data.has_qrcode;
            that.globalData.qr_code_list = res.data.data.qr_code_list;
            that.globalData.location = res.data.data.location;
            that.globalData.regFlag=true;
          },
          fail: function(res) {
            that.serverBusy();
            return;
          },
          complete: function(res) {},
        });
      }
    });
  },
  login: function(e) {
    var that = this;
    if (!e.detail.userInfo) {
      that.alert({
        'content': '登录失败，请再次登录～～'
      });
      return;
    }
    var data = e.detail.userInfo;
    wx.login({
      success: function(res) {
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
          success: function(res) {
            if (res.data.code != 200) {
              that.alert({
                'content': res.data.msg
              });
              return;
            }
            that.setCache("token", res.data.data.token);
            that.checkLogin();
            that.alert({
              'content': '登陆成功～'
            });
          },
          fail: function(res) {
            that.serverBusy();
            return;
          },
          complete: function(res) {},
        });
      }
    });
  }
});