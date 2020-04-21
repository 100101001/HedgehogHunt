// pages/Thanks/record/record.js
const util = require("../../../utils/util.js");
const app = getApp();
Page({
  data: {
    owner_name: "",
    goods_name: "",
    business_type: ""
  },
  onLoad: function(options) {
    let op_status = options.op_status * 1;
    let infos = {
      list: [],
      saveHidden: true,
      only_new: true
    };
    if (op_status === 4) {
      infos['check_cat']  = [{
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
      ];
      infos['check_status_id'] = 1;
    } else {
      infos['check_cat']  =[{
        id: 0,
        name: '收到',
        value: app.globalData.thanks_new,
      },
        {
          id: 1,
          name: "发出"
        }
      ];
      infos['check_status_id'] = 0;
    }
    this.setData({
      infos: infos,
      check_status_id: infos['check_status_id'],
      only_new: infos['only_new'],
      op_status: op_status,
      all_thanks_checked: false //用于更新查看状态（只看了收到，还是发出也都看了）
    });
    this.onPullDownRefresh()
  },
  //下拉刷新
  onPullDownRefresh: function () {
    let infos = this.data.infos;
    infos.list = [];
    this.setData({
      p: 1,
      infos: infos,
      loadingMoreHidden: true
    });
    if (this.data.op_status === 4) {
      this.getReportList();
    } else {
      this.getThanksList();
    }
  },
  //上滑加载
  onReachBottom: function(e) {
    //延时500ms处理加载
    setTimeout(()=> {
      this.setData({
        loadingHidden: true
      });
      this.getThanksList();
    }, 500);
  },
  listenerNameInput: function(e) {
    this.setData({owner_name: e.detail.value});
  },
  listenerGoodsNameInput: function(e) {
    this.setData({goods_name: e.detail.value});
  },
  //获取信息列表
  getThanksList: function(e) {
    let that = this;
    if (!this.data.loadingMoreHidden || this.data.processing) {
      return;
    }
    this.setData({
      processing: true,
      loadingHidden: false
    });
    wx.request({
      url: app.buildUrl("/thanks/search"),
      header: app.getRequestHeader(),
      data: {
        status: this.data.check_status_id,
        mix_kw: this.data.goods_name,
        owner_name: this.data.owner_name,
        p: this.data.p,
        //仅获取还未处理过的列表
        only_new: this.data.only_new
      },
      success: (res) => {
        let resp = res.data;
        if (resp['code'] !== 200) {
          app.alert({
            content: resp['msg']
          });
          return
        }
        let data = resp['data'];
        let goods_list = data['list'];
        goods_list = app.cutStr(goods_list);
        goods_list = this.data.infos.list.concat(goods_list);
        //修改save的状态
        this.setData({
          p: this.data.p + 1,
          loadingMoreHidden: data['has_more'] !== 0,
        });
        this.setPageData(this.getSaveHide(), this.allSelect(), this.noSelect(), goods_list);
      },
      fail: (res) => {
        app.serverBusy();
      },
      complete: (res) => {
        this.setData({
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
    let index = e.currentTarget.dataset.index;
    let list = this.data.infos.list;
    if (index !== "" && index != null) {
      list[index].selected = !list[index].selected;
      this.setPageData(this.getSaveHide(), this.allSelect(), this.noSelect(), list);
    }
  },
  /**
   * 拉黑举报者
   * @param e
   */
  toBlock: function (e) {
    wx.request({
      url: app.buildUrl("/thanks/block"),
      header: app.getRequestHeader(),
      data: {
        report_id: e.currentTarget.dataset.report_id,
        report_status: e.currentTarget.dataset.report_status,
      },
      success:  (res) => {
        let resp = res.data;
        if (resp['code'] !== 200) {
          app.alert({
            content: resp['msg']
          });
          return;
        }
        wx.showToast({
          title: '操作成功！',
          icon: 'success',
          duration: 1000,
          success: (res)=>{
            setTimeout(this.onPullDownRefresh, 800)
          }
        });
      },
      fail:  (res) => {
        app.serverBusy();
      },
      complete: (res) => {
        wx.hideLoading();
      }
    });
  },
  /**
   * 是否全选了
   * @returns {boolean}
   */
  noSelect: function () {
    let list = this.data.infos.list;
    let noSelect = true;
    for (let i = 0; i < list.length; i++) {
      if (list[i].selected) {
        noSelect = false;
        break;
      }
    }
    return noSelect;
  },
  //计算是否全选了
  allSelect: function() {
    let list = this.data.infos.list;
    let allSelect = true;
    for (let i = 0; i < list.length; i++) {
      if (!list[i].selected) {
        allSelect = false;
        break;
      }
    }
    return allSelect;
  },
  /**
   * 如果全选按钮选中的情况下，点击全选，所有都反选
   */
  bindAllSelect: function() {
    let currentAllSelect = this.data.infos.allSelect;
    let list = this.data.infos.list;
    for (let i = 0; i < list.length; i++) {
      list[i].selected = !currentAllSelect;
    }
    this.setPageData(this.getSaveHide(), !currentAllSelect, this.noSelect(), list);
  },
  /**
   * 关闭/打开操作，且默认所有不选中
   */
  editTap: function() {
    let list = this.data.infos.list;
    for (let i = 0; i < list.length; i++) {
      list[i].selected = false;
    }
    this.setPageData(!this.getSaveHide(), this.allSelect(), this.noSelect(), list);
  },
  //选中完成默认全选
  saveTap: function() {
    let list = this.data.infos.list;
    for (let i = 0; i < list.length; i++) {
      let curItem = list[i];
      curItem.selected = true;
    }
    this.setPageData(!this.getSaveHide(), this.allSelect(), this.noSelect(), list);
  },
  getSaveHide: function() {
    return this.data.infos.saveHidden;
  },
  setPageData: function(saveHidden, allSelect, noSelect, list) {
    this.setData({
      infos: {
        list: list,
        saveHidden: saveHidden,
        allSelect: allSelect,
        noSelect: noSelect,
        check_cat: this.data.infos.check_cat,
        check_status_id: this.data.check_status_id
      },
    });
  },
  /**
   * deleteSelected 删除选中答谢/举报记录
   */
  deleteSelected: function() {
    let list = this.data.infos.list;
    let id_list = [];
    for (let i = 0; i < list.length; i++) {
      let curItem = list[i];
      if (curItem.selected) {
        id_list.push(curItem.id);
      }
    }
    wx.request({
      url: app.buildUrl("/thanks/delete"),
      header: app.getRequestHeader(),
      data: {
        id_list: id_list,
        op_status:this.data.op_status,
      },
      success: (res) => {
        let resp = res.data;
        if (resp['code'] !== 200) {
          app.alert({
            content: resp['msg']
          });
          return
        }
        this.onPullDownRefresh();
      },
      fail: (res) => {
        app.serverBusy();
      },
      complete: (res) => {
        this.setData({
          processing: false,
          loadingHidden: true
        });
      },
    })
  },
  //举报答谢信息
  //举报按钮
  toReport: function (e) {
    if (!app.loginTip()) {
      return;
    }
    app.alert({
      title: "违规举报",
      content: "为维护平台环境，欢迎举报色情及诈骗、恶意广告等违规信息！同时，恶意举报将会被封号，请谨慎操作，确认举报？",
      showCancel: true,
      cb_confirm: () => {
        wx.showLoading({
          title: '信息提交中..'
        });
        wx.request({
          url: app.buildUrl("/thanks/report"),
          header: app.getRequestHeader(),
          data: {
            id: e.currentTarget.dataset.id
          },
          success: (res) => {
            let resp = res.data;
            if (resp['code'] !== 200) {
              app.alert({
                content: resp['msg']
              });
              return;
            }
            wx.showToast({
              title: '举报成功，感谢！',
              icon: 'success',
              duration: 1000,
              success: (res) => {
                setTimeout(this.onPullDownRefresh, 700)
              }
            });
          },
          fail: (res) => {
            app.serverBusy();
          },
          complete: (res) => {
            wx.hideLoading();
          }
        });
      },
    });
  },
  recordTypeClick: function(e) {
    //选择一次分类时返回选中值
    let infos = this.data.infos;
    infos.check_status_id = e.currentTarget.id * 1;
    this.setData({
      infos: infos,
      check_status_id: e.currentTarget.id,
    });
    this.onPullDownRefresh();
  },
  radioChange: function() {
    //选择一次分类时返回选中值
    let infos = this.data.infos;
    infos.only_new = !this.data.only_new;
    this.setData({
      infos: infos,
      only_new: infos.only_new,
    });
    this.onPullDownRefresh();
  },
  checkReportClick: function (e) {
    let infos = this.data.infos
    //从答谢收到切换到了发出时，更新tips
    if (this.data.check_status_id == 0 && e.currentTarget.id == 1) {
      this.data.all_thanks_checked = true
    }
    //选择一次分类时返回选中值
    infos.check_status_id = e.currentTarget.id
    this.setData({
      infos: infos,
      check_status_id: e.currentTarget.id,
    });
    this.onPullDownRefresh()
  },
  onUnload: function () {
    if (this.data.op_status !== 4) {
      wx.request({
        url: app.buildUrl("/thanks/update-status"),
        header: app.getRequestHeader(),
        data: {
          all: this.data.all_thanks_checked
        },
        success: res => {
          app.getNewRecommend()
        }
      })
    }
  }
})