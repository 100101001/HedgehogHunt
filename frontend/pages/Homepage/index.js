const navigate = require("../template/navigate-bar/navigate-bar-template.js");
const util = require("../../utils/util.js");
const app = getApp();



/**
 * simpleMemberInfo 用户是否有二维码
 * @param cb_complete
 */
const simpleMemberInfo = function (cb_complete=()=>{}) {
  wx.request({
    url: app.buildUrl("/member/simple/info"),
    header: app.getRequestHeader(),
    success: (res) => {
      cb_complete(res.data['data'])
    }, fail: (res) => {
      app.serverBusy();
    }
  })
};

// pages/Homepage/index.js
Page({

  /**
   * 页面的初始数据
   */
  data: {
    navigators : [
      {
        label: '我的发布',
        url: '/pages/Record/index?op_status=0'
      },
      {
        label: '我的认领',
        url: '/pages/Record/index?op_status=1'
      },
      {
        label: '推荐我的',
        url: '/pages/Record/index?op_status=2'
      },
      {
        label: '归还我的',
        url: '/pages/Record/index?op_status=5'
      },
      {
        label: "我的答谢",
        url: '/pages/Thanks/record/index?op_status=3'
      },
      {
        label: "我的购物",
        url: '/mall/pages/my/index'
      }
    ],
    activities: [
      {
        name: '关注公众号，获悉校园拾物动态',
        img: '/',
        nav: '立刻关注',
        act: "goSubscribeOfficial"
      },
      {
        name: "邀请好友获取二维码，领取现金红包",
        img: '/',
        nav: '立刻邀请',
        act: "goInvite"
      },
      {
        name: "购买二维码，享受失物闪寻",
        img: '/',
        nav: '立刻购买',
        act: "goBuy"
      }
    ]
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad: function (options) {

  },

  /**
   * 生命周期函数--监听页面初次渲染完成
   */
  onReady: function () {

  },

  /**
   * 生命周期函数--监听页面显示
   */
  onShow: function () {
    // 导航栏
    this.setNavigationBar();
    //
  },
  /**
   * 导航栏(浮窗)设置
   */
  setNavigationBar: function(){
    let [isSelecteds, urls] = util.onNavigateTap();  //不传值代表没有页被选中
    isSelecteds['showHintQrcode'] = app.globalData.showHintQrcode;  //用户有没有关闭
    isSelecteds['regFlag'] = app.globalData.regFlag;  //用户注册
    this.setData({
      isSelecteds: isSelecteds
    });
    this.setUserInfo(isSelecteds['regFlag']);
  },
  /**
   * 设置用户身份信息（已注册和未主册都要）
   */
  setUserInfo: function (regFlag=false) {
    if (!regFlag) {
      //未注册，设置默认头像
      let userInfo = app.globalData.unRegUserInfo;
      this.setData({
        total_new: 0,
        hasQrcode: userInfo['has_qr_code'],
        userInfo: userInfo
      })
    } else {
      // 注册后端获取
      util.getNewRecommend((data) => {
        this.setData({
          total_new: data.total_new
        })
      });
      let call_back = (userInfo) => {
        this.setData({
          hasQrcode: userInfo['has_qr_code'],
          userInfo: userInfo
        })
      };
      //已经注册了获取用户信息
      simpleMemberInfo(call_back)
    }
  },
  /**
   * 快速跳转"我的","购物"页面
   */
  quickLink: function (e){
    if(!app.loginTip()){
      return;
    }
    wx.showLoading({title:'正在跳转'});
    wx.navigateTo({
      url: e.currentTarget.dataset.url,
      success : res=> {
        setTimeout(wx.hideLoading, 300)
      }
    })
  },
  /**
   * 生命周期函数--监听页面隐藏
   */
  onHide: function () {

  },

  /**
   * 生命周期函数--监听页面卸载
   */
  onUnload: function () {

  },

  /**
   * 页面相关事件处理函数--监听用户下拉动作
   */
  onPullDownRefresh: function () {

  },

  /**
   * 页面上拉触底事件的处理函数
   */
  onReachBottom: function () {

  },

  /**
   * 用户点击右上角分享
   */
  onShareAppMessage: function () {

  },
  //点击导航
  onNavigateTap: function (event) {
    navigate.onNavigateTap(event, this)
  },
  tapOnHint: function(e){
    navigate.tapOnHint(this)
  },
  closeQrcodeHint: function (e) {
    navigate.closeQrcodeHint(this)
  },
  toSeeQrcode: function () {
    navigate.toSeeQrcode(this)
  },
  toGetQrcode: function () {
    navigate.toGetQrcode(this)
  },
  toLogin: function () {
    navigate.toLogin(this)
  }
})