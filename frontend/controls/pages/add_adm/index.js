// /controls/pages/add_adm/index.js
const app = getApp();
Page({
  data: {
    show_user: true,
    loadingHidden: true,
    hiddenContact: true,  //联络方式
    hiddenAddUser: true   //新增管理员
  },
  onLoad: function (options) {
  },
  onShow: function () {
    this.getUserList();
  },
  toDeleteUser: function(e){
    app.alert({
      content: '确定删除？',
      showCancel: true,
      cb_confirm: ()=>{
        this.doOpOnUser("/user/delete", e.currentTarget.dataset.id)
      }
    })
  },
  toRestoreUser: function(e){
    app.alert({
      content: '确定恢复？',
      showCancel: true,
      cb_confirm: ()=>{
        this.doOpOnUser("/user/restore", e.currentTarget.dataset.id)
      }
    })
  },
  /**
   * 删除或者恢复管理员
   * @param url
   * @param mid
   */
  doOpOnUser: function(url="/user/delete", mid=0){
    this.setData({
      loadingHidden: false
    });
    wx.request({
      url: app.buildUrl(url),
      method: 'POST',
      header: app.getRequestHeader(),
      data: {'id': mid},
      success:  (res) => {
        let resp = res.data;
        app.alert({content: resp['msg']});
        if (resp['code'] !== 200) {
          return
        }
        this.getUserList();
      },
      fail:  (res) => {
        app.serverBusy();
      },
      complete:  (res) =>{
        this.setData({
          loadingHidden: true
        });
      },
    })
  },
  /**
   * 打开新增管理员
   */
  openAddUser: function () {
    this.setData({
      hiddenAddUser: false
    })
  },
  /**
   * 关闭新增管理员
   */
  closeAddUser: function () {
    this.setData({
      hiddenAddUser: true,
      form_info: ''
    })
  },
  /**
   * 新增管理员的表单
   * @param e
   */
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
            this.closeAddUser();
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
  /**
   * 获取当前系统的所有的管理员
   */
  getUserList: function () {
    this.setData({
      loadingHidden: false
    });
    wx.request({
      url: app.buildUrl("/user/all"),
      header: app.getRequestHeader(),
      success:  (res) => {
        let resp = res.data;
        if (resp['code'] !== 200) {
          app.alert({content: resp['msg']});
          return
        }
        this.setData({
          user_list: resp['user_list']
        })
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
  },
  /**
   * 打开联络的模态框
   * @param e
   */
  openContact: function (e) {
    let dataset = e.currentTarget.dataset;
    this.setData({
      hiddenContact: false,
      mobile: dataset.mobile,
      email: dataset.email
    })
  },
  /**
   * 打开联络的模态框后点击复制手机号和邮箱
   * @param e
   */
  copyContact: function (e) {
    let id = e.currentTarget.dataset.id * 1;
    wx.setClipboardData({
      data: e.currentTarget.dataset.text,
      success: res => {
        wx.showToast({
          title: (id? '邮箱地址':'手机号') +'已复制',
        })
      }
    })
  },
  /**
   * 关闭联络的模态框
   */
  closeContact: function () {
    this.setData({
      hiddenContact: true,
      mobile: "",
      email: ""
    })
  },


});
