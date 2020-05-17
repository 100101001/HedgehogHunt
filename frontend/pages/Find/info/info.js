//index.js
//获取应用实例
const app = getApp();
const globalData = app.globalData;
const util = require('../../../utils/util');

/**
 * doCancelReturnGoods  待确认时，取消归还{@link cancelReturnGoods}时，选择直接删除归还帖子
 * @param goods_id
 * @param status
 */
const doCancelReturnGoods = function (goods_id = 0, status= 2) {
  wx.request({
    url: app.buildUrl('/goods/return/cancel'),
    header: app.getRequestHeader(),
    data: {
      ids: [goods_id],
      status: status
    },
    success: res => {
      let resp = res.data
      if (resp['code'] !== 200) {
        app.alert({content: resp['msg']})
        return
      }
      //直接回退
      app.alert({
        title: '操作提示',
        content: '取消成功，归还贴已删除',
        cb_confirm: wx.navigateBack
      })
    }
  })
};

/**
 * 因为对方的删帖
 * 只是删除归还（同时解除通知的链条(openid)）
 * 只是删除寻物
 * @param goods_ids
 * @param status
 * @param business_type
 */
const doDeleteMyRelease = function (goods_ids = [], status=3, business_type = 2) {
  wx.request({
    url: app.buildUrl('/record/delete'),
    header: app.getRequestHeader(),
    data: {
      ids: [goods_ids],
      biz_type: business_type,
      status: status,
      op_status: 0
    },
    success: res => {
      let resp = res.data
      if (resp['code'] !== 200) {
        app.alert({content: resp['msg']})
        return
      }
      //直接回退
      app.alert({
        title: '操作提示',
        content: '删除成功',
        cb_confirm: wx.navigateBack
      })
    },
    fail: res => {
      app.serverBusy()
    }
  })
};


/**
 * returnToFoundGoods 取消归还{@link cancelReturnGoods}时选择实际将帖子转成公开的失物招领
 * 或者被拒绝的归还去公开 {@link goReturnToFound}
 * @param goods_id
 */
const returnToFoundGoods = function (goods_id = 0, status = 0, biz_type=0) {
  wx.request({
    url: app.buildUrl('/goods/return/to/found'),
    header: app.getRequestHeader(),
    data: {
      id: [goods_id],
      biz_type: biz_type,
      status: status //标识待确认的，还是已拒绝的
    },
    success: res => {
      let resp = res.data
      if (resp['code'] !== 200) {
        app.alert({content: resp['msg']})
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
    }
  })
};

/**
 * fetchReturnGoodsInfo 在已寻回的帖子上操作进行答谢需要获取数据
 * @param return_goods_id
 * @param cb_success
 */
const fetchReturnGoodsInfo = function (return_goods_id = 0, cb_success = () => {}) {
  wx.request({
    url: app.buildUrl("/goods/pure/info"),
    header: app.getRequestHeader(),
    data: {
      id: return_goods_id
    },
    success: function (res) {
      let resp = res.data;
      if (resp['code'] !== 200) {
        app.alert({
          content: resp['msg']
        });
        return;
      }
      cb_success(resp['data']['info'])
    },
    fail: function (res) {
      app.serverBusy();
    }
  })
};


/**
 * hasReadGood
 * @param goods_id
 * @returns {boolean} 是否阅读过文章
 */
const hasReadGood = function (goods_id = 0) {
  let bf = app.globalData.read_goods;
  let read = bf.test(goods_id);
  if (!read) {
    bf.add(goods_id);
  }
  return read;
};

Page({
  data: {
    dataReady: false,
    hiddenThanks: true,
    loadingHidden: true,
    show_location: false,
    appLoadingHidden: true
  },
  /**
   * 页面分享
   * @param Options
   * @returns {{path: string, success: success, title: *}}
   */
  onShareAppMessage: function (Options) {
    let business_type = this.data.info.business_type;
    let type_name;
    let end;
    let start;
    if (business_type === 1) {
      type_name = "失物招领：" + this.data.info.goods_name;
      end = "有你或者你朋友丢失的东西吗？快来看看吧";
    } else {
      type_name = "寻物启事：" + this.data.info.goods_name;
      end = "你有看到过吗？帮忙看看吧";
    }
    let is_auth = this.data.info.is_auth;
    if (is_auth) {
      start = "我在【鲟回-失物招领】"
    } else {
      start = "有人在【鲟回-失物招领】"
    }
    let title_msg = start + type_name + end;
    return {
      title: title_msg,
      path: '/pages/index/index?goods_id=' + this.data.info.id,
      success: function (res) {
        wx.request({
          url: app.buildUrl('/member/share'),
          success: function (res) {
            wx.showToast({
              title: '分享成功！',
              icon: 'success',
              content: '积分+5',
              duration: 3000
            })
          },
          fail: function (res) {
            wx.showToast({
              title: '分享失败！',
              duration: 3000
            })
          }
        })
      }
    }
  },

  onLoad: function (options) {
    let goods_id = options.goods_id * 1;
    let op_status = options.op_status;
    op_status = op_status? op_status*1: -1;
    this.setData({
      appLoadingHidden: true, //申领中的加载loading图标
      op_status: op_status, //我的记录进入查看详情，可以得知是从什么记录过来的
      goods_id: goods_id,
      is_user: globalData.is_user
    })
  },
  onShow: function () {
    if (this.data.op_status === 4) {
      //管理员处理举报物品，获取举报信息
      this.getReportInfo(this.data.goods_id)
    } else {
      //一个用于普通阅读，另一个用于推荐操作
      this.getGoodsInfo(this.data.goods_id, hasReadGood(this.data.goods_id), this.data.op_status)
    }
  },
  /**
   * 打开地图进行导航
   */
  toNavigate: function (e) {
    let id = e.currentTarget.dataset.id * 1;
    let info = this.data.infos.info;
    let location = id === 1? info.location: info.os_location;
    console.log(id)
    wx.openLocation({ //​使用微信内置地图查看位置。
      latitude: location[2], //要去的纬度-地址
      longitude: location[3], //要去的经度-地址
      name: location[1],
      address: location[0],
    })
  },
  copyMobile: function(e) {
    wx.setClipboardData({
      data: e.currentTarget.dataset.mobile,
      success: res => {
        wx.showToast({
          title: '电话已复制',
        })
      }
    })
  },
  /**
   * 除了物品信息还需要举报信息
   * @param id
   */
  getReportInfo: function (id) {
    this.setData({
      loadingHidden: false
    });
    wx.request({
      url: app.buildUrl("/report/goods/info"),
      header: app.getRequestHeader(),
      data: {
        id: id  //被举报的物品ID
      },
      success: (res) => {
        let resp = res.data;
        if (resp['code'] !== 200) {
          app.alert({
            content: resp['msg']
          });
          return;
        }
        let data = resp['data'];
        this.setData({
          dataReady:true,
          infos: {
            info: data['info'],
            loadingHidden: true,
            show_location: true,
            report_auth_info: data['report_auth_info']
          }
        });
      },
      fail: (res) => {
        app.serverBusy();
      },
      complete: (res) => {
        this.setData({
          loadingHidden: true
        });
      },
    })
  },
  /**
   * 获取物品详情
   * @param id 物品id
   * @param read 是否已读
   * @param op_status 从归还通知，还是匹配推荐等记录栏过来的
   */
  getGoodsInfo: function (id, read = false, op_status = 0) {
    this.setData({
      loadingHidden: false
    });
    wx.request({
      url: app.buildUrl("/goods/info"),
      header: app.getRequestHeader(),
      data: {
        id: id,  //物品ID
        read: read ? 1 : 0,  // 是否已阅
        op_status: op_status  // 推荐已阅
      },
      success: (res) => {
        let resp = res.data;
        if (resp['code'] !== 200) {
          app.alert({
            content: resp['msg'],
            cb_confirm: wx.navigateBack
          });
          return;
        }
        let data = resp['data'];
        this.setData({
          dataReady:true,
          infos: {
            info: data.info,  //详情数据
            show_location: data.show_location  //是否能看地址
          }
        });
      },
      fail:  (res) => {
        app.serverBusy();
      },
      complete:  (res) => {
        this.setData({
          loadingHidden: true
        });
      }
    })
  },
  toDeleteReport: function(e){
    app.alert({
      content: '确认删除？',
      showCancel: true,
      cb_confirm: this.deleteReport
    })
  },
  /**
   * 删除举报
   * @param e
   */
  deleteReport: function(){
    wx.request({
      url: app.buildUrl('/report/goods/delete'),
      header: app.getRequestHeader(),
      data: {
        id_list: [this.data.goods_id],
        op_status: this.data.op_status // 4
      },
      success: (res) => {
        let resp = res.data;
        if (resp['code'] === 200) {
          app.alert({
            content: '删除成功',
            cb_confirm: wx.navigateBack
          })
        } else {
          app.alert({
            content: '删除失败，请稍后重试'
          })
        }
      },
      fail: (res) => {
        app.serverBusy()
      }
    })
  },
  /**
   * 处理举报 {@see doDealGoodsReport}
   */
  dealGoodsReport: function (e) {
    let content;
    let report_status = e.currentTarget.dataset.report_status * 1;
    if (report_status > 3) {
      content = '拉黑该用户代表默认本帖' + (report_status === 4 ? '无' : '') + '违规，此操作不可逆转，确认操作？'
    } else {
      content = '确认本帖' + (report_status === 2 ? '无' : '') + '违规？'
    }
    app.alert({
      title: '举报处理',
      content: content,
      showCancel: true,
      cb_confirm: () => {
        this.doDealGoodsReport(this.data.goods_id, report_status);
      }
    });
  },
  /**
   * 处理举报 {@link dealGoodsReport}
   */
  doDealGoodsReport: function (id=0, report_status=0) {
    wx.showLoading({
      title: '操作提交中..'
    });
    wx.request({
      url: app.buildUrl("/report/goods/deal"),
      header: app.getRequestHeader(),
      data: {
        id: id,
        report_status: report_status  //无违规 or 举报者block or 发布者block
      },
      success: function (res) {
        let resp = res.data;
        if (resp['code'] !== 200) {
          app.alert({
            content: resp['msg']
          });
          return
        }
        wx.showToast({
          title: '操作成功！',
          icon: 'success',
          duration: 1000,
          success: (res) => {
            setTimeout(wx.navigateBack, 700)
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
   * 一键举报{@see doReportGoods}
   * @param e
   */
  toReport: function (e) {
    if (!app.loginTip()) {
      return;
    }
    app.alert({
      title: "违规举报",
      content: "为维护平台环境，欢迎举报恶搞、诈骗、私人广告、色情等违规信息！同时，恶意举报将会被封号，请谨慎操作，确认举报？",
      showCancel: true,
      cb_confirm: ()=>{
        this.doReportGoods(e.currentTarget.dataset.id);
      }
    });
  },
  /**
   * doReportGoods
   * @param id
   */
  doReportGoods: function (id = 0) {
    wx.showLoading({
      title: '信息提交中..'
    });
    wx.request({
      url: app.buildUrl("/report/goods"),
      header: app.getRequestHeader(),
      data: {
        id: id,
        status: this.data.infos.info.status   //物品的状态，操作冲突检测
      },
      success: (res) => {
        let resp = res.data;
        if (resp['code'] !== 200) {
          app.alert({
            content: resp['msg'],
            cb_confirm: wx.navigateBack
          });
          return;
        }
        if (this.data.infos.info.business_type === 2 && this.data.infos.info.status < 3) {
          // 举报了未取回的归还物品
          app.alert({
            title: '举报成功',
            content: '您的物品将会重新被系统纳入匹配范围并等待他人主动归还，是否需要续订归还通知？',
            showCancel: true,
            cb_confirm: this.subscribeReturnMsg,
            cb_cancel: wx.navigateBack
          });
        } else {
          wx.showToast({
            title: '举报成功，感谢反馈！',
            icon: 'success',
            duration: 1000,
            success: (res) => {
              setTimeout(wx.navigateBack, 600);
            }
          });
        }
      },
      fail: (res) => {
        app.serverBusy();
      },
      complete: (res) => {
        wx.hideLoading();
      }
    });
  },
  goHome: function (e) {
    wx.navigateBack()
  },
  /**
   * 去发布
   * @param e
   */
  goRelease: function (e) {
    if (!app.loginTip()) {
      return
    }
    wx.navigateTo({
      url: "../../Release/release/index"
    })
  },
  /**
   * 归还 == 发布新的归还帖
   * @param e
   */
  goReturn: function (e) {
    app.alert({
      title: '归还确认',
      content: '恶意归还将被列入失信名单，并拉黑账户，确认你捡到了他/她的失物？',
      showCancel: true,
      cb_confirm: () => {
        wx.navigateTo({
          url: '../../Release/release/index?info=' + JSON.stringify(this.data.infos.info)   //智能填充归还贴的表单用
        })
      }
    });
  },
  /**
   * 已取回的三类帖子，都可一键去答谢{@see doGoThanks}
   * @param e
   */
  goThanks: function (e) {
    let info = this.data.infos.info;
    let business_type = info.business_type;
    if (business_type === 0) {
      //寻物启事答谢归还贴不可能被申诉
      fetchReturnGoodsInfo(info.return_goods_id, (goods_info) => {
        this.doGoThanks(goods_info)
      })
    } else if (business_type === 2) {
      //归还贴也不会遭到申诉
      this.doGoThanks(info)
    } else if (business_type === 1) {
      // 失物招领可能会遇到申诉
      util.checkGoodsStatus(this.data.goods_id, info.status,() => {
        this.doGoThanks(info);
      })
    }
  },
  /**
   * 去答谢 {@link goThanks}
   * @param info
   */
  doGoThanks: function (info = {}) {
    let data = {
      "auther_id": info.auther_id,
      "goods_id": info.id,
      "business_type": info.business_type,
      "goods_name": info.goods_name,
      "auther_name": info.auther_name,
      "owner_name": info.owner_name,
      "updated_time": info.updated_time,
      "avatar": info.avatar
    };
    wx.navigateTo({
      url: "../../Thanks/index?data=" + JSON.stringify(data)
    })
  },
  /**
   * 在线申领失物{@see doApplyGoods}
   */
  toApplicate: function () {
    if (!app.loginTip()) {
      //必须登录再操作
      return
    }
    app.alert({
      title: '提示',
      content: '申领后即便再取消申领也会在平台留下个人信息备查，确定申领？',
      showCancel: true,
      cb_confirm: () => {
        this.doApplyGoods(this.data.goods_id, this.data.infos.info.status)
      }
    })
  },
  /**
   * 在线申领失物{@link toApplicate}
   * @param id
   * @param status
   */
  doApplyGoods: function (id = 0, status = 1) {
    this.setData({
      appLoadingHidden: false  //申领中的loading图标
    });
    wx.request({
      url: app.buildUrl("/goods/apply"),
      header: app.getRequestHeader(),
      data: {
        id: id,
        status: status,   //物品状态，后台检测状态用
      },
      success: (res) => {
        let resp = res.data;
        if (resp['code'] !== 200) {
          app.alert({content: resp['msg']});
          return
        }
        this.getGoodsInfo(id);
        app.alert({
          title: '取回提示',
          content: "在线认领成功，请尽快前往放置地点取回，确认取回后可获奖励积分！"
        })
      },
      fail: (res) => {
        app.serverBusy();
      },
      complete: (res) => {
        this.setData({
          appLoadingHidden: true
        })
      },
    })
  },
  /**
   * 登录后操作
   * 确认取回 {@see doGotBack}
   */
  gotBack: function () {
    app.alert({
      title: '提示',
      content: '恭喜取回物品，是否确认取回？',
      showCancel: true,
      cb_confirm: () => {
          this.doGotBack(this.data.goods_id, this.data.infos.info.status)
      }
    })
  },
  /**
   * 确认取回认领的物品 {@link gotBack}
   * @param id
   * @param status
   */
  doGotBack: function (id = 0, status=2) {
    wx.request({
      url: app.buildUrl("/goods/gotback"),
      header: app.getRequestHeader(),
      data: {
        ids: [id],
        status: status   // 物品状态后台用于防冲突
      },
      success: (res) => {
        let resp = res.data;
        if (resp['code'] !== 200) {
          app.alert({content: resp['msg']});
          return
        }
        this.getGoodsInfo(id);
        app.alert({
          title: '答谢提示',
          content: "积分+5，记得答谢发布者哦~"
        })
      },
      fail: (res) => {
        app.serverBusy()
      }
    })
  },
  /**
   * 查看大图
   * @param e
   */
  previewItemImage: function (e) {
    wx.previewImage({
      current: this.data.infos.info.pics[e.currentTarget.dataset.index], // 当前显示图片的http链接
      urls: this.data.infos.info.pics // 需要预览的图片http链接列表
    })
  },
  /**
   * 编辑(1, 2可编辑)
   * @param event
   */
  toEdit: function (event) {
    // 编辑物品前，状态检查
    util.checkGoodsStatus(this.data.goods_id,  this.data.infos.info.status, (status) => {
      wx.navigateTo({
        url: '../edit/edit?info=' + JSON.stringify(this.data.infos.info),
      });
    });
  },
  /**
   * goAppeal 觉得他人拿错自己的失物，
   * @param e
   */
  goAppeal: function (e) {
    if (!app.loginTip()) {
      //登录后操作
      return
    }
    app.alert({
      title: '申诉提示',
      content: '确认是自己的物品被他人取走了？',
      showCancel: true,
      cb_confirm: () => {
        this.doAppeal(this.data.goods_id, this.data.infos.info.status);
      }
    })
  },
  /**
   * doAppeal 确认他人拿错后{@link goAppeal}，发起申诉
   * @param id
   * @param status
   */
  doAppeal: function (id = 0, status = 3) {
    wx.request({
      url: app.buildUrl('/goods/appeal'),
      header: app.getRequestHeader(),
      data: {
        id: id, // 物品ID
        status: status //答谢帖还是已取回，如果其看见的状态与后端不符合，则不操作
      },
      success: res => {
        let resp = res.data;
        if (resp['code'] !== 200) {
          app.alert({content: resp['msg']});
          return
        }
        app.alert({
          title: '申诉提示',
          content: '您的申诉已被接受，管理员将在一个工作日内与您取得联系，请保持联络方式畅通。',
          cb_confirm: () => {
            //处理前端视图
            this.getGoodsInfo(id)
          }
        })
      },
      fail: (res) => {
        app.serverBusy()
      }
    })
  },
  /**
   * goMyRelease 待状态，作者可以去查看自己其它的所有帖子
   */
  goMyRelease: function () {
    // 能看见这个按钮的一定已经登陆了
    let pages = getCurrentPages();
    if (pages.length > 1) {
      let page = pages[pages.length - 2];
      if (page.route === 'pages/Record/index' && page.data.op_status === 0) {
        //本来就从我发布的记录过来的
        wx.navigateBack()
      } else {
        //去链接帖子
        wx.navigateTo({
          url: '/pages/Record/index?op_status=0'
        })
      }
    }
  },
  /**
   * toSetTop 待状态的寻物启事，作者可以去一键置顶
   */
  toSetTop: function () {
    app.alert({
      title: '温馨提示',
      content: '置顶收费' + globalData.goodsTopPrice + '元，确认去置顶？',
      showCancel: true,
      cb_confirm: () => {
        wx.navigateTo({
          url: '../edit/edit?info=' + JSON.stringify(this.data.infos.info) + '&top=1',
        })
      }
    })
  },
  /**
   * goRejectReturnGoods 拒绝归还的帖子{@see doRejectReturnGoods}，不是自己的东西
   */
  goRejectReturnGoods: function () {
    app.alert({
      title: '拒绝提示',
      content: '归还将失效，确认不是您正在寻找的物品？',
      showCancel: true,
      cb_confirm: res => {
        this.doRejectReturnGoods(this.data.goods_id, this.data.infos.info.status)
      }
    })
  },
  /**
   * 归还贴中 确认不是自己的东西 {@link goRejectReturnGoods}
   * @param id
   * @param status
   */
  doRejectReturnGoods: function (id = 0, status=1) {
    wx.request({
      url: app.buildUrl('/goods/return/reject'),
      header: app.getRequestHeader(),
      data: {
        ids: [id],
        status: status  //状态CAS
      },
      success: (res) => {
        let resp = res.data;
        if (resp['code'] !== 200) {
          app.alert({content: resp['msg']});
          return
        }
        app.alert({
          title: '操作提示',
          content: '已拒绝归还。是否需要续订归还通知？',
          showCancel: true,
          cb_confirm: this.subscribeReturnMsg,
          cb_cancel: wx.navigateBack
        });
      },
      fail: res => {
        app.serverBusy()
      }
    });
  },
  /**
   * 续订消息
   */
  subscribeReturnMsg: function () {
    let tmpId =app.globalData.subscribe.return;
    wx.requestSubscribeMessage({
      tmplIds: [tmpId],
      complete: (sub_res) => {
        //订阅完归还消息后
        wx.showToast({
          title: sub_res[tmpId] === 'accept'? '续订成功': '定期来看看吧',
          success: (res) => {
            setTimeout(wx.navigateBack, 300)
          }
        });
      }
    });
  },
  /**
   * goConfirmReturnGoods 归还贴 ，确认归还的物品是自己的{@see doConfirmReturnGoods}
   */
  goConfirmReturnGoods: function () {
    app.alert({
      title: '确认提示',
      content: '确定是你的物品？',
      showCancel: true,
      cb_confirm: () => {
        this.doConfirmReturnGoods(this.data.goods_id, this.data.infos.info.status)
      },
    })
  },
  /**
   * doConfirmReturnGoods 确认归还的是自己的{@link goConfirmReturnGoods}
   * @param id
   */
  doConfirmReturnGoods: function (id = 0, status=1) {
    wx.request({
      url: app.buildUrl('/goods/return/confirm'),
      header: app.getRequestHeader(),
      data: {
        id: id,
        status: status //CAS
      },
      success: res => {
        let resp = res.data;
        if (resp['code'] !== 200) {
          app.alert({content: resp['msg']});
          return
        }
        this.getGoodsInfo(id);
        app.alert({title: '操作提示', content: '归还已确认。请尽快前往放置点取回，确认后可得奖励积分！'})
      },
      fail: (res) => {
        app.serverBusy()
      }
    })
  },
  /**
   * cancelApply 取消预认领操作{@see doCancelApply}
   */
  goCancelApply: function () {
    app.alert({
      title: '取消警示',
      content: '确认不是自己的？',
      showCancel: true,
      cb_confirm: () => {
        //确认取消
        this.doCancelApply(this.data.goods_id, this.data.infos.info.status);
      }
    })
  },
  /**
   * doCancelApply 取消认领{@link goCancelApply}
   * @param id
   * @param status
   */
  doCancelApply: function (id = 0, status= 0) {
    wx.request({
      url: app.buildUrl('/goods/cancel/apply'),
      header: app.getRequestHeader(),
      data: {
        ids: [id],
        status: status //状态CAS
      },
      success: (res) => {
        let resp = res.data;
        if (resp['code'] !== 200) {
          app.alert({title: '操作提示', content: resp['msg']});
          return
        }
        this.getGoodsInfo(id);
        app.alert({title: '取消成功', content: '系统将仍保留你的认领信息以查备。'})
      },
      fail: (res) => {
        app.serverBusy()
      }
    })
  },
  /**
   * cancelReturnGoods
   * 待确认的归还贴，归还者选择取消归还
   * 可删除{@see doCancelReturnGoods}
   * 可公开{@see returnToFoundGoods}
   */
  cancelReturnGoods: function () {
    let info = this.data.infos.info;
    app.alert({
      title: '取消提示',
      content: '确认你捡到的不是他/她的物品？',
      showCancel: true,
      cb_confirm: () => {
        wx.showActionSheet({
          itemList: ['公开归还贴', '删除归还贴'],
          success: (res) => {
            if (res.tapIndex === 0) {
              //公开归还贴
              app.alert({
                title: '公开提示',
                content: '确认转成公开的失物招领？',
                showCancel: true,
                cb_confirm: () => {
                  //把链接的自己发布的归还贴转成失物招领
                  returnToFoundGoods(info.return_goods_id, 1) //这里不能用info.status因为，info是寻物启事
                }
              })
            } else {
              //删除归还帖子
              app.alert({
                title: '删除提示',
                content: '确认删除？对方将无法查看归还贴',
                showCancel: true,
                cb_confirm: () => {
                  //把自己发布的归还贴删除
                  doCancelReturnGoods(info.return_goods_id, 1) //这里不能用info.status因为，info是寻物启事
                }
              })
            }
          }
        })
      }
    })
  },
  /**
   * 因为对帖（寻物）已删除，所以提示可以删除已取回的归还贴
   */
  goDeleteGotbackReturn: function () {
    app.alert({
      title: '清理提示',
      content: '是否也删除本帖？',
      showCancel: true,
      cb_confirm: () => {
        doDeleteMyRelease(this.data.goods_id, this.data.infos.info.status, this.data.infos.info.business_type)
      }
    })
  },
  /**
   * checkReturnGoods 寻物启事查看链接的归还贴，归还贴查看链接的寻物启事
   */
  goCheckReturnGoods: function (e) {
    let pages = getCurrentPages();
    if (pages.length > 1) {
      let page = pages[pages.length - 2];
      if (page.route === 'pages/Find/info/info' && page.data.goods_id === this.data.infos.info.return_goods_id) {
        //本来就从链接帖子过来的
        wx.navigateBack()
      } else {
        //去链接帖子
        wx.navigateTo({
          url: '/pages/Find/info/info?goods_id=' + e.currentTarget.dataset.id
        })
      }
    }
  },
  /**
   * gotBackReturnGoods 确认取回该归还贴{@see doGotbackReturnGoods}
   */
  gotBackReturnGoods: function () {
    app.alert({
      title: '操作提示',
      content: '恭喜取回物品，是否确认取回？',
      showCancel: true,
      cb_confirm: () => {
        this.doGotbackReturnGoods(this.data.goods_id, this.data.infos.info.status, this.data.infos.info.business_type)
      }
    });
  },
  /**
   * doGotbackReturnGoods 确认取回归还帖{@link gotBackReturnGoods}
   * @param id 归还/寻物ID
   * @param status
   * @param biz_type 帖子类型：寻物或归还贴
   */
  doGotbackReturnGoods: function (id = 0, status=2, biz_type = 2) {
    // 统一传入归还物品的ID
    wx.request({
      url: app.buildUrl('/goods/return/gotback'),
      header: app.getRequestHeader(),
      data: {
        ids: [id],
        biz_type: biz_type,
        status: status
      },
      success: (res) => {
        let resp = res.data;
        if (resp['code'] !== 200) {
          app.alert({content: resp['msg']});
          return
        }
        this.getGoodsInfo(this.data.goods_id);
        app.alert({title: '答谢提示', content: '积分+5，记得答谢发布者哦~'})
      },
      fail: (res) =>{
        app.serverBusy();
      }
    })
  },
  /**
   * goCheckSms 查看短信余额
   */
  goCheckSms: function () {
    wx.navigateTo({
      url: '/pages/Mine/userinfo/index'
    })
  },
  /**
   * goReturnToFound 已拒绝的归还去公开
   */
  goReturnToFound: function () {
    app.alert({
      title: '公开提示',
      content: '确认转成公开的失物招领？',
      showCancel: true,
      cb_confirm: res => {
        //转成失物招领
        returnToFoundGoods(this.data.goods_id, 0)
      }
    })
  },
  /**
   * goTips 状态描述区的点击提示语
   */
  goTips: function () {
    let info = this.data.infos.info;
    let status = info.status;
    let business_type = info.business_type;
    if (business_type === 2) {
      //归还贴
      if (status === 0) {
        //被拒绝了的归还贴
        app.alert({
          content: '别灰心，您可继续将归还贴公开，让真正的失主找到它~'
        })
      } else if (status === 3 || status === 4) {
        if (info.is_origin_deleted && status === 3) {
          //还未答谢就被删了帖的寻物启事
          app.alert({
            content: '别灰心，你的举手之劳帮失主找回了失物！系统已发放您奖励积分，可以兑换平台福利哟~'
          })
        } else if (!info.is_origin_deleted) {
          //未删除帖子
          app.alert({
            title: '认领详情',
            content: '失主于' + info.op_time + '线下取回了！'
          })
        }
      } else if (status === 2) {
        //被确认了的归还贴
        app.alert({
          title: '认领详情',
          content: '失主于' + info.op_time + '确认归还了！'
        })
      } else if (status === 1) {
        app.alert({
          title: '等待提示',
          content: '别着急，失主还没上线呢！'
        })
      }
    } else if (business_type === 1) {
      //失物招领贴
      if (status === 1) {
        app.alert({
          title: '等待提示',
          content: '别着急，失主还没发现自己丢了东西呢！'
        })
      } else if ((status === 2 || status === 3 || status === 4) && info.is_auth) {
        // 预认领了失物招领查看认领时间
        app.alert({
          title: '认领详情',
          content: '失主于' + info.op_time + (status === 2 ? '在线认领了！' : '线下取回了！')
        })
      } else if (status === 5) {
        //所有人能可见申诉帖的人可见
        app.alert({
          title: '申诉详情',
          content: '我们于' + info.op_time + '收到申诉，正在处理中。帖子正被冻结，您暂时无法进行任何操作。'
        })
      }
    } else if (business_type === 0) {
      //寻物贴
      if (status === 2) {
        //预归还
        if (!info.is_confirmed) {
          //寻物贴主人可见
          app.alert({
            title: '归还详情',
            content: '寻物于' + info.op_time + '被人拾到归还。'
          })
        }
      } else if (status === 3 || status === 4) {
        //归还者可见
        app.alert({
          title: '认领详情',
          content: '失主于' + info.op_time + '线下取回了！'
        })
      }
    }
  },
  /**
   * goDeleteGotbackLost 单纯删除已取回的寻物
   */
  goDeleteGotbackLost: function () {
    app.alert({
      title: '清理提示',
      content: '是否也删除本帖？',
      showCancel: true,
      cb_confirm: () => {
        doDeleteMyRelease(this.data.goods_id, this.data.infos.info.status, this.data.infos.info.business_type)
      }
    })
  },
  /**
   * goRejectRecommend 否认推荐
   * 只有在从推荐记录进入的时候才会有
   */
  goRejectRecommend: function () {
    app.alert({
      title: '否认提示',
      content: '确定不是你丢的？',
      showCancel: true,
      cb_confirm: this.doRejectRecommend
    });
  },
  /**
   * doRejectRecommend 续订消息，删除推荐
   */
  doRejectRecommend: function(){
    app.alert({
      title: '匹配失败',
      content: '别灰心，续订通知可实时获悉后续新的匹配！',
      cb_confirm: this.doSubscribeRecommend
    });
  },
  /**
   * doSubscribeRecommend 续订匹配通知，删除推荐记录
   */
  doSubscribeRecommend: function() {
    let tmp_id = app.globalData.subscribe.recommend;
    wx.requestSubscribeMessage({
      tmplIds: [tmp_id],
      complete: (sub_res) => {
        wx.request({
          url: app.buildUrl('/record/delete'),
          header: app.getRequestHeader(),
          data: {
            op_status: this.data.op_status,
            id_list: [this.data.goods_id],
          },
          success: (res) => {
            let resp = res.data;
            if (resp['code'] !== 200) {
              app.alert({
                content: resp['msg']
              });
              return;
            }
            app.alert({title:'订阅提示', content:sub_res[tmp_id] === 'accept'? '续订成功': '续订失败，定期来推荐记录看看吧', cb_confirm: wx.navigateBack})
          },
          fail: (res) => {
            app.serverBusy();
          },
        })
      }
    })
  },
  /**
   *
   * @param e
   */
  openThank: function (e) {
    this.setData({
      hiddenThanks: false,
      thanks: this.data.infos.info['thank_info']
    })
  },
  closeThanks: function (e) {
    this.setData({
      hiddenThanks: true,
      thanks: null
    })
  },
  statusExplain: function () {
    let info = this.data.infos.info;
    let status = info.status;
    let business_type = info.business_type;
    let show_location = info.show_location;
    let is_auth = info['is_auth'];
    let content = '';
    if (business_type === 1){
      if (!is_auth) {
        if (status === 1) {
          content = '还无人认领，如果是你丢的，赶紧认领吧~'
        } else if (status === 2) {
          content = show_location? '你已在线认领了，赶紧去取回来吧~': '他人已在线认领，如果是你的东西，你可以继续点击认领查看地址去取回。'
        } else if(status === 3) {
          content = show_location? '恭喜取回，快去答谢发布者吧~': '他人已取回，如果是你的东西，请赶紧申诉我们会第一时间处理！'
        } else if (status === 4) {
          content = show_location? '您的感谢是拾者归还的最大动力~': '他人已取回，如果是你的东西，请赶紧申诉我们会第一时间处理！'
        }
      } else {
        if (status === 1) {
          content = '请耐心等待失主认领~'
        } else if (status === 2) {
          content = '失主已在线认领了，正在前往取回~'
        } else if(status === 3) {
          content = '感谢您的举手之劳，失主已经取回了~'
        } else if (status === 4) {
          content = '感谢您的举手之劳，失主已经取回了~'
        }
      }
      if (status > 10) {
        content = "物品认领可能被冒领，正在申诉中！"
      }
    }
    else if (business_type === 0){
      if(!is_auth) {
        if (status === 1) {
          content = '还无人归还，如果你捡到了，赶紧归还吧~'
        } else {
          let is_returner = info['is_returner'];
          if (is_returner) {
            if (status === 2) {
              content = '请耐心等待失主确认并取回~'
            } else if(status === 3) {
              content = '感谢您的举手之劳，失主已经取回了~'
            } else if (status === 4) {
              content = is_auth? '您的感谢是拾者归还的最大动力~': '感谢您的举手之劳，失主已经取回了~'
            }
          } else {
            content = '失物已经收到了归还~'
          }
        }
      }
      else {
        if (status === 1) {
          content = '请耐心等待他人归还~'
        } else if (status === 2) {
          content ='有人归还了，赶紧确认获取回吧~'
        } else if(status === 3) {
          content = '恭喜取回，快去答谢发布者吧~'
        } else if (status === 4) {
          content = '您的感谢是拾者归还的最大动力~'
        }
      }
    } else if (business_type === 2) {
      if (status === 0) {
        content = '好像不是对方的物品哦，赶紧公开招领吧~'
      }
      else if (status === 1) {
        content = is_auth? '请耐心等待失主确认~': '快来确认是否是自己的失物~'
      } else if (status === 2) {
        content = is_auth? '失主已在线认领了，正在前往取回~': '快去放置地点取回失物吧~'
      } else if(status === 3) {
        content = is_auth? '感谢您的举手之劳，失主已经取回了~': '恭喜取回，快去答谢发布者吧~'
      } else if (status === 4) {
        content = is_auth?  '感谢您的举手之劳，失主已经取回了~' : '您的感谢是拾者归还的最大动力~'
      }
    }
    app.alert({
      title: '状态提示',
      content: content
    })
  }
});