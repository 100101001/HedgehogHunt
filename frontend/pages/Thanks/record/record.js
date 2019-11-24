// pages/Thanks/record/record.js
var util = require("../../../utils/util.js");
var app = getApp();
Page({
  data: {

  },

  onLoad: function (options) {

    this.setData({
      infos: {
        list:[{
          "auther_name": "韦朝旭",
          "mobile": 18385537403,
          "avatar": "https://wx.qlogo.cn/mmopen/vi_32/Q0j4TwGTfTJLMa7CuCcoXicK6SpMA9E0IHxPgLYibKFbeCkUo3IicyyDr8ssosTEaaptIL2Xjic6LXEC2OmjwmXMmQ/132",
          "summary": "谢谢你的反馈，我找回了钱包,钱包里面的很多证件对我很重要，真的真的十分感谢", //详情介绍
          // "reward": "酬金：3000",
          "updated_time": "2019-10-30 12:20:40", //更新时间
          "id": 1
        }],
        saveHidden: true,
        check_status_id: 0,
        check_cat: [
          {
            id: 0,
            name: '未读'
          },
          {
            id: 1,
            name: '已读',
          }]
      },
      check_status_id: 3
    })
  },
  //点击信息卡查看详情
  onDetailTap: function (event) {
    var id = event.currentTarget.dataset.id;
    var saveHidden = this.data.saveHidden;
    if (!saveHidden) {
      app.alert({
        'content': "请先完成编辑再查看详情~"
      });
    } else {
      wx.navigateTo({
        url: 'info/info',
      })
    }
  },
  //下拉刷新
  onPullDownRefresh: function (event) {
    util.showMessage("下拉刷新函数", "已经写好");
    wx.stopPullDownRefresh();
  },
  //上滑加载
  onReachBottom: function (event) {
    util.showMessage("上滑加载", "已经写好");
  },

  selectTap: function (e) {
    var index = e.currentTarget.dataset.index;
    var list = this.data.infos.list;
    if (index !== "" && index != null) {
      list[index].selected = !list[index].selected;
      this.setPageData(this.getSaveHide(), this.allSelect(), this.noSelect(), list);
    }
  },
  //计算是否全选了
  allSelect: function () {
    var list = this.data.infos.list;
    var allSelect = false;
    for (var i = 0; i < list.length; i++) {
      var curItem = list[i];
      if (curItem.selected) {
        allSelect = true;
      } else {
        allSelect = false;
        break;
      }
    }
    return allSelect;
  },
  //计算是否都没有选
  noSelect: function () {
    var list = this.data.infos.list;
    var noSelect = 0;
    for (var i = 0; i < list.length; i++) {
      var curItem = list[i];
      if (!curItem.selected) {
        noSelect++;
      }
    }
    if (noSelect == list.length) {
      return true;
    } else {
      return false;
    }
  },
  //全选和全部选按钮
  bindAllSelect: function () {
    var currentAllSelect = this.data.infos.allSelect;
    var list = this.data.infos.list;
    for (var i = 0; i < list.length; i++) {
      if (currentAllSelect) {
        list[i].selected = false;
      } else {
        list[i].selected = true;
      }
    }
    this.setPageData(this.getSaveHide(), !currentAllSelect, this.noSelect(), list);
  },
  //编辑默认全不选
  editTap: function () {
    var list = this.data.infos.list;
    for (var i = 0; i < list.length; i++) {
      var curItem = list[i];
      curItem.active = false;
    }
    this.setPageData(!this.getSaveHide(), this.allSelect(), this.noSelect(), list);
  },
  //选中完成默认全选
  saveTap: function () {
    var list = this.data.infos.list;
    for (var i = 0; i < list.length; i++) {
      var curItem = list[i];
      curItem.active = true;
    }
    this.setPageData(!this.getSaveHide(), this.allSelect(), this.noSelect(), list);
  },
  getSaveHide: function () {
    return this.data.infos.saveHidden;
  },
  setPageData: function (saveHidden, allSelect, noSelect, list) {
    var check_cat = this.data.infos.check_cat;
    var check_status_id = this.data.check_status_id;
    this.setData({
      infos: {
        list: list,
        saveHidden: saveHidden,
        allSelect: allSelect,
        noSelect: noSelect,
        check_cat: check_cat,
        check_status_id: check_status_id
      },
    });
  },
  //选中删除的数据
  deleteSelected: function () {
    var list = this.data.infos.list;
    var id_list = [];
    for (var i = 0; i < list.length; i++) {
      var curItem = list[i];
      if (curItem.selected) {
        id_list.push(curItem.id);
      }
    }
    //获取到有改动的记录的id
    console.log(id_list);
    // this.setPageData(this.getSaveHide(), this.allSelect(), this.noSelect(), list);
  },
  getCartList: function () {
    var that = this;
    wx.request({
      url: app.buildUrl("/cart/index"),
      header: app.getRequestHeader(),
      success: function (res) {
        var resp = res.data;
        if (resp.code != 200) {
          app.alert({
            "content": resp.msg
          });
          return;
        }
        that.setData({
          list: resp.data.list,
          saveHidden: true,
          totalPrice: 0.00,
          allSelect: true,
          noSelect: false
        });

        that.setPageData(that.getSaveHide(), that.totalPrice(), that.allSelect(), that.noSelect(), that.data.list);
      }
    });
  },
  checkReportClick: function (e) {
    var list = this.data.infos.list;
    //选择一次分类时返回选中值
    this.setData({
      check_status_id: e.currentTarget.id,
      p: 1,
      goods_list: [],
      loadingMoreHidden: true,
      processing: false
    });
    this.setPageData(this.getSaveHide(), this.allSelect(), this.noSelect(), list);
  },
})