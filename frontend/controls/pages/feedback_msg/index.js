
const app = getApp();
Page({
  data: {
    loadingMore: true,
    processing: false,
    feedback_list: [],
    p: 1,
    loadingHidden: true,
    hiddenFeedbackDetail: true,
    read_ids: [],
    del_ids: [],
    only_unread: false,
    hiddenReadDetail: true
  },
  onLoad: function () {
    this.getFeedbackList();
  },
  onShow: function () {

  },
  getFeedbackList: function (e) {
    if (!this.data.loadingMore || this.data.processing) {
      return;
    }
    this.setData({
      processing: true,
      loadingHidden: false
    });
    wx.request({
      url: app.buildUrl("/feedback/search"),
      header: app.getRequestHeader(),
      data: {
        p: this.data.p
      },
      success:  (res) => {
        let resp = res.data;
        if (resp['code'] !== 200) {
            app.alert({content: resp['msg']});
            return
        }
        let feedback_list = resp['data']['list'];
        feedback_list = app.cutStr(feedback_list);
        this.setData({
          feedback_list: this.data.feedback_list.concat(feedback_list),
          p: this.data.p + 1,
          processing: false,
          loadingMore: resp['data']['has_more'],
          user_id: resp['data']['user_id'],
        });
      },
      fail:  (res) => {
        app.serverBusy();
      },
      complete:  (res) => {
        this.setData({
          loadingHidden: true
        });
      }
    })
  },
  onReachBottom: function () {
    setTimeout(() => {
      this.setData({
        loadingHidden: true,
      });
      this.getFeedbackList();
    }, 500)
  },
  /**
   * openFeedbackDetail 反馈详情
   */
  openFeedbackDetail: function (e) {
    let index = e.currentTarget.dataset.index;
    this.setData({
      hiddenFeedbackDetail: false,
      feedback: this.data.feedback_list[index]
    })
  },
  /**
   * closeFeedbackDetail 关闭反馈详情
   */
  closeFeedbackDetail: function () {
    this.setData({
      hiddenFeedbackDetail: true,
      feedback: {}
    })
  },
  /**
   * markRead 标记已读
   * @param e
   */
  markRead: function (e) {
    let index = e.currentTarget.dataset.index;
    let fb_list = this.data.feedback_list;
    fb_list[index].viewed = true;
    fb_list[index]['views'].push(this.data.user_id);
    this.setData({
      feedback_list: fb_list
    })
    this.data.read_ids.push(this.data.feedback_list[index].id);
  },
  onUnload: function () {
    this.setFeedbackStatus()
  },
  /**
   * setFeedbackRead 设置反馈已读
   */
  setFeedbackStatus: function () {
    let read_ids = this.data.read_ids;
    let del_ids = this.data.del_ids;
    if (read_ids.length === 0 && del_ids.length === 0){
      return
    }
    wx.request({
      url: app.buildUrl('/feedback/status/set'),
      header: app.getRequestHeader(),
      data: {
        read_ids: this.data.read_ids,
        del_ids: this.data.del_ids
      },
      fail: (res) => {
        app.serverBusy()
      }
    })
  },
  delFeedback: function (e) {
    let index = e.currentTarget.dataset.index;
    let fb_list = this.data.feedback_list;
    if(fb_list[index]['view_count'] < 2) {
      app.alert({title: '删除提示', content: '至少有两名管理员查阅后才能删除'})
      return
    }
    app.alert({
      title: '删除提示',
      content: '确认删除，其他管理员将无法查阅',
      showCancel: true,
      cb_confirm: ()=>{
        fb_list.splice(index, 1);
        this.setData({
          feedback_list: fb_list,
          del_ids: this.data.del_ids.push(this.data.feedback_list[index].id)
        })
      }
    })
  },
  /**
   * 查看大图
   * @param e
   */
  previewItemImage: function (e) {
    wx.previewImage({
      current: this.data.feedback['pics'][e.currentTarget.dataset.index], // 当前显示图片的http链接
      urls: this.data.feedback['pics'] // 需要预览的图片http链接列表
    })
  },
  openViewDetail: function(){
    this.setData({
      hiddenReadDetail: false
    })
  },
  closeViewDetail: function () {
    this.setData({
      hiddenReadDetail: true
    })
  },
  hideReadFeedback: function () {
    this.setData({
      only_unread: !this.data.only_unread
    })
  }
});