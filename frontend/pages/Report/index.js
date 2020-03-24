var util = require("../../utils/util.js");
var app = getApp();
Page({
  data: {
    owner_name: "",
    goods_name: "",
    business_type: "",
  },

  onLoad: function(options) {
    var goodsList = goodsData.goodsList;
    //截取前14个字当做概况
    for (var i in goodsList) {
      goodsList[i].content = goodsList[i].summary.substring(0, 27) + "...";
    }
    this.setData({
      infos:{
        list: goodsList,
        only_new: false,
        saveHidden: true,
        check_status_id: 1,
        check_cat: [
          {
            id: 1,
            name: '待处理'
          },
          {
            id: 2,
            name: '发布者'
          },
          {
            id: 3,
            name: '举报者'
          },
          {
            id: 4,
            name: '无违规'
          }
        ]
      },
      check_status_id:1,
      record_type_status: 1,
      record_type_cat: [
        {
          id: 1,
          name: '物品'
        },
        {
          id: 0,
          name: '答谢'
        }
      ]
    });
    this.onPullDownRefresh();
  },
  updateTips: function () {
    if (this.data.op_status == 2) {
      var recommend = app.globalData.recommend;
      var infos = this.data.infos;
      infos.check_cat = [
        {
          id: 1,
          name: '待认领/寻回',
          value: recommend.wait,
        },
        {
          id: 2,
          name: '预认领/寻回',
          value: recommend.doing,
        },
        {
          id: 3,
          name: '已认领/寻回',
          value: recommend.done,
        },
      ];
      this.setData({
        infos: infos
      })
    }
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
        url: '/pages/Find/info/info?goods_id=' + id,
      })
    }
  },
  //下拉刷新
  onPullDownRefresh: function (event) {
    var infos = this.data.infos;
    infos.list = [];
    this.setData({
      p: 1,
      infos: infos,
      loadingMoreHidden: true
    });
    // this.updateTips();
    this.getGoodsList();
  },
  //下滑加载
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
      url: app.buildUrl("/report/search"),
      header: app.getRequestHeader(),
      data: {
        status: that.data.check_status_id,
        mix_kw: that.data.goods_name,
        owner_name: that.data.owner_name,
        p: that.data.p,
        record_type: that.data.record_type_status,
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
        goods_list = that.data.infos.list.concat(goods_list),
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
  selectTap: function(e) {
    var index = e.currentTarget.dataset.index;
    var list = this.data.infos.list;
    if (index !== "" && index != null) {
      list[index].selected = !list[index].selected;
      this.setPageData(this.getSaveHide(), this.allSelect(), this.noSelect(), list);
    }
  },
  //计算是否全选了
  allSelect: function() {
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
  noSelect: function() {
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
  bindAllSelect: function() {
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
  editTap: function() {
    var list = this.data.infos.list;
    for (var i = 0; i < list.length; i++) {
      var curItem = list[i];
      curItem.active = false;
    }
    this.setPageData(!this.getSaveHide(), this.allSelect(), this.noSelect(), list);
  },
  //选中完成默认全选
  saveTap: function() {
    var list = this.data.infos.list;
    for (var i = 0; i < list.length; i++) {
      var curItem = list[i];
      curItem.active = true;
    }
    this.setPageData(!this.getSaveHide(), this.allSelect(), this.noSelect(), list);
  },
  getSaveHide: function() {
    return this.data.infos.saveHidden;
  },
  setPageData: function(saveHidden, allSelect, noSelect, list) {
    var check_cat = this.data.infos.check_cat;
    var check_status_id=this.data.check_status_id;
    this.setData({
      infos:{
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
  deleteSelected: function() {
    var list = this.data.infos.list;
    var id_list=[];
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
  checkReportClick: function (e) {
    //选择一次分类时返回选中值
    var infos = this.data.infos;
    infos.check_status_id = e.currentTarget.id;
    this.setData({
      infos: infos,
      check_status_id: e.currentTarget.id,
    });
    this.onPullDownRefresh();
  },
  recordTypeClick: function (e) {
    //选择一次分类时返回选中值
    var record_type_status = e.currentTarget.id;
    this.setData({
      record_type_status: record_type_status,
    });
    this.onPullDownRefresh();
  },
  radioChange: function () {
    //选择一次分类时返回选中值
    var infos = this.data.infos;
    infos.only_new = !this.data.only_new;
    this.setData({
      infos: infos,
      only_new: infos.only_new,
    });
    this.onPullDownRefresh();
  }
})