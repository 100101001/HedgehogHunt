var goodsData = require("../../data/posts-data.js");
var util = require("../../utils/util.js");
Page({
  data: {
    name: "",
    type: ""
  },

  //点击搜索框的取消键
  onCancelTap: function(event) {
    this.setData({
      messageCardShow: true,
      searchPanelShow: false,
      name: "",
      type: ""
    })
  },

  onLoad: function(options) {
    var typeArray = [{
        type: "钱包",
        id: 0
      },
      {
        type: "钥匙",
        id: 1
      },
      {
        type: "校园卡",
        id: 2
      },
      {
        type: "U盘",
        id: 3
      },
    ];
    var nameArray = [{
        name: "韦朝旭",
        id: 0
      },
      {
        name: "路飞",
        id: 1
      },
      {
        name: "XX",
        id: 2
      },
    ];

    var goodsList = goodsData.goodsList;

    //截取前14个字当做概况
    for (var i in goodsList) {
      goodsList[i].content = goodsList[i].goodsDetail.substring(0, 14) + "...";
    }
    //设置底部导航栏
    var [isSelecteds,urls]=util.onNavigateTap(1);
    this.setData({
      isSelecteds: isSelecteds,
      goodsList: goodsList,
      typeArray: typeArray,
      nameArray: nameArray,
      messageCardShow: true,
      searchPanelShow: false,
      name: "",
      type: "",
      searchShow: true,
    })
  },

  //点击搜索按钮或者点击键盘完成键
  onBindNameInput: function(event) {
    this.setData({
      searchName:event.detail.value
    })
  },
  onBindGoodsTypeInput: function (event) {
    this.setData({
      searchGoodsType: event.detail.value
    })
  },

  onBindConfirm:function(event){
    util.showMessage('获取值',this.data.searchName+"和"+this.data.searchGoodsType);
  },

  //点击名字搜索历史
  onNameChooseTap: function(event) {
    var id = event.currentTarget.dataset.id;
    var name = this.data.nameArray[id].name;
    this.setData({
      name: name,
      searchName:name
    })
  },

  //点击物品搜索历史
  onTypeChooseTap: function(event) {
    var id = event.currentTarget.dataset.id;
    var type = this.data.typeArray[id].type;
    this.setData({
      type: type,
      searchGoodsType:type
    })
  },

  //点击输入框
  onBindFocus: function(event) {
    this.setData({
      messageCardShow: false,
      searchPanelShow: true,
    })
  },

  //点击信息卡查看详情
  onDetailTap: function(event) {
    var id = event.currentTarget.dataset.id;
    wx.navigateTo({
      url: 'Find-detail/Find-detail?id=' + id,
    })
  },

  //点击联系之后
  onConnectTap: function(event) {
    util.showMessage('点击联系', '需要让用户自己联系吗？存在诈骗风险');
  },

  onShareTap: function(event) {
    var itemList = [
      "分享给微信好友",
      "分享到朋友圈",
      "分享到QQ",
      "分享到微博"
    ]
    wx.showActionSheet({
      itemList: itemList,
      itemColor: "#405f80",
      success: function(res) {
        //res.cancel
        //res.tapIndex
        util.showMessage('用户 ' + itemList[res.tapIndex], res.cancel ? "取消分享" : "分享成功");
      }
    })
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

  onScroll: function(event) {
    var deltaY = event.detail.deltaY;
    if (deltaY <= 0) {
      var serchShow = false
    } else {
      var serchShow = true
    }
    this.setData({
      searchShow: serchShow
    })
  },
  
  //点击导航图标
  onNavigateTap: function(event) {
    var id = event.currentTarget.dataset.id*1;//乘1强制转换成数字
    var [isSelecteds,urls]= util.onNavigateTap(id,2);
    this.setData({
      isSelecteds:isSelecteds
    })
    wx.redirectTo({
      url: urls[id],
    })
  }
})