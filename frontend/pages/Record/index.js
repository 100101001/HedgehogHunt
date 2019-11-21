var goodsData = require("../../data/posts-data.js");
var util = require("../../utils/util.js");
var app = getApp();
Page({
  data: {
    name: "",
    type: "",
    banners: ["/images/goods/camera.jpg", "/images/goods/ear_phone.jpg"],
    activeCategoryId: -1,
    saveHidden: true
  },

  onLoad: function(options) {
    var goodsList = goodsData.goodsList;
    //截取前14个字当做概况
    for (var i in goodsList) {
      goodsList[i].content = goodsList[i].summary.substring(0, 27) + "...";
    }
    //设置底部导航栏
    var [isSelecteds, urls] = util.onNavigateTap(1);
    var cat_ori = [{
      id: -1,
      name: '全部'
    }];
    var cat_all = app.globalData.objectArray;
    var cats = cat_ori.concat(cat_all);
    this.setData({
      isSelecteds: isSelecteds,
      list: goodsList,
      name: "",
      type: "",
      searchShow: true,
      categories: cats,
    })
  },
  //点击信息卡查看详情
  onDetailTap: function(event) {
    var id = event.currentTarget.dataset.id;
    var saveHidden=this.data.saveHidden;
    if(!saveHidden){
      app.alert({
        'content':"请先完成编辑再查看详情~"
      });
    }else{
    wx.navigateTo({
      url: 'info/info',
    })
    }
  },
  //下拉刷新
  onPullDownRefresh: function(event) {
    util.showMessage("下拉刷新函数", "已经写好");
    wx.stopPullDownRefresh();
  },

  //上滑加载
  onReachBottom: function(event) {
    util.showMessage("上滑加载", "已经写好");
  },

  selectTap: function(e) {
    var index = e.currentTarget.dataset.index;
    var list = this.data.list;
    if (index !== "" && index != null) {
      list[index].selected = !list[index].selected;
      this.setPageData(this.getSaveHide(), this.allSelect(), this.noSelect(), list);
    }
  },
  //计算是否全选了
  allSelect: function() {
    var list = this.data.list;
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
    var list = this.data.list;
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
    var currentAllSelect = this.data.allSelect;
    var list = this.data.list;
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
    var list = this.data.list;
    for (var i = 0; i < list.length; i++) {
      var curItem = list[i];
      curItem.active = false;
    }
    this.setPageData(!this.getSaveHide(), this.allSelect(), this.noSelect(), list);
  },
  //选中完成默认全选
  saveTap: function() {
    var list = this.data.list;
    for (var i = 0; i < list.length; i++) {
      var curItem = list[i];
      curItem.active = true;
    }
    this.setPageData(!this.getSaveHide(), this.allSelect(), this.noSelect(), list);
  },
  getSaveHide: function() {
    return this.data.saveHidden;
  },
  setPageData: function(saveHidden, allSelect, noSelect, list) {
    this.setData({
      list: list,
      saveHidden: saveHidden,
      allSelect: allSelect,
      noSelect: noSelect,
    });
  },
  //选中删除的数据
  deleteSelected: function() {
    var list = this.data.list;
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
})