const app = getApp();

Page({
  data: {
    log_id: 0,
    p: 1,
    user_op_list: [],
    hiddenAppeal: true,
    hiddenStuffDetail: true,
    hiddenReason: true,
    warn: false,
    focus: false,
    stuff_type: 1,
    stuff_types: [
      {
        id: 1,
        name: '物品'
      },
      {
        id: 0,
        name: '答谢'
      }
    ]
  },
  onLoad: function (options) {
    let op_status = options.op_status *1;
    let id = options.id * 1;
    this.setData({
      op_status: op_status,  //管理员恢复账户前进入查看2，还是用户申诉进入查看1
      id: id  //会员id
    });
    this.getMemberBlockedRecords()
  },
  refresh: function(){
    this.setData({
      p: 1,
      user_op_list: []
    });
    this.getMemberBlockedRecords()
  },
  getMemberBlockedRecords: function(){
    if (this.data.processing) {
      return
    }
    this.setData({
      processing: true
    });
    wx.request({
      url: app.buildUrl('/member/blocked/record'),
      header: app.getRequestHeader(),
      data: {
        id: this.data.id,  //会员ID
        stuff_type: this.data.stuff_type //拉黑类型
      },
      success: (res) => {
        let resp = res.data;
        if (resp['code']!==200) {
          app.alert({content: resp['msg']});
          return;
        }
        //一般不需要分页
        this.setData({
          user_op_list: this.data.user_op_list.concat(resp['data']['list']),
          p: this.data.p + 1,
          has_more: resp['data']['has_more']
        })
      },
      fail: (res)=>{
        app.serverBusy()
      },
      complete: (res) => {
        this.setData({
          processing: true
        });
      }
    })
  },
  stuffTypeClick: function(e){
    let new_type = e.currentTarget.id * 1;
    let old_type = this.data.stuff_type;
    this.setData({
      stuff_type: new_type,
    });
    if(new_type !== old_type) {
      this.refresh()
    }
  },
  appealInput: function(e){
    this.setData({
      warn: e.detail.value.length >= 130,
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
  /**
   * 点击申诉打开弹窗
   * @param e
   */
  openAppeal: function(e){
    let index = e.currentTarget.dataset.index;
    this.setData({
      hiddenAppeal: false,
      log_id: this.data.user_op_list[index].id,
      index: index
    })
  },
  closeAppeal: function(e){
    this.setData({
      hiddenAppeal: true,
      form_info: ""
    })
  },
  /**
   * 提交申诉理由，进行申请
   * @param e
   */
  formSubmit: function (e) {
    let appeal_info = e.detail.value;
    if (appeal_info.reason.length === 0) {
      app.alert({content: "理由不能为空"});
    } else {
      app.alert({
        title: '申诉提示',
        content: '只有一次申诉机会，确认提交？',
        showCancel: true,
        cb_confirm: ()=>{
          appeal_info['id'] = this.data.log_id;
          this.doAppealBlock(appeal_info)
        }
      });
    }
  },
  doAppealBlock: function(appeal_info={}){
    wx.showLoading({title:'提交中..', mask: true});
    wx.request({
      url: app.buildUrl("/member/blocked/appeal"),
      method: 'POST',
      header: app.getRequestHeader(),
      data: appeal_info,
      success:  (res) => {
        let resp = res.data;
        if (resp['code']!==200) {
          app.alert({content: resp['msg']});
          return;
        }
        //标记申诉过了
        let op_list = this.data.user_op_list;
        let index = this.data.index;
        op_list[index].status = 1;
        this.setData({
          user_op_list: op_list
        });
        //关闭申诉弹窗
        wx.showToast({
          title:'请耐心等待处理结果。',
          icon: 'success',
          duration: 800,
          success: (res) => {
            setTimeout(this.closeAppeal, 500)
          }
        })
      },
      fail:  (res) => {
        app.serverBusy();
      },
      complete:  (res) => {
        wx.hideLoading()
      },
    })
  },
  /**
   * toAcceptBlockAppeal 接受申诉
   * @param e
   */
  toAcceptBlockAppeal: function(e){
    let id = e.currentTarget.dataset.id;
    let index = e.currentTarget.dataset.index;
    app.alert({
      content: '操作不可逆，确定接受？',
      showCancel: true,
      cb_confirm: ()=>{
        this.doOpOnBlockAppeal(id, index, '/member/block/appeal/accept', 2)
      }
    })
  },
  /**
   * toDeleteBlockAppeal 驳回申诉
   * @param e
   */
  toTurnDownBlockAppeal: function (e) {
    let id = e.currentTarget.dataset.id;
    let index = e.currentTarget.dataset.index;
    app.alert({
      content: '操作不可逆，确定驳回？',
      showCancel: true,
      cb_confirm: ()=>{
        this.doOpOnBlockAppeal(id, index, '/member/block/appeal/reject', 3)
      }
    })
  },
  doOpOnBlockAppeal: function (id=0, index=0, url='', status=3) {
    wx.request({
      url: app.buildUrl(url),
      header: app.getRequestHeader(),
      data: {
        id: id
      },
      success: (res) => {
        let resp = res.data;
        if (resp['code'] !== 200) {
          app.alert({content: resp['msg']});
          return;
        }
        let op_list = this.data.user_op_list;
        op_list[index].status = status;
        this.setData({
          user_op_list: op_list
        });
        wx.showToast({title: '操作成功', duration: 800, mask: true})
      },
      fail: (res) => {
        app.serverBusy()
      }
    })
  },
  openStuffDetail: function (e){
    let index= e.currentTarget.dataset.index;
    let ele = this.data.user_op_list[index];
    this.setData({
      hiddenStuffDetail: false,
      stuff: ele.stuff,
      reason: ele['member_reason']
    })
  },
  closeStuffDetail: function (e) {
    this.setData({
      hiddenStuffDetail: true,
      stuff: {},
      reason: ''
    })
  },
  /**
   * 查看大图
   * @param e
   */
  previewItemImage: function (e) {
    wx.previewImage({
      current: this.data.goods['pics'][e.currentTarget.dataset.index], // 当前显示图片的http链接
      urls: this.data.goods['pics'] // 需要预览的图片http链接列表
    })
  },
  openReason: function (e) {
    this.setData({
      hiddenReason: false
    })
  },
  closeReason: function (e) {
    this.setData({
      hiddenReason: true
    })
  },
  onReachBottom: function () {
    if(this.data.has_more){
      setTimeout(this.getMemberBlockedRecords, 500)
    }
  }
});