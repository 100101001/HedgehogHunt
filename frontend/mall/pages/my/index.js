//获取应用实例
var app = getApp();
const navigate = require("../template/navigate-bar1/navigate-bar1-template.js")
const utils = require("../../utils/util.js")
Page({
    data: {},
    onLoad() {
        //设置底部导航栏
        var [isSelecteds, urls] = utils.onNavigateTap(2);
        this.setData({
            isSelecteds: isSelecteds
        })
    },
    onShow() {
        this.getInfo();
    },
    getInfo: function () {
        var that = this;
        wx.request({
            url: app.buildUrl("/member/info"),
            header: app.getRequestHeader(),
            success: function (res) {
                var resp = res.data;
                if (resp.code != 200) {
                    app.alert({ "content": resp.msg });
                    return;
                }
                that.setData({
                    user_info: resp.data.info
                });
            }
        });
    },
    //点击导航
    onNavigateTap: function (event) {
        navigate.onNavigateTap(event, this)
    }
});