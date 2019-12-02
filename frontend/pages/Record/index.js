var goodsData = require("../../data/posts-data.js");
var util = require("../../utils/util.js");
var app = getApp();
Page({
  data: {
    name: "",
    type: "",
  },

  onLoad: function (options) {
    this.setData({
      infos: {
        list: {},
        saveHidden: true,
        check_status_id: 2,
        check_cat: [
          {
            id: 2,
            name: '待取回'
          },
          {
            id: 3,
            name: '已取回',
          },
          {
            id: 4,
            name: '已答谢',
          },
        ],
      },
      check_status_id: 2,
      owner_name: "",
      goods_name: "",
    })
    this.onPullDownRefresh();
  },
  onShow: function () {
    var regFlag = app.globalData.regFlag;
    this.setData({
      regFlag: regFlag
    });
    this.onPullDownRefresh();
    // this.getBanners();
  },
  //下拉刷新
  onPullDownRefresh: function (event) {
    var infos=this.data.infos;
    infos.list=[];
    this.setData({
      p: 1,
      infos:infos,
      loadingMoreHidden: true
    });
    this.getGoodsList();
  },
  listenerNameInput: function (e) {
    this.setData({
      owner_name: e.detail.value
    });
  },
  listenerGoodsNameInput: function (e) {
    this.setData({
      goods_name: e.detail.value
    });
  },
  //点击信息卡查看详情
  onDetailTap: function (event) {
    var id = event.currentTarget.dataset.id;
    var saveHidden = this.data.infos.saveHidden;
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
  onReachBottom: function (e) {
    var that = this;
    //延时500ms处理函数
    setTimeout(function () {
      that.setData({
        loadingHidden: true
      });
      that.getGoodsList();
    }, 500);
  },
  formSubmit: function (e) {
    this.onPullDownRefresh();
  },
  //获取信息列表
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
        status: that.data.check_status_id,
        mix_kw: that.data.goods_name,
        owner_name: that.data.owner_name,
        p: that.data.p,
        business_type: that.data.business_type,
      },
      success: function (res) {
        var resp = res.data;
        if (resp.code !== 200) {
          app.alert({
            'content': resp.msg
          });
          return
        }
        var goods_list = resp.data.list;
        goods_list = app.cutStr(goods_list);
        goods_list=that.data.infos.list.concat(goods_list),
        //修改save的状态
        that.setData({
          p: that.data.p + 1,
        });
        if (resp.data.has_more === 0) {
          that.setData({
            loadingMoreHidden: false,
          })
        }
        that.setPageData(that.getSaveHide(), that.allSelect(), that.noSelect(), goods_list);
      },
      fail: function (res) {
        app.serverBusy();
        return;
      },
      complete: function (res) {
        that.setData({
          processing: false,
          loadingHidden: true
        });
      },
    })
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
    //选择一次分类时返回选中值
    this.setData({
      check_status_id: e.currentTarget.id,
      p: 1,
      loadingMoreHidden: true,
      processing: false
    });
    this.onPullDownRefresh();
  },
})