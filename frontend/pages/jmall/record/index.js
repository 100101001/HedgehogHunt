//index.js
var app = getApp();
Page({
    data: {
        goods_list: [],
        loadingHidden:true,
        loadingMoreHidden: true,
        p: 1,
        processing: false,
        statusId: 1,
        businessTypeId: 1,
        reportStatusId:3,
        business_cat: [
            {
                id: 1,
                name: '闲置'
            },
            {
                id: 0,
                name: '求购'
            }],

        status_cat: [
            {
                id: 1,
                name: '已上架'
            },
            {
                id: 0,
                name: '已下架'
            }
        ],
        check_report_cat:[
            {
                id: 3,
                name: '未处理'
            },
            {
                id: 4,
                name: '发布者'
            },
            {
                id: 5,
                name: '举报者'
            },
            {
                id: 6,
                name: '无违规'
            }
        ]
    },
    onLoad: function (options) {
        var check_report = app.globalData.check_report;
        this.setData({
            check_report: check_report
        });
        if (check_report){
            this.getReportList();
        }
        else{
            this.getGoodsList();
        }
    },
    onShow: function () {
        this.setData({
            p: 1,
            goods_list: [],
            loadingMoreHidden: true
        });
        var check_report = app.globalData.check_report;
        this.setData({
            check_report: check_report
        });
        if (check_report){
            this.getReportList();
        }
        else{
            this.getGoodsList();
        }
    },
    businessTypeClick: function (e) {
        //选择一次分类时返回选中值
        this.setData({
            businessTypeId: e.currentTarget.id,
            p: 1,
            goods_list: [],
            loadingMoreHidden: true,
            processing: false,
        });
        this.getGoodsList();
    },
    statusTypeClick: function (e) {
        //选择一次分类时返回选中值
        this.setData({
            statusId: e.currentTarget.id,
            p: 1,
            goods_list: [],
            loadingMoreHidden: true,
            processing: false,
        });
        this.getGoodsList();
    },
    checkReportClick: function (e) {
        //选择一次分类时返回选中值
        this.setData({
            reportStatusId: e.currentTarget.id,
            p: 1,
            goods_list: [],
            loadingMoreHidden: true,
            processing:false
        });
        this.getReportList();
    },
    getGoodsList: function (e) {
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
            url: app.buildUrl("/record/search"),
            header: app.getRequestHeader(),
            data: {
                p: that.data.p,
                status: that.data.statusId,
                business_type: that.data.businessTypeId
            },
            success: function (res) {
                var resp = res.data
                if (resp.code !== 200) {
                    app.alert({'content': resp.msg});
                    return
                }
                var goods_list = resp.data.list;
                goods_list = app.cutStr(goods_list);
                that.setData({
                    goods_list: that.data.goods_list.concat(goods_list),
                    p: that.data.p + 1,
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
                            loadingHidden: true,
                            processing: false,
                        });
                        },
        })
    },
    getReportList: function (e) {
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
            url: app.buildUrl("/report/search"),
            header: app.getRequestHeader(),
            data: {
                p: that.data.p,
                status: that.data.reportStatusId,
            },
            success: function (res) {
                var resp = res.data
                if (resp.code !== 200) {
                    app.alert({'content': resp.msg});
                    return
                }
                var goods_list = resp.data.list;
                goods_list = app.cutStr(goods_list);
                that.setData({
                    goods_list: that.data.goods_list.concat(goods_list),
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
                            loadingHidden: true,
                            processing:false
                        });
                    },
        })
    },
    onReachBottom: function (e) {
        var that = this;
        //延时500ms处理函数
        if (this.data.check_report){
            setTimeout(function () {
            that.setData({
                hloadingHidden: true,
            });
            that.getReportList();
        }, 500)
        }
        else{
        setTimeout(function () {
            that.setData({
                hloadingHidden: true,
            });
            that.getGoodsList();
        }, 500)}
    },
    editRecord: function (event) {
        var goods_id = event.currentTarget.dataset.id;
        var statusId=this.data.statusId;
        console.log(statusId);
        if (statusId===1) {
            wx.navigateTo({
                url: "../goods/info?goods_id=" + goods_id
            });
        } else {
            wx.showModal({
                title: '温馨提示',
                content: '下架商品不允许修改，请上架后再修改',
            })
        }
    },
    changeRecordStatus: function (event) {
        var id = event.currentTarget.dataset.id;
        var index = event.currentTarget.dataset.index;
        console.log(index);
        var that = this;
        wx.showLoading({
            'title': '提交中..'
        });
        wx.request({
            url: app.buildUrl("/record/change-status"),
            header: app.getRequestHeader(),
            data: {
                id: id,
            },
            success: function (res) {
                wx.hideLoading();
                wx.showToast({
                    title: '修改成功',
                    icon: 'success',
                    duration: 2000
                });
                var goods_list = that.data.goods_list;
                if (goods_list[index].status === 1) {
                    var statusID = 0
                } else {
                    var statusID = 1
                }
                that.setData({
                    statusId: statusID,
                    goods_list: [],
                    loadingMoreHidden: true,
                    p: 1,
                });
                that.getGoodsList();
            }
        })
    },
    toDetail: function (event) {
        var goods_id = event.currentTarget.dataset.id;
        wx.navigateTo({
                    url: '../goods/info?goods_id=' + goods_id,
        })
    },
    logoutCheckReport: function () {
        if (this.data.check_report) {
            app.globalData.check_report = !this.data.check_report
        }
        wx.switchTab({
            url: '../goods/index',
        })
    }
});