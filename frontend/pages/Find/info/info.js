//index.js
//获取应用实例
const app = getApp();
const globalData = app.globalData

/**
 * doCancelReturnGoods  待确认时，取消归还{@link cancelReturnGoods}时，选择直接删除归还帖子
 * @param goods_id
 */
const doCancelReturnGoods = function(goods_id = 0){
  wx.request({
    url: app.buildUrl('/goods/return/cancel'),
    header: app.getRequestHeader(),
    data: {
      ids: [goods_id]
    },
    success: res => {
      let resp = res.data
      if(resp['code'] !== 200){
        app.alert({content:resp['msg']})
        return
      }
      //直接回退
      app.alert({
        title: '操作提示',
        content: '取消成功，归还贴已删除',
        cb_confirm: () => {
          wx.navigateBack()
        }
      })
    }
  })
};

/**
 * 因为对方的删帖
 * 只是删除归还（同时解除通知的链条(openid)）
 * 只是删除寻物
 * @param goods_id
 * @param business_type
 */
const doCleanReturnGoods = function (goods_id = 0, business_type=2) {
  wx.request({
    url: app.buildUrl('/goods/return/clean'),
    header: app.getRequestHeader(),
    data: {
      ids: [goods_id],
      biz_type: business_type
    },
    success: res => {
      let resp = res.data
      if(resp['code'] !== 200){
        app.alert({content:resp['msg']})
        return
      }
      //直接回退
      app.alert({
        title: '操作提示',
        content: '归还贴已删除',
        cb_confirm: () => {
          wx.navigateBack()
        }
      })
    },
    fail: res =>{
      app.serverBusy()
    }
  })
};


/**
 * returnToFoundGoods 取消归还{@link cancelReturnGoods}时选择实际将帖子转成公开的失物招领
 * 或者被拒绝的归还去公开 {@link goReturnToFound}
 * @param goods_id
 */
const returnToFoundGoods = function(goods_id=0){
  wx.request({
    url: app.buildUrl('/goods/return/to/found'),
    header: app.getRequestHeader(),
    data: {
      id: [goods_id]
    },
    success: res => {
      let resp = res.data
      if(resp['code'] !== 200){
        app.alert({content:resp['msg']})
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
 * @param goods_id
 */
const fetchReturnGoodsInfo  = function (return_goods_id=0, cb_success=()=>{}){
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


Page({
  data: {
    loadingHidden: true,
    show_location: false,
    appLoadingHidden: true
  },
  onShareAppMessage: function (Options) {
    let business_type = this.data.info.business_type;
    if (business_type === 1) {
      var type_name = "失物招领：" + this.data.info.goods_name;
      var end = "有你或者你朋友丢失的东西吗？快来看看吧";
    } else {
      var type_name = "寻物启事：" + this.data.info.goods_name;
      var end = "你有看到过吗？帮忙看看吧";
    }
    var is_auth = this.data.info.is_auth;
    if (is_auth) {
      var start = "我在【闪寻-失物招领】"
    } else {
      var start = "有人在【闪寻-失物招领】"
    }
    var title_msg = start + type_name + end;
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
    this.setData({
      appLoadingHidden: true,
      op_status: op_status,
      goods_id: goods_id
    })
  },
  onShow: function () {
    var regFlag = globalData.regFlag;
    this.setData({regFlag: regFlag})
    if (this.data.op_status === 4) {
      this.getReportInfo(this.data.goods_id)
    } else {
      this.getGoodsInfo(this.data.goods_id)
    }
  },
  //打开位置导航
  toNavigate: function () {
    var location = this.data.infos.info.location;
    wx.openLocation({ //​使用微信内置地图查看位置。
      latitude: location[2], //要去的纬度-地址
      longitude: location[3], //要去的经度-地址
      name: location[1],
      address: location[0],
    })
  },
  getReportInfo: function (id) {
    var that = this;
    that.setData({
      loadingHidden: false
    });
    wx.request({
      url: app.buildUrl("/report/goods-info"),
      header: app.getRequestHeader(),
      data: {
        id: id
      },
      success: function (res) {
        var resp = res.data;
        if (resp.code !== 200) {
          app.alert({
            'content': resp.msg
          });
          return;
        }
        var op_status = that.data.op_status;
        that.setData({
          //认领过的则直接显示地址
          //op_status是操作的代码，商品详情就是0
          infos: {
            info: resp.data.info,
            loadingHidden: true,
            show_location: resp.data.show_location,
            report_auth_info: resp.data.report_auth_info,
            op_status: op_status,
            report_id: resp.data.report_id
          },
          ids: resp.data.ids,
        });
      },
      fail: function (res) {
        app.serverBusy();
        return;
      },
      complete: function (res) {
        that.setData({
          loadingHidden: true
        });
      },
    })
  },
  getGoodsInfo: function (id) {
    var that = this;
    that.setData({
      loadingHidden: false
    });
    wx.request({
      url: app.buildUrl("/goods/info"),
      header: app.getRequestHeader(),
      data: {
        id: id,
        openid: app.getUserOpenId()
      },
      success: function (res) {
        let resp = res.data;
        if (resp.code !== 200) {
          app.alert({
            content: resp.msg,
            cb_confirm: ()=>{
              wx.navigateBack()
            }
          });
          return;
        }
        that.setData({
          //认领过的则直接显示地址
          //op_status是操作的代码，商品详情就是0
          infos: {
            info: resp.data.info,
            loadingHidden: true,
            show_location: resp.data.show_location,
          }
        });
      },
      fail: function (res) {
        app.serverBusy();
        return;
      },
      complete: function (res) {
        that.setData({
          loadingHidden: true
        });
      },
    })
  },
  //拉黑举报者
  toBlock: function (e) {
    var report_status = e.currentTarget.dataset.report_status;
    var that = this;
    var ids = that.data.ids;
    var data = {
      auther_id: ids['auther_id'],
      report_member_id: ids['report_member_id'],
      goods_id: ids['goods_id'],
      report_id: ids['report_id'],
      report_status: report_status
    };
    wx.request({
      url: app.buildUrl("/report/block"),
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
  toReport: function (e) {
    var regFlag = globalData.regFlag;
    if (!regFlag) {
      app.alert({
        "content": "没有授权登录，不能举报！请授权登录"
      });
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
              record_type: 1,
            },
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
                title: '举报成功，感谢反馈！',
                icon: 'success',
                duration: 2000
              });
            },
            fail: function (res) {
              wx.hideLoading()
              wx.showToast({
                title: '系统繁忙，反馈失败！',
                duration: 2000
              });
              app.serverBusy();
            }
          });
          wx.navigateBack()
        }
      }
    });
  },
  goHome: function (e) {
    wx.navigateBack()
  },
  goRelease: function (e) {
    if (!app.loginTip()) {
      return
    }
    wx.navigateTo({
      url: "../../Release/release/index"
    })
  },
  /**
   * 归还 == 发布新的失物招领帖子
   * @see getUserMemberId
   * @param e
   */
  goReturn: function (e) {
    wx.navigateTo({
      url: '../../Release/release/index?info=' + JSON.stringify(this.data.infos.info)
    })
  },
  //归还按钮
  goThanks: function (e) {
    if(this.data.business_type == 0){
      //先获取归还物品的信息
      fetchReturnGoodsInfo(this.data.infos.info.return_goods_id,(goods_info) => {
        this.doGoThanks(goods_info)
      })
    } else {
      this.doGoThanks(this.data.infos.info)
    }
  },
  /**
   *
   * @param info
   */
  doGoThanks: function(info={}){
    let data = {
      "auther_id": info.auther_id,
      "goods_id": info.id,
      "business_type": info.business_type,
      "goods_name": info.goods_name,
      "auther_name": info.auther_name,
      "owner_name": info.owner_name,
      "updated_time": info.updated_time,
      "avatar": info.avatar
    }
    wx.navigateTo({
      url: "../../Thanks/index?data=" + JSON.stringify(data)
    })
  },
  //申领的按钮
  toApplicate: function () {
    if (!app.loginTip()) {
      return
    }
    if (this.data.infos.info.is_auth) {
      app.alert({
        'content': "发布者不可认领自己捡到的物品"
      })
      return
    }
    //防止重复申领（申领过可见地址，所以可见地址代表已申领过了）
    if (this.data.infos.show_location) {
      if (this.data.infos.info.business_type == 1) {
        var content = "您已认领过物品,请到对应地址取回物品";
      } else {
        var content = "您已归还过物品,请勿重复操作";
      }
      app.alert({
        'content': content
      })
      return
    }
    // 认领确认
    wx.showModal({
      title: '提示',
      content: '申领后即便再取消申领也会在平台留下个人信息备查，确定申领？',
      success: (res) => {
        if (res.confirm) {
          this.setData({
            appLoadingHidden: false
          })
          this.applyGoods()
        }
      },
    })
  },
  applyGoods: function(){
    wx.request({
      url: app.buildUrl("/goods/applicate"),
      header: app.getRequestHeader(),
      data: {
        id: this.data.infos.info.id,
      },
      success:  (res) => {
        let resp = res.data;
        if (resp.code !== 200) {
          return
        }
        let infos = this.data.infos;
        infos['show_location'] = resp.data.show_location;
        infos.info.status_desc = resp.data.status_desc;
        infos.info.status = resp.data.status;
        this.setData({
          infos: infos
        });
        app.alert({
          title: '取回提示',
          content: "在线认领成功，请尽快前往放置地点取回，确认取回后可获奖励积分！"
        })
      },
      fail:  (res) => {
        app.serverBusy();
      },
      complete:  (res) => {
        this.setData({
          appLoadingHidden: true
        })
      },
    })
  },
  //已经取回的按钮
  gotBack: function () {
    if (!app.loginTip()) {
      return
    }
    if (this.data.infos.info.is_auth) {
      app.alert({
        'content': "发布者不可操作自己的记录"
      });
      return
    }
    wx.showModal({
      title: '提示',
      content: '恭喜取回物品，是否确认取回？',
      showCancel: true,
      success: (res) => {
        if (res.confirm) {
          this.doGotBack()
        }
      },
    })
  },
  doGotBack: function () {
    wx.request({
      url: app.buildUrl("/goods/gotback"),
      header: app.getRequestHeader(),
      data: {
        id: [this.data.infos.info.id],
      },
      success: (res) => {
        let resp = res.data;
        if (resp.code !== 200) {
          return
        }

        let infos = this.data.infos;
        infos['show_location'] = true;
        infos.info.status_desc = this.data.infos.info.business_type == 1? '已认领': '已取回';
        infos.info.status = 3;
        this.setData({
          infos: infos
        });
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
  previewItemImage: function (e) {
    wx.previewImage({
      current: this.data.infos.info.pics[e.currentTarget.dataset.index], // 当前显示图片的http链接
      urls: this.data.infos.info.pics // 需要预览的图片http链接列表
    })
  },
  toEdit: function (event) {
    wx.navigateTo({
      url: '../edit/edit?info=' + JSON.stringify(this.data.infos.info),
    })
  },
  /**
   * goAppeal 觉得他人拿错自己的失物，
   * @param e
   */
  goAppeal: function (e) {
    app.alert({
      title: '申诉提示',
      content: '确认是自己的物品被他人取走了？',
      showCancel: true,
      cb_confirm: ()=>{
        this.doAppeal()
      }
    })
  },
  /**
   * doAppeal 确认他人拿错后{@link goAppeal}，发起申诉
   */
  doAppeal: function () {
    wx.request({
      url: app.buildUrl('/goods/appeal'),
      header: app.getRequestHeader(),
      data: {
        id: this.data.goods_id // 物品ID
      },
      success: res => {
        let resp = res.data
        if(resp['code']!==200){
          app.alert({content: resp['msg']});
          return
        }
        app.alert({
          title:'申诉提示',
          content: '您的申诉已被接受，管理员将在一个工作日内与您取得联系，请保持联络方式畅通。',
          cb_confirm: ()=>{
            //处理前端视图
            this.getGoodsInfo(this.data.goods_id)
          }
        })
      },
      fail: res=>{
        app.serverBusy()
      }
    })
  },
  /**
   * goMyRelease 待状态，作者可以去查看自己其它的所有帖子
   */
  goMyRelease: function () {
    wx.navigateTo({
      url: '/pages/Record/index?op_status=0'
    })
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
   * goRejectReturnGoods 拒绝归还的帖子，不是自己的东西
   */
  goRejectReturnGoods: function () {
    app.alert({
      title: '拒绝提示',
      content: '归还将失效，确认不是您正在寻找的物品？',
      showCancel: true,
      cb_confirm: res=>{
        wx.request({
          url: app.buildUrl('/goods/return/reject'),
          header: app.getRequestHeader(),
          data: {
            id: [this.data.infos.info.id]
          },
          success: res => {
            let resp = res.data;
            if(resp['code'] !== 200) {
              app.alert({content: resp['msg']});
              return
            }
            app.alert({
              title: '操作提示',
              content:'已拒绝归还。望您早日寻回失物！',
              cb_confirm: ()=>{
                wx.navigateBack()
              }
            })
          },
          fail: res=>{
            app.serverBusy()
          }
        })
      }
    })
  },
  /**
   * goConfirmReturnGoods 确认归还的物品
   */
  goConfirmReturnGoods: function () {
    app.alert({
      title: '确认提示',
      content: '确定是你的物品？',
      showCancel: true,
      cb_confirm: ()=>{
        wx.request({
          url: app.buildUrl('/goods/return/confirm'),
          header: app.getRequestHeader(),
          data: {
            id: this.data.infos.info.id
          },
          success: res => {
            let resp = res.data;
            if(resp['code'] !== 200){
              app.alert({content:resp['msg']});
              return
            }
            this.getGoodsInfo(this.data.goods_id);
            app.alert({title: '操作提示', content:'归还已确认。请尽快前往放置点取回，确认后可得奖励积分！'})
          },
          fail: res=>{
            app.serverBusy()
          }
        })
      },
    })
  },
  /**
   * cancelApply 取消预认领操作
   */
  goCancelApply: function () {
    let id = this.data.goods_id
    app.alert({
      title: '取消警示',
      content: '确认不是自己的？',
      showCancel: true,
      cb_confirm: () =>{
        //确认取消
        wx.request({
          url: app.buildUrl('/goods/cancel/apply'),
          header: app.getRequestHeader(),
          data: {
            id: id
          },
          success: res => {
            let resp = res.data
            if(resp['code'] !== 200){
              app.alert({title:'操作提示', content:resp['msg']})
              return
            }
            this.getGoodsInfo(id)
            app.alert({'title':'取消成功', content: '系统将仍保留你的认领信息以查备。'})
          },
          fail: res=>{
            app.serverBusy()
          }
        })
      }
    })
  },
  /**
   * cancelReturnGoods 待确认的归还贴，归还者选择删除
   */
  cancelReturnGoods: function () {
    app.alert({
      title: '取消提示',
      content: '确认你捡到的不是他/她的物品？',
      showCancel: true,
      cb_confirm: ()=>{
        wx.showActionSheet({
          itemList: ['公开归还贴', '删除归还贴'],
          success: (res) => {
            if (res.tapIndex == 0) {
              //公开归还贴
              app.alert({
                title: '公开提示',
                content: '确认转成公开的失物招领？',
                showCancel: true,
                cb_confirm: res => {
                  //把链接的自己发布的归还贴转成失物招领
                  returnToFoundGoods(this.data.infos.info.return_goods_id)
                }
              })
            } else {
              //删除归还帖子
              app.alert({
                title: '删除提示',
                content: '确认删除？对方将无法查看归还贴',
                showCancel: true,
                cb_confirm: ()=>{
                  //把自己发布的归还贴删除
                  doCancelReturnGoods(this.data.infos.info.return_goods_id)
                }
              })
            }
          }
        })
      }
    })
  },
  goDeleteGotbackReturn: function () {
    app.alert({
      title: '清理提示',
      content: '是否也删除本帖？',
      showCancel: true,
      cb_confirm: () => {
        doCleanReturnGoods(this.data.goods_id, this.data.infos.info.business_type)
      }
    })
  },
  /**
   * checkReturnGoods 寻物启事查看链接的归还贴，归还贴查看链接的寻物启事
   */
  goCheckReturnGoods: function (e) {
    let pages = getCurrentPages()
    if (pages.length > 1) {
      let page = pages[pages.length - 2];
      if (page.route === 'pages/Find/info/info' && page.data.goods_id == this.data.infos.info.return_goods_id) {
        wx.navigateBack()
      } else {
        wx.navigateTo({
          url: '/pages/Find/info/info?goods_id=' + e.currentTarget.dataset.id
        })
      }
    }
  },
  /**
   * gotBackReturnGoods 确认取回该归还贴
   */
  gotBackReturnGoods: function () {
    app.alert({
      title: '操作提示',
      content: '恭喜取回物品，是否确认取回？',
      showCancel: true,
      cb_confirm: ()=>{
        this.doGotbackReturnGoods()
      }
    });
  },
  /**
   * doGotbackReturnGoods 确认取回归还帖
   */
  doGotbackReturnGoods: function () {
    // 统一传入归还物品的ID
    wx.request({
      url: app.buildUrl('/goods/return/gotback'),
      header: app.getRequestHeader(),
      data: {
        id: [this.data.goods_id],
        biz_type: this.data.infos.info.business_type
      },
      success: (res) => {
        let resp = res.data;
        if (resp['code'] !== 200) {
          app.alert({content: resp['msg']});
          return
        }
        this.getGoodsInfo(this.data.goods_id)
        app.alert({title:'答谢提示', content: '积分+5，记得答谢发布者哦~'})
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
        returnToFoundGoods(this.data.goods_id)
      }
    })
  },
  /**
   * goTips 状态描述区的点击提示语
   */
  goTips: function () {
    let status = this.data.infos.info.status;
    let business_type = this.data.infos.info.business_type;
    if (business_type == 2 && status == 0) {
      //被拒绝了的归还贴
      app.alert({
        content: '别灰心，您可继续将归还贴公开，让真正的失主找到它~'
      })
    } else if (business_type==2 && status == 3) {
      if(this.data.infos.info.is_origin_deleted && !this.data.infos.info.is_thanked) {
        app.alert({
          content: '别灰心，你的举手之劳帮失主找回了失物！系统已发放您奖励积分，可以兑换平台福利哟~'
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
        doCleanReturnGoods(this.data.goods_id, this.data.infos.info.business_type)
      }
    })
  }
});