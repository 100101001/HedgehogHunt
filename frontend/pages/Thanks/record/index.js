// pages/Thanks/record/record.js
var util = require("../../../utils/util.js");
var app = getApp();
Page({
  data: {
    owner_name: "",
    goods_name: "",
    business_type: "",
    only_new: false
  },

  onLoad: function(options) {
    var op_status = options.op_status;
    var thanks_new = app.globalData.thanks_new;
    // var op_status = app.globalData.op_status;
    // var op_status=4;
    if (op_status == 4) {
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
            name: '已隐藏'
          }
        ]
      };
      var check_status_id = 1;
    } else {
      var infos = {
        list: [],
        saveHidden: true,
        only_new: false,
        op_status: op_status,
        check_status_id: 0,
        check_cat: [{
            id: 0,
            name: '收到',
            value: thanks_new,
          },
          {
            id: 1,
            name: "发出"
          }
        ]
      };
      var check_status_id = 0;
    }
    this.setData({
      infos:infos,
      check_status_id:check_status_id,
      only_new: false,
      op_status:op_status
    });
    this.onPullDownRefresh();
    //更新最新提示
    // this.updateTips();
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
    app.getNewRecommend();
    var op_status=this.data.op_status;
    if (op_status==4){
      console.log("op_status+"+op_status);
      this.getReportList();
    }else{
      this.getGoodsList();
    }
  },
  //上滑加载
  onReachBottom: function(e) {
    var that = this;
    //延时500ms处理函数
    setTimeout(function() {
      that.setData({
        loadingHidden: true
      });
      that.getGoodsList();
    }, 500);
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
      url: app.buildUrl("/thanks/search"),
      header: app.getRequestHeader(),
      data: {
        status: that.data.check_status_id,
        mix_kw: that.data.goods_name,
        owner_name: that.data.owner_name,
        p: that.data.p,
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
  //获取信息列表
  getReportList: function(e) {
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
      url: app.buildUrl("/thanks/reports-search"),
      header: app.getRequestHeader(),
      data: {
        report_status: that.data.check_status_id,
        mix_kw: that.data.goods_name,
        owner_name: that.data.owner_name,
        p: that.data.p,
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
  selectTap: function(e) {
    var index = e.currentTarget.dataset.index;
    var list = this.data.infos.list;
    if (index !== "" && index != null) {
      list[index].selected = !list[index].selected;
      this.setPageData(this.getSaveHide(), this.allSelect(), this.noSelect(), list);
    }
  },
  //拉黑举报者
  toBlock: function (e) {
    var report_status = e.currentTarget.dataset.report_status;
    var report_id = e.currentTarget.dataset.report_id;
    var that = this;
    var data = {
      report_id: report_id,
      report_status: report_status,
    };
    wx.request({
      url: app.buildUrl("/thanks/block"),
      header: app.getRequestHeader(),
      data: data,
      success: function (res) {
        var resp = res.data;
        if (resp.code !== 200) {
          app.alert({
            'content': resp.msg
          });
          return
        }
        wx.hideLoading();
        wx.showToast({
          title: '操作成功！',
          icon: 'success',
          duration: 2000
        });
        that.onPullDownRefresh();
      },
      fail: function (res) {
        wx.hideLoading();
        wx.showToast({
          title: '操作失败',
          duration: 2000
        });
        app.serverBusy();
        return;
      }
    });
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
      url: app.buildUrl("/thanks/delete"),
      header: app.getRequestHeader(),
      data: {
        id_list: id_list,
        op_status:that.data.op_status,
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
  //举报答谢信息
  //举报按钮
  toReport: function (e) {
    var regFlag = app.globalData.regFlag;
    if (!regFlag) {
      app.loginTip();
      return;
    }
    var id = e.currentTarget.dataset.id;
    var that = this;
    wx.showModal({
      title: "违规举报",
      content: "为维护平台环境，欢迎举报色情及诈骗、恶意广告等违规信息！同时，恶意举报将会被封号，请谨慎操作，确认举报？",
      success: function (res) {
        if (res.confirm) { //点击确定,获取操作用户id以及商品id,从用户token里面获取id
          wx.showLoading({
            title: '信息提交中..'
          });
          wx.request({
            url: app.buildUrl("/goods/report"),
            header: app.getRequestHeader(),
            data: {
              id: id,
              record_type: 0,
            },
            success: function (res) {
              var resp = res.data;
              if (resp.code != 200) {
                app.alert({
                  'content': resp.msg
                });
                return
              }
              wx.hideLoading();
              wx.showToast({
                title: '举报成功，感谢！',
                icon: 'success',
                duration: 2000
              });
            },
            fail: function (res) {
              wx.hideLoading();
              wx.showToast({
                title: '系统繁忙，反馈失败，还是感谢！',
                duration: 2000
              });
            },
            complete: function () {
              wx.hideLoading();
              that.onPullDownRefresh();
            }
          });
        }
      }
    });
  },
  getCartList: function() {
    var that = this;
    wx.request({
      url: app.buildUrl("/cart/index"),
      header: app.getRequestHeader(),
      success: function(res) {
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
  recordTypeClick: function(e) {
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
})