// pages/jmall/my/controls/feedback_msg/index.js
var app=getApp();
Page({
  data: {
    loadingMoreHidden: true,
    processing: false,
    feedback_list:[],
      p:1,
    loadingHidden: true,
    feedback_cat: [
            {
                id: 1,
                name: '未读'
            },
            {
                id: 0,
                name: '已读'
            }],
    statusId:1,
  },
  onLoad:function(){
      this.getFeedbacksList();
  },
    onShow:function(){

  },
  toFeedBackDetail:function(e){
      var id=e.currentTarget.dataset.id;
    wx.navigateTo({
      url: '../feedback_msg/info?id='+id,
    })
  },
  statusTypeClick: function (e) {
        //选择一次分类时返回选中值
        this.setData({
            statusId: e.currentTarget.id,
            p: 1,
            feedback_list: [],
            loadingMoreHidden: true
        });
        this.getFeedbacksList();
    },
  getFeedbacksList: function (e) {
        var that = this;
        if (!that.data.loadingMoreHidden) {
            return;
        }
        if (that.data.processing) {
            return;
        }
        that.setData({
            processing: true,
            loadingHidden: false
        });
        wx.request({
            url: app.buildUrl("/feedback/search"),
            header: app.getRequestHeader(),
            data: {
                p: that.data.p,
                status: that.data.statusId,
            },
            success: function (res) {
                // var resp = res.data
                // if (resp.code !== 200) {
                //     app.alert({'content': resp.msg});
                //     return
                // }
                var feedback_list = resp.data.list;
                feedback_list = app.cutStr(feedback_list);
                that.setData({
                    feedback_list: that.data.feedback_list.concat(feedback_list),
                    p: that.data.p + 1,
                    processing: false,
                });
                if (resp.data.has_more === 0) {
                    that.setData({
                        loadingMoreHidden: false,
                    })
                }
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
  onReachBottom: function (e) {
        var that = this;
        //延时500ms处理函数
            setTimeout(function () {
            that.setData({
                hloadingHidden: true,
            });
            that.getFeedbacksList();
        }, 500)
    },
});