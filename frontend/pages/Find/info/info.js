//index.js
//获取应用实例
var app = getApp();
Page({
  data: {
    loadingHidden: true,
    show_location: false,
    appLoadingHidden: true
  },
  onShareAppMessage: function (Options) {
    var business_type = this.data.info.business_type;
    if (business_type == 1) {
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
    var goods_id = options.goods_id;
    var op_status = app.globalData.op_status;
    this.setData({
      appLoadingHidden: true,
      op_status: op_status,
      goods_id: goods_id
    })
  },
  onShow: function () {
    var regFlag = app.globalData.regFlag;
    this.setData({regFlag: regFlag})
    if (this.data.op_status == 4) {
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
      },
      success: function (res) {
        var resp = res.data;
        if (resp.code !== 200) {
          app.alert({
            'content': resp.msg
          });
          return;
        }
        //更新全局的新推荐数
        app.getNewRecommend()
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
    var regFlag = app.globalData.regFlag;
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
              wx.hideLoading();
              wx.showToast({
                title: '系统繁忙，反馈失败！',
                duration: 2000
              });
              app.serverBusy();
              return;
            }
          });
          wx.navigateBack();
        }
      }
    });
  },
  goHome: function (e) {
    wx.reLaunch({
      url: "../../Find/Find?business_type=1",
    })
  },
  goRelease: function (e) {
    if (!app.loginTip()) {
      return;
    }
    wx.navigateTo({
      url: "../../Release/release/index",
    })
  },
  //归还按钮
  goReturn: function (e) {
    var auther_id = this.data.infos.info.auther_id;
    var info = this.data.infos.info;
    app.globalData.info = info;
    wx.navigateTo({
      url: "../../Release/release/index?auther_id=" + auther_id,
    })
  },
  //归还按钮
  goThanks: function (e) {
    var is_auth = this.data.infos.info.is_auth;
    if (is_auth) {
      app.alert({
        'content': "发布者不可操作自己的记录"
      })
      return;
    }
    var info = this.data.infos.info;
    var data = {
      "auther_id": info.auther_id,
      "goods_id": info.id,
      "business_type": info.business_type,
      "goods_name": info.goods_name,
      "auther_name": info.auther_name,
      "updated_time": info.updated_time,
      "avatar": info.avatar
    }
    data = JSON.stringify(data);
    // data=JSON.parse(data) 将字符串转换成json格式
    wx.navigateTo({
      url: "../../Thanks/index?data=" + data,
    })
  },
  //申领的按钮
  toApplicate: function () {
    var that = this;
    if (!app.loginTip()) {
      return;
    }
    //TODO:发布者看不到认领按钮（或者禁止按键）
    var is_auth = that.data.infos.info.is_auth;
    if (is_auth) {
      app.alert({
        'content': "发布者不可认领自己捡到的物品"
      })
      return;
    }
    //防止重复申领
    var show_location = that.data.infos.show_location;
    if (show_location) {
      if (this.data.infos.info.business_type == 1) {
        var content = "您已认领过物品,请到对应地址取回物品";
      } else {
        var content = "您已归还过物品,请勿重复操作";
      }
      app.alert({
        'content': content
      })
      return;
    }
    // 认领确认
    wx.showModal({
      title: '提示',
      content: '申领后会在平台留下个人信息备查，是否确定申领？',
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
        })
        app.alert({
          'content': "认领成功，可到 【我的】——【认寻记录】 中查看"
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
    if (!app.globalData.regFlag) {
      app.loginTip()
      return
    }
    if (this.data.infos.info.is_auth) {
      app.alert({
        'content': "发布者不可操作自己的记录"
      })
      return
    }
    wx.showModal({
      title: '提示',
      content: '恭喜取回物品，是否确定取回了物品？',
      success: (res) => {
        if (res.confirm) {
          this.setData({
            loadingHidden: false
          })
          wx.request({
            url: app.buildUrl("/goods/gotback"),
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
              })
              app.alert({
                'content': "记得答谢发布者哦~"
              })
            },
            fail:  (res) => {
              app.serverBusy()
            },
            complete:  (res) => {
              this.setData({
                loadingHidden: true
              });
            },
          })
        }
      },
    })
  },
  previewItemImage: function (e) {
    var index = e.currentTarget.dataset.index;
    wx.previewImage({
      current: this.data.infos.info.pics[index], // 当前显示图片的http链接
      urls: this.data.infos.info.pics // 需要预览的图片http链接列表
    })
  },
  toEdit: function (event) {
    var info = this.data.infos.info;
    app.globalData.info = info;
    wx.navigateTo({
      url: '../edit/edit',
    })
  },
});