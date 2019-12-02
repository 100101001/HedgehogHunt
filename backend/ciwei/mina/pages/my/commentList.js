var app = getApp();
Page({
    data: {
    },
    onLoad: function (options) {
        // 生命周期函数--监听页面加载

    },
    onShow: function () {
        this.getCommentList();
    },
    getCommentList:function(){
        var that = this;
        wx.request({
            url: app.buildUrl("/my/comment/list"),
            header: app.getRequestHeader(),
            success: function (res) {
                var resp = res.data;
                if (resp.code != 200) {
                    app.alert({"content": resp.msg});
                    return;
                }

                that.setData({
                    list: resp.data.list
                });

            }
        });
    }
});
