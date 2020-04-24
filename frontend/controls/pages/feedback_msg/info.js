// pages/jmall/my/controls/feedback_msg/info.js
var app=getApp();
Page({
  data: {
      loadingHidden:true
  },
  onLoad: function (options) {
    var id=options.id;
    this.getGoodsInfo(id);
  },
  getGoodsInfo: function (id) {
        var that = this;
        that.setData({
            loadingHidden:false
        });
        wx.request({
            url: app.buildUrl("/feedback/info"),
            header: app.getRequestHeader(),
            data: {
                id: id,
            },
            success: function (res) {
                var resp = res.data;
                // if (resp.code !== 200) {
                //     app.alert({'content': resp.msg});
                //     return;
                // }
                that.setData({
                    info: resp.data.info,
                    feedback_id:resp.data.info.feedback_id
                });
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
  toBlockMember: function (e) {
        //选择操作的用户id
      var that=this;
      that.setData({
          loadingHidden:false
      });
    var feedback_id=this.data.feedback_id;
        var select_member_id = this.data.info.member_id;
        wx.showModal({
            title: '操作提示',
            content: '确认拉黑？',
            success: function (res) {
                wx.request({
                    url: app.buildUrl("/feedback/more_record"),
                    header: app.getRequestHeader(),
                    data: {
                        select_member_id: select_member_id,
                      feedback_id:feedback_id
                    },
                    success: function (res) {
                        wx.hideLoading();
                        wx.showToast({title: '拉黑用户成功！', icon: 'success', duration: 2000});
                        wx.switchTab({
                            url: '../record/index',
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
                });
            }
        });
    },
  //预览图片
  previewImage: function (e) {
    var current = e.target.dataset.src;
    wx.previewImage({
      current: current, // 当前显示图片的http链接  
      urls: this.data.info.pics,
    })
  }, 
});