//获取应用实例
var app = getApp();
Page({
    data: {
        "content": "收到货了，物品无损坏，很喜欢~~",
        "score": 10,
        "order_sn": ""
    },
    onLoad: function (e) {
        var that = this;
        that.setData({
            order_sn: e.order_sn
        });
    },
    scoreChange: function (e) {
        this.setData({
            "score": e.detail.value
        });
    },
    contentBlur: function ( e ) {
        app.console( e );
        this.setData({
            content: e.detail.value
        });
    },
    doComment: function () {
        var that = this;
        wx.request({
            url: app.buildUrl("/my/comment/add"),
            header: app.getRequestHeader(),
            method: "POST",
            data: {
                "content": that.data.content,
                "score": that.data.score,
                "order_sn": that.data.order_sn
            },
            success: function (res) {
                var resp = res.data;
                if (resp.code != 200) {
                    app.alert({"content": resp.msg});
                    return;
                }

                wx.redirectTo({
                    url: "/mall/pages/my/commentList"
                });
            }
        });
    }
});