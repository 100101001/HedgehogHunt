const app = getApp();
const util = require("../../utils/util");


/**
 * deleteLinkLostGoods 在删除归还通知的时候删除链接的失物
 * @param id_list
 * @param status
 */
const deleteLinkLostGoods = function (id_list = [], status=3) {
  wx.request({
    url: app.buildUrl('/goods/link/lost/del'),
    header: app.getRequestHeader(),
    data: {
      ids: id_list,
      status: status
    },
    success: res => {
      if (res.data.code !== 200) {
        app.alert({content: res.data.msg})
      }
    },
    fail: res => {
      app.serverBusy()
    }
  })
};


/**
 * deleteLinkReturnGoods 在删除寻物的时候，删除归还通知
 * @param id_list
 */
const deleteLinkReturnGoods = function (id_list = []) {
  wx.request({
    url: app.buildUrl('/goods/link/return/del'),
    header: app.getRequestHeader(),
    data: {
      ids: id_list
    },
    success: res => {
      if (res.data['code'] !== 200) {
        app.alert({content: res.data['msg']})
      }
    },
    fail: res => {
      app.serverBusy()
    }
  })
};

/**
 * doCancelReturnGoods  取消归还{@link toDeleteMyReleaseReturn}时，选择直接删除归还帖子
 * @param goods_ids
 */
const doCancelReturnGoods = function (goods_ids = [], status, that) {
  wx.request({
    url: app.buildUrl('/goods/return/cancel'),
    header: app.getRequestHeader(),
    data: {
      ids: goods_ids,
      status: status
    },
    success: res => {
      let resp = res.data
      if (resp['code'] !== 200) {
        app.alert({content: resp['msg']});
        return
      }
      that.editTap();
      that.onPullDownRefresh();
      app.alert({
        title: '操作提示',
        content: '删除成功'
      })
    },
    fail: res => {
      app.serverBusy()
    }
  })
};


/**
 * returnToFoundGoodsInBatch 取消归还{@link toDeleteMyReleaseReturn}时选择实际将帖子转成公开的失物招领
 * @param goods_ids
 * @param status
 */
const returnToFoundGoodsInBatch = function (goods_ids = [], status=0) {
  wx.request({
    url: app.buildUrl('/goods/return/to/found'),
    header: app.getRequestHeader(),
    data: {
      id: goods_ids,
      status: status
    },
    success: res => {
      let resp = res.data;
      if (resp['code'] !== 200) {
        app.alert({content: resp['msg']});
        return
      }
      //直接前往失物招领的发布页面
      wx.showToast({
        title: '操作成功',
        duration: 500,
        mask: true,
        success: res => {
          wx.redirectTo({
            url: '/pages/Find/Find?business_type=1'
          })
        }
      })
    },
    fail: res => {
      app.serverBusy()
    }
  })
};

/**
 * giveUnmarkedFoundToSystem 把待认领的失物招领送给系统
 * @param goods_ids
 * @param status
 * @param that
 */
const giveUnmarkedFoundToSystem = function (goods_ids = [], status=1, that) {
  wx.request({
    url: app.buildUrl('/goods/found/to/sys'),
    header: app.getRequestHeader(),
    data: {
      ids: goods_ids,
      status: status
    },
    success: res => {
      let resp = res.data;
      if (resp['code'] !== 200) {
        app.alert({content: resp['msg']});
        return
      }
      //关闭编辑栏和刷新
      that.editTap();
      that.onPullDownRefresh();
    },
    fail: res => {
      app.serverBusy()
    }
  })
};

/**
 * 根据此进行全选按钮禁用
 * @param goods_list
 * @returns {boolean}
 */
const allUnEditableGood = function (goods_list) {
  let arr =  goods_list.filter((item)=>{return item.unselectable});
  return arr.length === goods_list.length
};


//从Mine/Mine跳转至此
Page({
  data: {
    owner_name: "",
    goods_name: "",
    business_type: 0,
  },
  /**
   * 设置页面顶部选项卡和搜索框(编辑框)的初始化数据
   * 加载后端记录数据，如果是匹配记录则还需更新匹配new计数
   * @param options 跳转传入参数
   */
  onLoad: function (options) {
    let op_status = options.op_status * 1;
    this.setData({
      op_status: op_status, //参数,代表正在查看认领/匹配/发布/答谢
    });
    this.onLoadSetData(op_status);
    this.onPullDownRefresh();
  },
  /**
   * 设置顶部状态选项卡数据，及其它页面初始化数据
   * @param op_status 发布记录 or 认领找回 or 匹配推荐 or 发布举报(管理员可见的管理后台)
   */
  onLoadSetData: function (op_status) {
    let check_cat;
    let title;
    if (op_status === 0) {
      //发布记录
      title = '发布记录';
      check_cat = [
        {
          id: 1,  //goods的status
          name: '待寻回'
        },
        {
          id: 2,  //goods的status
          name: '预寻回',
        },
        {
          id: 3,  //goods的status
          name: '已寻回',
        },
        {
          id: 4,  //goods的status
          name: '已答谢'
        }
      ];
      // 默认查看寻物启事帖子
      this.setData({
        business_type: 0
      })
    } else if (op_status === 1) {
      title = '认领记录';
      //认领记录（后端是Mark表的status不是Goods表的status）
      check_cat = [
        {
          id: 0,  //mark的status，不是goods的status
          name: '待取回',
        },
        {
          id: 1, //mark的status，不是goods的status
          name: '已取回',
        },
        {
          id: 2, //mark的status，不是goods的status
          name: '已答谢',
        }
      ];
    } else if (op_status === 5) {
      title = '归还通知';
      //归还记录（后端是Goods表的status但因为business_type==2所以不用考虑和外部同步）
      check_cat = [
        {
          id: 1,  //goods的status
          name: '待确认',
        },
        {
          id: 2,   //goods的status
          name: '待取回',
        },
        {
          id: 3,  //goods的status
          name: '已取回',
        },
        {
          id: 4,  //goods的status
          name: '已答谢',
        }
      ];
    } else if (op_status === 2) {
      title = '匹配推送';
      //匹配推送
      let recommend = app.globalData.recommend;
      check_cat = [{
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
    }
    else if (op_status === 6){
      title = '申诉记录';
      check_cat = [{
        id: 0,
        name: '待处理',
        //value: recommend.wait,
      },
        {
          id: 1,
          name: '已处理',
          //value: recommend.doing,
        }
      ]
    }
    else if (op_status === 4) {
      title = '举报记录';
      //管理后台
      check_cat = [
        {
          id: 1,
          name: '待处理'
        },
        {
          id: 2,
          name: '无违规'
        },
        {
          id: 3,
          name: '已屏蔽'
        },
        {
          id: 4,
          name: '举报者'
        },
        {
          id: 5,
          name: '发布者'
        }
      ]
    }
    //默认选中首个状态
    wx.setNavigationBarTitle({title: title});
    let check_cat_id = check_cat[0].id;
    this.setData({
      only_new: false,
      check_status_id: check_cat_id, //代表当前选中的选项卡
      infos: {
        list: {},
        only_new: false,
        saveHidden: true,
        op_status: op_status,  //参数,代表正在查看认领/匹配/发布/答谢
        check_status_id: check_cat_id, //代表当前选中的选项卡
        check_cat: check_cat
      },
      all_selected_disabled: true
    })
  },
  /**
   * onShow 如果是匹配推荐页面则，刷新new计数
   */
  onShow: function () {
    this.setData({
      regFlag: app.globalData.regFlag
    });
    //新的recommend和return的数量
    this.onPullDownRefresh();
    this.updateTips();
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
      loadingMore: true,  // 还有更多数据未加载
      all_selected_disabled: true  // 每次操作后的重新加載時，重置，全选按钮禁用
    });
    if (this.data.op_status === 4) {
      this.getReportList();
    } else {
      //匹配更新new计数
      this.getGoodsList();
    }
  },
  /**
   * updateTips 同步推荐计数
   */
  updateTips: function () {
    if (this.data.op_status === 2) {
      util.getNewRecommend((data) => {
        //新的推荐通知
        let recommend = data.recommend;
        let infos = this.data.infos;
        infos.check_cat[0].value = recommend.wait;
        infos.check_cat[1].value = recommend.doing; //推荐记录状态是预认领
        infos.check_cat[2].value = recommend.done; //推荐记录状态是已认领
        this.setData({
          infos: infos
        })
      })
    } else if (this.data.op_status === 5) {
      //新的归还通知
      util.getNewRecommend((data) => {
        let returns = data.return;
        let infos = this.data.infos;
        infos.check_cat[0].value = returns.wait;
        infos.check_cat[1].value = returns.doing; //推荐记录状态是预认领
        this.setData({
          infos: infos
        })
      })
    }
  },
  /**
   * listenerNameInput 搜索框监听物主名输入
   * @param e
   */
  listenerNameInput: function (e) {
    this.setData({
      owner_name: e.detail.value
    });
  },
  /**
   * listenerNameInput 搜索框监听物品名输入
   * @param e
   */
  listenerGoodsNameInput: function (e) {
    this.setData({
      goods_name: e.detail.value
    });
  },
  /**
   * onDetailTap 点击信息卡查看详情
   * @param event
   */
  onDetailTap: function (event) {
    let id = event.currentTarget.dataset.id;
    let saveHidden = this.data.infos.saveHidden;
    if (!saveHidden) {
      app.alert({
        content: "请先完成操作再查看详情~"
      });
    } else {
      wx.navigateTo({
        url: '/pages/Find/info/info?goods_id=' + id + '&op_status=' + this.data.op_status
      });
      //在当前页的info中找到该帖，更新其new标识
      let infos = this.data.infos;
      let idx = (infos.list || []).findIndex((item) => item.id === id);
      infos.list[idx].new = 1;
      this.setData({
        infos: infos
      })
    }
  },
  //下滑加载
  onReachBottom: function (e) {
    //延时500ms处理函数
    setTimeout(() => {
      this.setData({
        loadingHidden: true
      });
      if (this.data.op_status === 4) {
        this.getReportList()
      } else {
        this.getGoodsList()
      }
    }, 500)
  },
  formSubmit: function (e) {
    this.onPullDownRefresh();
  },
  //获取信息列表
  getGoodsList: function (e) {
    if (!this.data.loadingMore || this.data.processing) {
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
        only_new: this.data.only_new,
        business_type: this.data.business_type
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
          all_selected_disabled: this.data.all_selected_disabled && allUnEditableGood(goods_list),  // 都需要不存在才不禁用
          loadingMore: resp['data']['has_more']
        });
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
  /**
   * 获取被举报的物品的列表，进行处理
   */
  getReportList: function () {
    if (!this.data.loadingMore || this.data.processing) {
      return;
    }
    this.setData({
      processing: true,
      loadingHidden: false
    });
    wx.request({
      url: app.buildUrl("/report/goods/search"),
      header: app.getRequestHeader(),
      data: {
        status: this.data.check_status_id,
        mix_kw: this.data.goods_name,
        owner_name: this.data.owner_name,
        p: this.data.p
      },
      success:  (res) => {
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
          all_selected_disabled: this.data.all_selected_disabled && allUnEditableGood(goods_list),  // 都需要不存在才不禁用
          loadingMore: data['has_more']
        });
        this.setPageData(this.getSaveHide(), this.allSelect(), this.noSelect(), goods_list);
      },
      fail:  (res) => {
        app.serverBusy();
      },
      complete:  (res) => {
        this.setData({
          processing: false,
          loadingHidden: true
        });
      },
    })
  },
  /**
   * 勾选了记录后，
   * @param e
   */
  selectTap: function (e) {
    let index = e.currentTarget.dataset.index;
    let list = this.data.infos.list;
    if (index !== "" && index != null) {
      list[index].selected = !list[index].selected;
      this.setPageData(this.getSaveHide(), this.allSelect(), this.noSelect(), list);
    }
  },
  /**
   * 是否全选
   * @returns {boolean}
   */
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
   * 是否全没选
   * @returns {boolean}
   */
  noSelect: function () {
    let list = this.data.infos.list;
    let noSelect = 0;
    for (let i = 0; i < list.length; i++) {
      if (!list[i].selected) {
        noSelect++;
      }
    }
    return noSelect === list.length;
  },
  /**
   * 点击全选按钮后，所有radio状态反选（全选选中点击，radio全空）
   */
  bindAllSelect: function () {
    let currentAllSelect = this.data.infos.allSelect;
    let list = this.data.infos.list;
    for (let i = 0; i < list.length; i++) {
      if (list[i]['unselectable']) {  //不可选择的，点击全选会被跳过
        continue;
      }
      list[i].selected = !currentAllSelect;
    }
    this.setPageData(this.getSaveHide(), !currentAllSelect, this.noSelect(), list);
  },
  //编辑默认全不选
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
      list[i].selected = true;
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
      }
    });
  },
  /**
   * getSelectedIdList 获取批量选中的记录
   * @returns {[]}
   */
  getSelectedIdList: function () {
    let list = this.data.infos.list;
    let id_list = [];
    for (let i = 0; i < list.length; i++) {
      let curItem = list[i];
      if (curItem.selected) {
        id_list.push(curItem.id);
      }
    }
    return id_list
  },
  /**
   * deleteSelected 删除批量选中的记录
   */
  deleteSelected: function () {
    let id_list = this.getSelectedIdList();
    if (id_list.length === 0) {
      app.alert({title: '选择提示', content: '请点击勾选后，再重试。'});
      return;
    }
    let op_status = this.data.op_status;
    if (op_status == 0) {
      // 删除我的发布记录
      this.toDeleteMyRelease(id_list);
    }
    //删除我的认领，我的匹配，归还通知，答谢等
    else if (op_status == 5) {
      //删除我的归还通知
      this.toDeleteReceivedReturn(id_list)
    } else if (op_status == 1) {
      this.toDeleteMyMark(id_list)
    } else if (op_status == 4) {
      this.toDeleteGoodsReport(id_list)
    }
    else {
      this.doDeleteSelected(id_list)
    }
  },
  toDeleteGoodsReport: function(id_list){
    let status = this.data.check_status_id;
    //举报状态是待处理不能操作，其他就直接删除
    if (status !== 1) {
      app.alert({
        title: '删除提示',
        content: '确认删除该举报？',
        showCancel: true,
        cb_confirm: () => {
          this.doDeleteSelected(id_list)
        }
      });
    }
  },
  /**
   * 操作认领记录
   * @param id_list
   */
  toDeleteMyMark: function (id_list=[]) {
    let status = this.data.check_status_id;
    if (status == 1 || status == 2) {
      //删除已取回和已答谢的物品
      app.alert({
        title: '删除提示',
        content: (status == 1 ? '还未答谢，' : '') + '确认删除？',
        showCancel: true,
        cb_confirm: () => {
          this.doDeleteSelected(id_list);
        },
        cb_cancel: () => {
          this.editTap();
        }
      })
    }
  },
  /**
   * op_status==0 && check_status_id == 2 || op_status==5 && check_status_id == 2
   * confirmSelected 批量确认已取回
   */
  confirmSelected: function () {
    //批量确认取回
    app.alert({
      title: '操作提示',
      content: '恭喜取回物品，是否确认取回？',
      showCancel: true,
      cb_cancel: this.editTap,
      cb_confirm: () => {
        let id_list = this.getSelectedIdList();
        let op_status = this.data.op_status;
        let url;
        let biz_type;
        let status;
        if (op_status == 1) {
          url = '/goods/gotback';
          biz_type = 1; //认领记录
          status = 2;  //因为check的是认领
        } else if (op_status == 5 || op_status == 0) {
          url = '/goods/return/gotback';
          biz_type = this.data.business_type;  //0对应发布记录的寻物启事[该页的全选可能会禁掉]或者2对应
          status = this.data.check_status_id;
        }
        this.doGotbackReturnGoods(url, id_list, biz_type, status)
      }
    });
  },
  /**
   * doGotbackReturnGoods 确认取回归还帖
   */
  doGotbackReturnGoods: function (url = "", id_list = [], biz_type = 1, status=2) {
    wx.request({
      url: app.buildUrl(url),
      header: app.getRequestHeader(),
      data: {
        ids: id_list,
        biz_type: biz_type, //给 /goods/return/back 判断传入的id是什么类型的物品
        status: status
      },
      success: res => {
        let resp = res.data;
        if (resp['code'] !== 200) {
          app.alert({content: resp['msg']});
          return
        }
        this.editTap();
        this.onPullDownRefresh();
        app.alert({title: '答谢提示', content: '积分+5，记得答谢发布者哦~'})
      },
      fail: res => {
        app.serverBusy()
      }
    })
  },
  /**
   * toDeleteReceivedReturn 删除收到的归还通知
   */
  toDeleteReceivedReturn: function (id_list = []) {
    let status = this.data.check_status_id
    let cnt = id_list.length
    if (status == 1) {
      //待确认的归还，删除代表拒绝
      this.toRejectReturnGoods("确认" + (cnt > 1 ? '都' : '') + '不是你丢的东西？', id_list, status)
    } else if (status == 3) {
      //已取回的归还，
      this.toDeleteGotbackReturnGoods(id_list)
    }
  },
  /**
   * toRejectReturnGoods 批量删除归还通知代表拒绝归还（不是自己的）
   * @param msg
   */
  toRejectReturnGoods: function (msg = "", id_list = [], status=1) {
    app.alert({
      title: '删除提示',
      content: msg,
      showCancel: true,
      cb_confirm: res => {
        wx.request({
          url: app.buildUrl('/goods/return/reject'),
          header: app.getRequestHeader(),
          data: {
            ids: id_list,
            status: status
          },
          success: res => {
            let resp = res.data;
            if (resp['code'] !== 200) {
              app.alert({content: resp['msg']});
              return
            }
            this.editTap()
            this.onPullDownRefresh()
            app.alert({
              title: '操作提示',
              content: '已拒绝归还。望您早日寻回失物！'
            });
          },
          fail: res => {
            app.serverBusy()
          }
        })
      }
    })
  },
  /**
   * toDeleteGotbackReturnGoods 删除已取回的归还通知
   */
  toDeleteGotbackReturnGoods: function (id_list = []) {
    let status = this.data.check_status_id;
    app.alert({
      title: '删除提示',
      content: (status == 4 ? '' : '还未答谢呢，') + '确认删除？',
      showCancel: true,
      cb_confirm: () => {
        app.alert({
          title: '智能删除',
          content: '点击确认可同时删除已取回的寻物贴。取消则只删除归还通知。',
          showCancel: true,
          cb_confirm: () => {
            deleteLinkLostGoods(id_list, status);
            this.doDeleteSelected(id_list);
          },
          cb_cancel: () => {
            this.doDeleteSelected(id_list)
          }
        })
      }
    })
  },
  /**
   * toDeleteMyRelease 删除我发过的帖子
   */
  toDeleteMyRelease: function (id_list = []) {
    let business_type = this.data.business_type;
    if (business_type === 2) {
      //删除归还贴
      this.toDeleteMyReleaseReturn(id_list)
    } else if (business_type === 1) {
      //删失物招领
      this.toDeleteMyFound(id_list)
    } else if (business_type === 0) {
      //删寻物启事
      this.toDeleteMyLost(id_list)
    }
  },
  /**
   * biz_type == 2 && op_status==0
   * toDeleteMyReleaseReturn 删除我发布的归还帖
   * 已答谢
   */
  toDeleteMyReleaseReturn: function (id_list = []) {
    let status = this.data.check_status_id;
    if (status == 4 || status == 3) {
      //已答谢过的归还贴
      app.alert({
        title: '删除提示',
        content: (status == 3 ? '失主还未答谢，' : '') + '确认删除？',
        showCancel: true,
        cb_confirm: () => {
          this.doDeleteSelected(id_list);
        },
        cb_cancel: () => {
          //收起编辑板
          this.editTap()
        }
      })
    } else if (status == 2) {
      // 待取回时不允许操作
      app.alert({
        title: '删除警示',
        content: '对方还已确认，还未取回，现在不能进行任何操作！',
        cb_confirm: this.editTap
      })
    } else if (status == 1) {
      //删除待确认的归还贴
      app.alert({
        title: '取消提示',
        content: '好心归还的东西，对方还没查阅呢，不再等等？',
        showCancel: true,
        cb_confirm: () => {
          wx.showActionSheet({
            itemList: ['公开归还贴', '删除归还贴'],
            success: (res) => {
              if (res.tapIndex == 0) {
                //公开归还贴
                app.alert({
                  title: '公开提示',
                  content: '是否转成公开的失物招领？',
                  showCancel: true,
                  cb_confirm: res => {
                    //转成失物招领
                    returnToFoundGoodsInBatch(id_list, status)
                  },
                  cb_cancel: this.editTap
                })
              } else {
                //删除归还帖子
                app.alert({
                  title: '删除提示',
                  content: '确认删除？对方将无法查看归还贴',
                  showCancel: true,
                  cb_confirm: () => {
                    doCancelReturnGoods(id_list, status, this)
                  },
                  cb_cancel: this.editTap
                })
              }
            }
          })
        }
      })
    } else if (status == 0) {
      app.alert({
        title: '公开提示',
        content: '确认转成公开的失物招领？',
        showCancel: true,
        cb_confirm: res => {
          //转成失物招领
          returnToFoundGoodsInBatch(id_list, status)
        }
      })
    }
  },
  /**
   * biz_type == 1 && op_status==0
   * toDeleteMyFound 删除我发布的失物招领帖子
   * 待取回的不能操作
   * 待认领，已取回，已答谢的可直接单纯删除{@see doDeleteSelected}
   * 待认领的提示可以送给平台
   */
  toDeleteMyFound: function (id_list = []) {
    let status = this.data.check_status_id;
    if (status == 1) {
      // 无人认领
      app.alert({
        title: '删除提示',
        content: '好心捡到的东西，还没有人认领呢，不再等等？',
        showCancel: true,
        cb_cancel: this.editTap,
        cb_confirm: () => {
          wx.showActionSheet({
            itemList: ['送给系统', '狠心删除'],
            fail: (res)=>{
              this.editTap()
            },
            success: (res) => {
              if (res.tapIndex == 0) {
                //公开归还贴
                app.alert({
                  title: '转送提示',
                  content: '确认转送？',
                  showCancel: true,
                  cb_confirm: res => {
                    //送给系统
                    giveUnmarkedFoundToSystem(id_list, status, this)
                  },
                  cb_cancel: this.editTap
                })
              } else {
                //删除归还帖子
                app.alert({
                  title: '删除提示',
                  content: '确认删除？',
                  showCancel: true,
                  cb_confirm: () => {
                    this.doDeleteSelected(id_list)
                  },
                  cb_cancel: this.editTap
                })
              }
            }
          })
        }
      })
    } else if (status == 2) {
      // 待取回时不允许操作
      app.alert({
        title: '操作警示',
        content: '对方已确认，还未取回，现在不能进行任何操作！',
        cb_confirm: this.editTap
      })
    } else if (status == 3 || status == 4) {
      // 已取回和已答谢允许删除操作
      app.alert({
        title: '删除提示',
        content: (status == 3 ? '失主还未答谢，' : '') + '确认删除？',
        showCancel: true,
        cb_confirm: () => {
          this.doDeleteSelected(id_list);
        },
        cb_cancel: this.editTap
      })
    } else if (status == 5) {
      app.alert({
        title: '操作警示',
        content: '系统收到申诉，正在处理中，帖子已被系统冻结，您无法进行任何操作，请您谅解！',
        cb_confirm: this.editTap
      })
    }
  },
  /**
   * toDeleteMyLost 删除我发布的寻物启事帖子
   * 待归还的，已取回，已答谢的都可以单纯直接删除
   * 已取回，已答谢的可以选择智能删除归还通知{@see deleteLinkReturnGoods}
   */
  toDeleteMyLost: function (id_list = []) {
    //寻物启事帖，除了预寻回的可任意删除
    let status = this.data.check_status_id;
    if (status == 1) {
      //待归还的帖子
      app.alert({
        title: '删除提示',
        content: "很遗憾，暂无人拾到归还，确定不再等等？",
        showCancel: true,
        cb_confirm: () => {
          //批量删除
          this.doDeleteSelected(id_list)
        },
        cb_cancel: this.editTap
      })
    } else if (status == 3 || status == 4) {
      //已取回和已答谢的
      app.alert({
        title: '删除提示',
        content: (status == 3 ? '还未答谢，' : '') + '确认删除？',
        showCancel: true,
        cb_confirm: () => {
          //批量删除
          app.alert({
            title: '智能清理',
            content: '是否同步清除寻物贴对应的归还通知？',
            showCancel: true,
            cb_confirm: () => {
              this.doDeleteSelected(id_list);
              deleteLinkReturnGoods(id_list);
            },
            cb_cancel: () => {
              this.doDeleteSelected(id_list);
            }
          })
        },
        cb_cancel: this.editTap
      })
    }
  },
  /**
   * doDeleteSelected 纯粹的批量删除操作
   */
  doDeleteSelected: function (id_list = []) {
    wx.request({
      url: app.buildUrl("/record/delete"),
      header: app.getRequestHeader(),
      data: {
        op_status: this.data.op_status,
        id_list: id_list,
        status: this.data.check_status_id,
        biz_type: this.data.business_type
      },
      success: (res) => {
        let resp = res.data;
        if (resp['code'] !== 200) {
          app.alert({
            'content': resp['msg']
          });
          return
        }
        //关闭编辑栏
        this.editTap();
        //刷新
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
  /**
   * checkReportClick 举报选项卡切换
   * @param e
   */
  checkReportClick: function (e) {
    //选择一次分类时返回选中值
    let status = e.currentTarget.id * 1
    let infos = this.data.infos;
    infos.check_status_id = status;
    this.setData({
      infos: infos,
      check_status_id: status
    });
    this.onPullDownRefresh();
  },
  /**
   * radioChange 查看推荐推送时，修改了仅新增选项后进行筛选
   */
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
  /**
   * businessTypeClick 失物招领 <——> 寻物启事 <——> 归还帖
   */
  businessTypeClick: function () {
    let infos = this.data.infos;
    let business_type = this.data.business_type;
    if (business_type === 0) {
      //寻-->失
      infos.check_cat = [
        {
          id: 1,
          name: '待认领'
        },
        {
          id: 2,
          name: '预认领',
        },
        {
          id: 3,
          name: '已认领',
        },
        {
          id: 4,
          name: '已答谢'
        },
        {
          id: 5,
          name: '申诉中'
        }];
      business_type = 1
    } else if (business_type === 1) {
      //失->还
      infos.check_cat = [
        {
          id: 0,
          name: '已拒绝'
        },
        {
          id: 1,
          name: '待确认'
        },
        {
          id: 2,
          name: '待取回',
        },
        {
          id: 3,
          name: '已取回',
        },
        {
          id: 4,
          name: '已答谢'
        }];
      business_type = 2
    } else {
      //还->寻
      infos.check_cat = [
        {
          id: 1,
          name: '待寻回'
        },
        {
          id: 2,
          name: '预寻回',
        },
        {
          id: 3,
          name: '已寻回',
        },
        {
          id: 4,
          name: '已答谢',
        }
      ];
      business_type = 0
    }
    infos.check_status_id = 1;
    //设置选项栏和业务类型
    this.setData({
      check_status_id: 1,
      infos: infos,
      business_type: business_type
    });
    //重新加载页面
    this.onPullDownRefresh();
  },
  /**
   * 状态栏的切换
   * @param e
   */
  recordTypeClick: function (e) {
    let infos = this.data.infos;
    let old_id = infos.check_status_id;
    let new_id = e.currentTarget.id * 1;
    if (old_id !== new_id) {
      // 切换了新的状态，重新加载数据
      infos.check_status_id = new_id;
      this.setData({
        infos: infos,
        check_status_id: e.currentTarget.id
      });
      this.onPullDownRefresh();
    }
  }
});