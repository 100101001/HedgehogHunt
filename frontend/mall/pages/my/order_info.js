var app = getApp();
Page({
    data: {},
    onLoad: function (e) {
        this.setData({
            order_sn: e.order_sn
        })
    },
    onShow: function () {
        this.getPayOrderInfo();
    },
    getPayOrderInfo:function(){
        wx.request({
            url: app.buildUrl("/my/order/info"),
            header: app.getRequestHeader(),
            data: {
                order_sn: this.data.order_sn
            },
            success:  (res) => {
                let resp = res.data;
                if (resp['code'] != 200) {
                    app.alert({content: resp['msg']});
                    return
                }

                this.setData({
                   info:resp.data.info
                })
            }
        });
    }
});