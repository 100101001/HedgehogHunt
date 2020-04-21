var app = getApp();
Page({
  data: {
    loadingMore: true,
    processing: false,
    block_list: [],
    p: 1,
    loadingHidden: true,
    feedback_cat: [
      {
        id: 0,
        name: '未申诉'
      },
      {
        id: 2,
        name: '申诉'
      }],
    statusId: 0,
  },
  onLoad: function (res) {
  },
  /**
   *
   * @param res
   */
  onShow: function (res) {
    this.setData({
      p: 1,
      block_list: [],
      loadingMore: true
    });
    this.getBlockMemberList();
  },
  /**
   * 上方申诉状态切换（用户被拉黑后申诉了）
   * @param e
   */
  statusTypeClick: function (e) {
    //选择一次分类时返回选中值
    this.setData({
      statusId: e.currentTarget.id * 1,
      p: 1,
      block_list: [],
      loadingMore: true
    });
    this.getBlockMemberList();
  },
  /**
   * 分页加载被拉黑了的用户，状态分为
   * @param e
   */
  getBlockMemberList: function (e) {
    if (!this.data.loadingMore) {
      return;
    }
    if (this.data.processing) {
      return;
    }
    this.setData({
      processing: true,
      loadingHidden: false
    });
    wx.request({
      url: app.buildUrl("/member/blocked/search"),
      header: app.getRequestHeader(),
      data: {
        p: this.data.p,
        status: this.data.statusId,
      },
      success: (res) => {
        let resp = res.data;
        if (resp['code'] !== 200) {
          app.alert({content: resp['msg']});
          return;
        }
        let block_list = resp['data']['list'];
        this.setData({
          block_list: this.data.block_list.concat(block_list),
          p: this.data.p + 1,
          processing: false,
          loadingHidden: true,
          loadingMore: resp['data']['has_more']
        });
      },
      fail: (res) => {
        app.serverBusy();
      },
      complete: (res) => {
        this.setData({
          loadingHidden: true
        });

      },
    })
  },
  /**
   * 恢复被拉黑的用户
   * @param e
   */
  toRestoreMember: function (e) {
    wx.request({
      url: app.buildUrl("/member/restore"),
      header: app.getRequestHeader(),
      data: {
        id: e.currentTarget.dataset.id
      },
      success: (res) => {
        wx.showToast({
          title: '恢复成功',
          content: '恢复用户成功！',
          duration: 2000
        });
        this.setData({
          p: 1,
          block_list: [],
          loadingMore: true
        });
        this.getBlockMemberList();
      },
      fail: (res) => {
        app.serverBusy()
      }
    })
  },
  /**
   * 触底加载
   * @param e
   */
  onReachBottom: function (e) {
    setTimeout(() => {
      this.setData({
        loadingHidden: true,
      });
      this.getBlockMemberList();
    }, 500)
  },
});