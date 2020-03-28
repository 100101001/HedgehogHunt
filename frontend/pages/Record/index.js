var app = getApp();
//从Mine/Mine跳转至此
Page({
  data: {
    owner_name: "",
    goods_name: "",
    business_type: "",
  },
  /**
   * 设置页面顶部选项卡和搜索框(编辑框)的初始化数据
   * 加载后端记录数据，如果是匹配记录则还需更新匹配new计数
   * @param options 跳转传入参数
   */
  onLoad: function(options) {
    var op_status = options.op_status;
    this.setData({
      op_status: op_status, //参数,代表正在查看认领/匹配/发布/答谢
    })
    this.onLoadSetData(op_status);
    this.onPullDownRefresh();
  },
  /**
   * 设置顶部状态选项卡数据，及其它页面初始化数据
   * @param op_status 发布记录 or 认领找回 or 匹配推荐 or 发布举报(管理员可见的管理后台)
   */
  onLoadSetData: function (op_status) {
    if (op_status == 0) { //发布
      var check_cat = [
        {
          id: 1,
          name: '待寻回/认领'
        },
        {
          id: 2,
          name: '已寻回/认领',
        },
        {
          id: 3,
          name: '已答谢',
        },
      ]
    } else if (op_status == 1) { //认领和找回记录
      var check_cat = [
        {
          id: 2,
          name: '预认领/找回',
        },
        {
          id: 3,
          name: '已认领/找回',
        },
      ];
    } else if (op_status == 2) { //匹配推送
      var recommend = app.globalData.recommend
      var check_cat = [{
        id: 1,
        name: '待认领',
        value: recommend.wait,
      },
        {
          id: 2,
          name: '预认领',
          value: recommend.doing,
        },
        {
          id: 3,
          name: '已认领',
          value: recommend.done,
        },
      ]
    } else if (op_status == 4) { //管理后台
      var check_cat = [{
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
    }
    this.setData({
      only_new: false,
      check_status_id: op_status == 1 ? 2 : 1, //代表当前选中的选项卡，认寻记录的默认状态是预，其它都是待
      infos: {
        list: {},
        only_new: false,
        saveHidden: true,
        op_status: op_status,  //参数,代表正在查看认领/匹配/发布/答谢
        check_status_id: 1, //代表当前选中的选项卡
        check_cat: check_cat
      }
    })
  },
  /**
   * onShow 如果是匹配推荐页面则，刷新new计数
   */
  onShow: function() {
    this.setData({
      regFlag: app.globalData.regFlag
    });
    //新的recommend数量与app全局数据同步化
    if (this.data.op_status == 2) {
      this.updateTips();
    }
  },
  /**
   * onPullDownRefresh 刷新页面
   * 重新从第一页开始获取记录，如果是匹配推荐则还需更新new计数
   */
  onPullDownRefresh: function () {
    let infos = this.data.infos;
    infos.list = [];
    this.setData({
      p: 1,
      infos: infos,
      loadingMoreHidden: true
    });
    let op_status = this.data.op_status;
    if (op_status == 4) {
      this.getReportList();
    } else {
      if (op_status == 2) {
        //匹配更新new计数
        this.updateTips();
      }
      this.getGoodsList();
    }
  },
  /**
   * updateTips 同步推荐计数
   */
  updateTips: function() {
    if (this.data.op_status == 2) {
      let recommend = app.globalData.recommend;
      let infos = this.data.infos;
      infos.check_cat[0].value = recommend.wait //推荐记录状态是待认领
      infos.check_cat[1].value = recommend.doing //推荐记录状态是预认领
      infos.check_cat[2].value = recommend.done //推荐记录状态是已认领
      this.setData({
        infos: infos
      })
    }
  },
  /**
   * listenerNameInput 搜索框监听物主名输入
   * @param e
   */
  listenerNameInput: function(e) {
    this.setData({
      owner_name: e.detail.value
    });
  },
  /**
   * listenerNameInput 搜索框监听物品名输入
   * @param e
   */
  listenerGoodsNameInput: function(e) {
    this.setData({
      goods_name: e.detail.value
    });
  },
  /**
   * onDetailTap 点击信息卡查看详情
   * @param event
   */
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
      //更新new标识
      var infos = this.data.infos
      var idx = (infos.list || []).findIndex((item) => item.id === id)
      infos.list[idx].new = 1
      this.setData({
        infos: infos
      })
    }
  },
  //下滑加载
  onReachBottom: function (e) {
    var that = this
    //延时500ms处理函数
    setTimeout(function () {
      that.setData({
        loadingHidden: true
      });
      var op_status = that.data.op_status
      if (op_status == 4) {
        that.getReportList()
      } else {
        that.getGoodsList()
      }
    }, 500)
  },
  formSubmit: function(e) {
    this.onPullDownRefresh();
  },
  //获取信息列表
  getGoodsList: function(e) {
    if (!this.data.loadingMoreHidden) {
      return
    }
    if (this.data.processing) {
      return
    }
    this.setData({
      processing: true,
      loadingHidden: false
    });
    wx.request({
      url: app.buildUrl("/record/search"),
      header: app.getRequestHeader(),
      data: {
        status: this.data.check_status_id,
        mix_kw: this.data.goods_name,
        owner_name: this.data.owner_name,
        p: this.data.p,
        op_status: this.data.op_status,
        //仅获取还未处理过的列表
        only_new: this.data.only_new
      },
      success: (res) => {
        let resp = res.data
        if (resp['code'] !== 200) {
          app.alert({
            content: resp['msg']
          })
          return
        }
        let goods_list = resp['data']['list']
        goods_list = app.cutStr(goods_list);
        goods_list = this.data.infos.list.concat(goods_list)
        //修改save的状态
        this.setData({
          p: this.data.p + 1,
        })
        if (resp['data']['has_more'] === 0) {
          this.setData({
            loadingMoreHidden: false,
          })
        }
        this.setPageData(this.getSaveHide(), this.allSelect(), this.noSelect(), goods_list);
      },
      fail: (res) => {
        app.serverBusy()
      },
      complete: (res) => {
        this.setData({
          processing: false,
          loadingHidden: true
        })
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
  },
  checkReportClick: function(e) {
    //选择一次分类时返回选中值
    let infos = this.data.infos;
    infos.check_status_id = e.currentTarget.id;
    this.setData({
      infos: infos,
      check_status_id: e.currentTarget.id,
    });
    this.onPullDownRefresh();
  },
  /**
   * radioChange 查看推荐推送时，修改了仅新增选项后进行筛选
   */
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
  /**
   * op_status为4的时候
   * @param e
   */
  recordTypeClick: function(e) {
    //选择一次分类时返回选中值
    let infos = this.data.infos
    infos.check_status_id = e.currentTarget.id
    this.setData({
      infos: infos,
      check_status_id: e.currentTarget.id
    })
    this.onPullDownRefresh();
  },
})