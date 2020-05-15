// pages/Thanks/record/record.js
const util = require("../../../utils/util.js");
const app = getApp();
Page({
  data: {
    owner_name: "",
    goods_name: "",
    business_type: ""
  },
  onLoad: function (options) {
    let op_status = options.op_status * 1;
    let infos = {
      list: [],
      saveHidden: true,
      only_new: true
    };
    if (op_status === 4) {
      infos['check_cat'] = [{
        id: 1,
        name: '待处理'
      },
        {
          id: 2,
          name: '无违规'
        },
        {
          id: 3,
          name: '已隐藏'
        },
        {
          id: 4,
          name: '举报者'
        },
        {
          id: 5,
          name: '发布者'
        }
      ];
      infos['check_status_id'] = 1;
    } else {
      infos['check_cat'] = [{
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
      op_status: op_status
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
      loadingMore: true
    });
    if (this.data.op_status === 4) {
      this.getReportList();
    } else {
      this.getThanksList();
    }
  },
  //上滑加载
  onReachBottom: function (e) {
    //延时500ms处理加载
    setTimeout(() => {
      this.setData({
        loadingHidden: true
      });
      this.getThanksList();
    }, 500);
  },
  /**
   * listenerNameInput 搜索框监听物主名输入
   * @param e
   */
  listenerNameInput: function (e) {
    this.setData({
      changed: true,
      owner_name: e.detail.value
    });
  },
  /**
   * listenerNameInput 搜索框监听物品名输入
   * @param e
   */
  listenerGoodsNameInput: function (e) {
    this.setData({
      changed: true,
      goods_name: e.detail.value
    });
  },
  onBindFocus: function(e){
    let id = e.currentTarget.dataset.id * 1;
    this.setData({focused1: id===1, focused2: id===2});
  },
  onBindBlur: function(e){
    let id = e.currentTarget.dataset.id * 1;
    this.setData({focused1: !(id===1 || !this.data.focused1), focused2: !(id===2 || !this.data.focused2)});
    this.search();
  },
  ownerNameClean: function (e) {
    this.setData({
      changed: true,
      owner_name: ''
    });
    this.search();
  },
  goodsNameClean: function(e){
    this.setData({
      changed: true,
      goods_name: ''
    });
    this.search();
  },
  search: function () {
    if (this.data.changed) {
      this.setData({changed: false});
      this.onPullDownRefresh();
    }
  },
  //获取信息列表
  getThanksList: function (e) {
    if (!this.data.loadingMore || this.data.processing) {
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
          loadingMore: data['has_more'],
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
  /**
   * 获取被举报的答谢
   * @param e
   */
  getReportList: function (e) {
    if (!this.data.loadingMore || this.data.processing) {
      return;
    }
    this.setData({
      processing: true,
      loadingHidden: false
    });
    wx.request({
      url: app.buildUrl("/report/thanks/search"),
      header: app.getRequestHeader(),
      data: {
        report_status: this.data.check_status_id,
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
        let goods_list = resp['data']['list'];
        goods_list = app.cutStr(goods_list);
        goods_list = this.data.infos.list.concat(goods_list);
        //修改save的状态
        this.setData({
          p: this.data.p + 1,
          loadingMore: resp['data']['has_more']
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
  selectTap: function (e) {
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
    app.alert({
      content: '操作不可逆，确认操作？',
      showCancel: true,
      cb_confirm: () => {
        this.doBlock(e.currentTarget.dataset.id, e.currentTarget.dataset.report_status)
      }
    })
  },
  doBlock: function (thank_id, report_status) {
    wx.request({
      url: app.buildUrl("/report/thanks/deal"),
      header: app.getRequestHeader(),
      data: {
        thank_id: thank_id,
        report_status: report_status,
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
          title: '操作成功！',
          icon: 'success',
          duration: 1000,
          success: (res) => {
            setTimeout(this.onPullDownRefresh, 800)
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
  allSelect: function () {
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
  bindAllSelect: function () {
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
  editTap: function () {
    let list = this.data.infos.list;
    for (let i = 0; i < list.length; i++) {
      list[i].selected = false;
    }
    this.setPageData(!this.getSaveHide(), this.allSelect(), this.noSelect(), list);
  },
  //选中完成默认全选
  saveTap: function () {
    let list = this.data.infos.list;
    for (let i = 0; i < list.length; i++) {
      let curItem = list[i];
      curItem.selected = true;
    }
    this.setPageData(!this.getSaveHide(), this.allSelect(), this.noSelect(), list);
  },
  getSaveHide: function () {
    return this.data.infos.saveHidden;
  },
  setPageData: function (saveHidden, allSelect, noSelect, list) {
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
  deleteSelected: function () {
    let list = this.data.infos.list;
    let id_list = [];
    for (let i = 0; i < list.length; i++) {
      let curItem = list[i];
      if (curItem.selected) {
        id_list.push(curItem.id);
      }
    }
    let url = this.data.op_status*1 === 4? '/report/thanks/delete' : '/thanks/delete';
    wx.request({
      url: app.buildUrl(url),
      header: app.getRequestHeader(),
      data: {
        id_list: id_list,
        op_status: this.data.op_status,
        status: this.data.check_status_id
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
      content: "为维护平台环境，欢迎举报恶搞、诈骗、私人广告、色情等违规信息！同时，恶意举报将会被封号，请谨慎操作，确认举报？",
      showCancel: true,
      cb_confirm: () => {
        this.doReport(e.currentTarget.dataset.index)
      },
    });
  },
  doReport: function (index) {
    wx.showLoading({
      title: '信息提交中..'
    });
    wx.request({
      url: app.buildUrl("/report/thanks"),
      header: app.getRequestHeader(),
      data: {
        id: this.data.infos.list[index].id
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
          duration: 1000
        });
        //前端隐藏举报项
        let received_thanks = this.data.infos;
        received_thanks.list.splice(index, 1);
        this.setData({
          infos: received_thanks
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
  checkReportClick: function (e) {
    //选择一次分类时返回选中值
    let infos = this.data.infos;
    //选择一次分类时返回选中值
    let old_status_id = infos.check_status_id;
    infos.check_status_id = e.currentTarget.id;
    this.setData({
      infos: infos,
      check_status_id: e.currentTarget.id,
    });
    //如果不一致
    if (old_status_id !== infos.check_status_id) {
      this.onPullDownRefresh()
    }
  },
  radioChange: function () {
    //选择一次分类时返回选中值
    let infos = this.data.infos;
    infos.only_new = !this.data.only_new;
    this.setData({
      infos: infos,
      only_new: infos.only_new,
    });
    this.onPullDownRefresh();
  },
  recordTypeClick: function (e) {
    let infos = this.data.infos;
    //选择一次分类时返回选中值
    let old_status_id = infos.check_status_id;
    infos.check_status_id = e.currentTarget.id;
    this.setData({
      infos: infos,
      check_status_id: e.currentTarget.id,
    });
    //如果不一致
    if (old_status_id !== infos.check_status_id) {
      this.onPullDownRefresh()
    }
  },
  onUnload: function () {
    if (this.data.op_status !== 4) {
      wx.request({
        url: app.buildUrl("/thanks/read"),
        header: app.getRequestHeader()
      })
    }
  }
})