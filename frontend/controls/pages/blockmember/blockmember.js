var app = getApp();
Page({
    data: {
        loadingMoreHidden: true,
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
        this.getBlockList();
    },
    onShow: function (res) {
        this.setData({
            p: 1,
            block_list: [],
            loadingMoreHidden: true
        });
        this.getBlockList();
    },
    statusTypeClick: function (e) {
        //选择一次分类时返回选中值
        this.setData({
            statusId: e.currentTarget.id,
            p: 1,
            block_list: [],
            loadingMoreHidden: true
        });
        this.getBlockList();
    },
    getBlockList: function (e) {
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
            url: app.buildUrl("/member/block-search"),
            header: app.getRequestHeader(),
            data: {
                p: that.data.p,
                status: that.data.statusId,
            },
            success: function (res) {
                var resp = res.data;
                if (resp.code !== 200) {
                    app.alert({'content': resp.msg});
                    return
                }
                var block_list = resp.data.list;
                that.setData({
                    block_list: that.data.block_list.concat(block_list),
                    p: that.data.p + 1,
                    processing: false,
                    loadingHidden: true
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
    toRestoreMember: function (e) {
        var that = this;
        var id = e.currentTarget.dataset.id;
        wx.request({
            url: app.buildUrl("/member/restore-member"),
            header: app.getRequestHeader(),
            data: {
                id: id
            },
            success: function (res) {
                wx.showToast({
                    title: '恢复成功',
                    content: '恢复用户成功！',
                    duration: 2000
                });
                that.setData({
                    statusId: e.currentTarget.id,
                    p: 1,
                    block_list: [],
                    loadingMoreHidden: true
                });
                that.getBlockList();
            }
        })

    },
    onReachBottom: function (e) {
        var that = this;
        //延时500ms处理函数
        setTimeout(function () {
            that.setData({
                hloadingHidden: true,
            });
            that.getBlockList();
        }, 500)
    },
});