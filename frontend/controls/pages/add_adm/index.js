// pages/jmall/my/controls/add_adm/index.js
var app = getApp();
Page({
  data: {
    show_user: true,
    loadingHidden: true
  },
  onLoad: function (options) {
    this.getUserList();
    var is_adm = app.globalData.is_adm;
  },
  onShow: function () {
    this.getUserList();
  },
  deleteUser: function (e) {
    var that = this;
    that.setData({
      loadingHidden: false
    });
    var uid = e.currentTarget.dataset.id;
    wx.request({
      url: app.buildUrl("/user/delete"),
      method: 'POST',
      header: app.getRequestHeader(),
      data: {'uid': uid},
      success: function (res) {
        var resp = res.data;
        if (resp.code != 200) {
          app.alert({'content': resp.msg});
          return
        }
        app.alert({'content': resp.msg});
        that.getUserList();
      },
      fail: function (res) {
        app.serverBusy();
        return;
      },
      complete: function (res) {
        that.setData({
          loadingHidden: true
        });
      },
    })
  },
  restoreUser: function (e) {
    var that = this;
    that.setData({
      loadingHidden: false
    });
    var uid = e.currentTarget.dataset.id;
    wx.request({
      url: app.buildUrl("/user/restore"),
      method: 'POST',
      header: app.getRequestHeader(),
      data: {'uid': uid},
      success: function (res) {
        var resp = res.data;
        if (resp.code != 200) {
          app.alert({'content': resp.msg});
          return
        }
        app.alert({'content': resp.msg});
        that.getUserList();
      },
      fail: function (res) {
        app.serverBusy();
        return;
      },
      complete: function (res) {
        that.setData({
          loadingHidden: true
        });
      },
    })
  },
  formSubmit: function (e) {
    let user_info = e.detail.value;
    if (user_info.name.length === 0 || user_info.level.length === 0 || user_info.mobile.length === 0 || user_info.name.length === 0) {
      app.alert({content: "任何字段都不能为空"});
    } else {
      this.setData({
        loadingHidden: false
      });
      wx.request({
        url: app.buildUrl("/user/register"),
        method: 'POST',
        header: app.getRequestHeader(),
        data: user_info,
        success:  (res) => {
          let resp = res.data;
          app.alert({content: resp['msg']});
          if (resp['code'] === 200) {
            this.formReset();
            this.getUserList();
          }
        },
        fail:  (res) => {
          app.serverBusy();
        },
        complete:  (res) => {
          this.setData({
            loadingHidden: true
          });
        },
      })
    }
  },
  formReset: function () {
    console.log('form发生了reset事件')
  },
  changeShowUser: function () {
    var show_user = !this.data.show_user;
    this.setData({
      show_user: show_user,
    })
  },
  getUserList: function () {
    var that = this;
    that.setData({
      loadingHidden: false
    });
    wx.request({
      url: app.buildUrl("/user/get-user"),
      header: app.getRequestHeader(),
      success: function (res) {
        var resp = res.data;
        if (resp.code != 200) {
          app.alert({'content': resp.msg});
          return
        }
        that.setData({
          user_list: resp['user_list']
        })
      },
      fail: function (res) {
        app.serverBusy();
        return;
      },
      complete: function (res) {
        that.setData({
          loadingHidden: true
        });

      },
    })
  }
});
