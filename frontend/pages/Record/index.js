var goodsData = require("../../data/posts-data.js");
var util = require("../../utils/util.js");
var app = getApp();
Page({
  data: {
    owner_name: "",
    goods_name: "",
    business_type: "",
  },

  onLoad: function(options) {
    var op_status = options.op_status;
    console.log("op_status+" + op_status);
    // var op_status =4;
    this.setData({
      op_status: op_status
    })
    this.onLoadSetData(op_status);
    this.onPullDownRefresh();
  },
  onLoadSetData: function(op_status) {
    var recommend = app.globalData.recommend;
    if (op_status == 1) {
      var infos = {
        list: {},
        only_new: false,
        saveHidden: true,
        op_status: op_status,
        check_status_id: 2,
        check_cat: [{
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
      };
      var check_status_id = 2;
    } else if (op_status == 4) {
      var infos = {
        list: {},
        saveHidden: true,
        only_new: false,
        check_status_id: 1,
        op_status: op_status,
        check_cat: [{
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
          },
          {
            id: 5,
            name: '已下架'
          }
        ]
      };
      var check_status_id = 1;
    } else {
      var infos = {
        list: {},
        saveHidden: true,
        check_status_id: 1,
        op_status: op_status,
        only_new: false,
        check_cat: [{
            id: 1,
            name: '待认领/找回',
            value: recommend.wait,
          },
          {
            id: 2,
            name: '预认领/找回',
            value: recommend.doing,
          },
          {
            id: 3,
            name: '已认领/找回',
            value: recommend.done,
          },
        ],
      };
      var check_status_id = 1;
    };
    this.setData({
      check_status_id: check_status_id,
      infos: infos,
      only_new: false
    })
  },
  onShow: function() {
    var regFlag = app.globalData.regFlag;
    this.setData({
      regFlag: regFlag
    });
    // this.getBanners();
  },
  //下拉刷新
  onPullDownRefresh: function(event) {
    var infos = this.data.infos;
    infos.list = [];
    this.setData({
      p: 1,
      infos: infos,
      loadingMoreHidden: true
    });
    var op_status = this.data.op_status;
    if (op_status == 4) {
      this.getReportList();
    } else {
      this.updateTips();
      this.getGoodsList();
    }
  },
  updateTips: function() {
    if (this.data.op_status == 2) {
      var recommend = app.globalData.recommend;
      var infos = this.data.infos;
      infos.check_cat = [{
          id: 1,
          name: '待认领/找回',
          value: recommend.wait,
        },
        {
          id: 2,
          name: '预认领/找回',
          value: recommend.doing,
        },
        {
          id: 3,
          name: '已认领/找回',
          value: recommend.done,
        },
      ];
      this.setData({
        infos: infos
      })
    }
  },
  listenerNameInput: function(e) {
    this.setData({
      owner_name: e.detail.value
    });
  },
  listenerGoodsNameInput: function(e) {
    this.setData({
      goods_name: e.detail.value
    });
  },
  //点击信息卡查看详情
  onDetailTap: function(event) {
    var id = event.currentTarget.dataset.id;
    var saveHidden = this.data.infos.saveHidden;
    if (!saveHidden) {
      app.alert({
        'content': "请先完成编辑再查看详情~"
      });
    } else {
      app.globalData.op_status = this.data.op_status;
      wx.navigateTo({
        url: '/pages/Find/info/info?goods_id=' + id,
      })
    }
  },
  //下滑加载
  onReachBottom: function(e) {
    var that = this;
    //延时500ms处理函数
    setTimeout(function() {
      that.setData({
        loadingHidden: true
      });
      var op_status = that.data.op_status;
      if (op_status == 4) {
        that.getReportList();
      } else {
        that.updateTips();
        that.getGoodsList();
      }
    }, 500);
  },
  formSubmit: function(e) {
    this.onPullDownRefresh();
  },
  //获取信息列表
  getGoodsList: function(e) {
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
        op_status: that.data.op_status,
        //仅获取还未处理过的列表
        only_new: that.data.only_new
      },
      success: function(res) {
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
      fail: function(res) {
        app.serverBusy();
        return;
      },
      complete: function(res) {
        that.setData({
          processing: false,
          loadingHidden: true
        });
      },
    })
  },
  //获取违规列表
  getReportList: function() {
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
      url: app.buildUrl("/report/goods-search"),
      header: app.getRequestHeader(),
      data: {
        status: that.data.check_status_id,
        mix_kw: that.data.goods_name,
        owner_name: that.data.owner_name,
        p: that.data.p,
        record_type: 1,
      },
      success: function(res) {
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
      fail: function(res) {
        app.serverBusy();
        return;
      },
      complete: function(res) {
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
  deleteSelected: function() {
    var that = this;
    var list = this.data.infos.list;
    var id_list = [];
    for (var i = 0; i < list.length; i++) {
      var curItem = list[i];
      if (curItem.selected) {
        id_list.push(curItem.id);
      }
    }
    wx.request({
      url: app.buildUrl("/record/delete"),
      header: app.getRequestHeader(),
      data: {
        op_status: that.data.op_status,
        id_list: id_list
      },
      success: function(res) {
        var resp = res.data;
        if (resp.code !== 200) {
          app.alert({
            'content': resp.msg
          });
          return
        }
        that.onPullDownRefresh();
      },
      fail: function(res) {
        app.serverBusy();
        return;
      },
      complete: function(res) {
        that.setData({
          processing: false,
          loadingHidden: true
        });
      },
    })
    // //获取到有改动的记录的id
    // console.log(id_list);
    // this.setPageData(this.getSaveHide(), this.allSelect(), this.noSelect(), list);
  },
  checkReportClick: function(e) {
    //选择一次分类时返回选中值
    var infos = this.data.infos;
    infos.check_status_id = e.currentTarget.id;
    this.setData({
      infos: infos,
      check_status_id: e.currentTarget.id,
    });
    this.onPullDownRefresh();
  },
  radioChange: function() {
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