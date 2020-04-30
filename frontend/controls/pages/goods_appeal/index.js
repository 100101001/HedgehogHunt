const app = getApp();

Page({
  data: {
    appeal_status: [
      {
        id: 0,
        name: '待处理'
      },
      {
        id: 1,
        name: '已处理'
      }
    ],
    appeal_list: [],
    p: 1,
    status: 0,
    hiddenContact: true,
    hiddenStuffDetail: true,
    hiddenDeal: true,
    hiddenResult: true
  },
  onLoad: function (options) {
    this.getAppealRecord()
  },
  getAppealRecord: function(){
    if (this.data.processing) {
      return
    }
    this.setData({
      processing: true
    });
    wx.request({
      url: app.buildUrl('/goods/appeal/search'),
      header: app.getRequestHeader(),
      data: {
        p: this.data.p,
        status: this.data.status
      },
      success: (res)=>{
        let resp = res.data;
        if (resp['code'] !== 200) {
          app.alert({content: resp['msg']});
          return
        }
        let data = resp['data'];
        this.setData({
          appeal_list: this.data.appeal_list.concat(data['list']),
          p:this.data.p+1,
          has_more: data['has_more']
        })
      },
      fail: (res) => {
        app.serverBusy()
      },
      complete: (res) => {
        setTimeout(()=>{
          this.setData({processing: false})
        }, 500)
      }
    })
  },
  statusClick: function (e) {
    let new_status = e.currentTarget.id * 1;
    let old_status = this.data.status;
    this.setData({
      status: new_status
    });
    if(new_status !== old_status) {
      this.refresh()
    }
  },
  refresh: function() {
    this.setData({
      p: 1,
      appeal_list: []
    })
    this.getAppealRecord()
  },
  onReachBottom: function () {
    if(this.data.has_more) {
      setTimeout(this.getAppealRecord, 500)
    }
  },
  openContact: function (e) {
    let index = e.currentTarget.dataset.index;
    this.setData({
      hiddenContact: false,
      contact: this.data.appeal_list[index].contact
    })
  },
  closeContact: function (e) {
    this.setData({
      hiddenContact: true,
      contact: {}
    })
  },
  openStuffDetail: function (e) {
    let index = e.currentTarget.dataset.index;
    this.setData({
      hiddenStuffDetail: false,
      stuff: this.data.appeal_list[index].stuff,
      stuff_index: index
    })
  },
  closeStuffDetail: function () {
    this.setData({
      hiddenStuffDetail: true,
      stuff_index: -1,
      stuff: {}
    })
  },
  openDeal: function (e) {
    let index = e.currentTarget.dataset.index;
    this.setData({
      hiddenDeal: false,
      index: index
    })
  },
  closeDeal: function() {
    this.setData({
      form_info: "",
      hiddenDeal: true,
      index: -1  //已处理的
    })
  },
  doSetAppealDealt: function (index, url, result='') {
    wx.request({
      url: app.buildUrl(url),
      header: app.getRequestHeader(),
      data: {
        id: this.data.appeal_list[index].id,
        result: result  //设置已处理的处理结果
      },
      success: (res) => {
        let resp = res.data;
        if (resp['code'] !== 200) {
          app.alert({content: resp['msg']});
          return
        }
        this.closeDeal();
        let app_list = this.data.appeal_list;
        app_list.splice(index, 1);
        this.setData({
          appeal_list: app_list,
        });
      },
      fail: (res) => {
        app.serverBusy()
      }
    })
  },
  copyContact: function (e) {
    wx.setClipboardData({
      data: e.currentTarget.dataset.text,
      success: res => {
        wx.showToast({
          title: '手机号已复制'
        })
      }
    })
  },
  appealInput: function(e){
    this.setData({
      warn: e.detail.value.length >= 270,
      empty: e.detail.value.length ===0
    })
  },
  appealFocus: function(e){
    this.setData({
      focus: 1
    })
  },
  appealBlur: function(e){
    this.setData({
      focus: 0
    })
  },
  formSubmit: function (e) {
    let info = e.detail.value;
    if (info.result.length < 50) {
      app.alert({
        content: '字数过少，请详细描述'
      });
      return
    }
    app.alert({
      content: '操作不可逆，确认已解决并提交处理结果？',
      showCancel: true,
      cb_confirm: () => {
        this.doSetAppealDealt(this.data.index, '/goods/appeal/dealt', info.result);
      }
    });
  },
  deleteDealtAppeal: function (e) {
    app.alert({
      title: '删除确认',
      content: '操作不可逆，确认删除？',
      showCancel: true,
      cb_confirm: ()=>{
        this.doSetAppealDealt(e.currentTarget.dataset.index, '/goods/appeal/delete')
      }
    })
  },
  openResult: function (e) {
    this.setData({
      hiddenResult: false
    })
  },
  closeResult: function () {
    this.setData({
      hiddenResult: true
    })
  }
});