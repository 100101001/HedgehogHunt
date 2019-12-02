//获取应用实例
var app = getApp();
Page({
    data: {
        show_qr_code: false,
        qr_code_list: ["/images/more/qr_code.jpg"],
        loadingHidden:true
    },
    onLoad() {
        this.getInfo();
        var is_user = app.globalData.is_user;
        this.setData({
            is_user: is_user,
        })
    },
    onShow() {
        this.getInfo();
        var is_user = app.globalData.is_user;
        this.setData({
            is_user: is_user,
        })
    },
    getInfo: function () {
        var that = this;
        that.setData({
            loadingHidden: false
        });
        wx.request({
            url: app.buildUrl("/member/info"),
            header: app.getRequestHeader(),
            success: function (res) {
                var resp = res.data;
                if (resp.code !== 200) {
                    app.alert({"content": resp.msg});
                    return;
                }
                that.setData({
                    user_info: resp.data.info,
                    items: [
            {
                label: "反馈建议",
                icons: "/images/icons/next.png",
                act: "goFeedback",
            },
            {
                label: "积分",
                num:resp.data.info.credits,
            },
            {
                label: "联系开发者",
                icons: "/images/icons/down-arrow.png",
                act: "showDeveloperQrcode",
            }
        ]
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
    goControls: function () {
        console.log("去控制台");
        wx.navigateTo({
            url: 'controls/index',
        })
    },
    goFeedback: function () {
        console.log("去反馈");
        wx.navigateTo({
            url: 'controls/feedback/index',
        })
    },
    showDeveloperQrcode: function () {
        var show_qr_code = !this.data.show_qr_code;
        this.setData({
            show_qr_code: show_qr_code
        })
    },
    //预览图片
    previewImage: function (e) {
        var current = e.target.dataset.src;
        wx.previewImage({
            current: current, // 当前显示图片的http链接
            urls: this.data.qr_code_list,
        })
    },
});