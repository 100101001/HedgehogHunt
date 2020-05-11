const navigate = require("../template/navigate-bar/navigate-bar-template.js");
const util = require("../../utils/util.js");
const app = getApp();



/**
 * simpleMemberInfo 用户是否有二维码
 * @param cb_complete
 * @param cb_fail  服务器无响应时，设置为默认的用户信息
 */
const simpleMemberInfo = function (cb_complete=()=>{}, cb_fail=()=>{}) {
  wx.request({
    url: app.buildUrl("/member/simple/info"),
    header: app.getRequestHeader(),
    success: (res) => {
      let resp = res.data;
      if (resp['code']!==200) {
        cb_fail()
        app.alert({content: resp['msg']});
        return
      }
      cb_complete(res.data['data'])
    }, fail: (res) => {
      app.serverBusy();
      cb_fail()
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
    getLaunchOptionsSyncArr: [1047, 1124, 1089, 1038, 1011, 1017], //公众号关注组件显示的场景值
    activities: [
      {
        slogans: ['关注公众号', '获悉校园拾物动态'],
        img: '/images/more/target.png',
        nav: '立刻关注 >',
        act: 'goSubscribeOfficial',
        url: '',
      },
      {
        slogans: ['购买寻物码', '享受失物闪寻'],
        img: '/images/more/qrcode.png',
        nav: '立刻购买 >',
        act: "goBuy",
        url: "/pages/Mine/userinfo/index"
      },
      {
        slogans: ['邀请好友获取寻物码', '领取现金红包'],
        img: '/images/more/invite.png',
        nav: '立刻邀请 >',
        act: "goInvite",
        url: ''
      },
    ],
    has_subscribe: true,
    invite_tutorial_hidden: true,
    subscribe_hidden: true
  },
  execute: function(method_name='') {
    let methods_map = {'goInvite': this.goInvite,
                       'goSubscribeOfficial': this.openSubscribe
                      };
    methods_map[method_name]()
  },
  clickNav: function(e){
    let target = this.data.activities[e.currentTarget.dataset.id];
    if (target.url) {
      wx.showLoading({title: '跳转中', success: res => {setTimeout(wx.hideLoading, 500)}});
      wx.navigateTo({url: target.url});
    } else {
      this.execute(target.act)
    }
  },
  openSubscribe: function() {
    this.setData({
      subscribe_hidden: false,
    })
  },
  closeSubscribe: function(){
    this.setData({
      subscribe_hidden: true
    })
  },
  closeAndRemoveActivity: function(){
    if(this.data.has_subscribe) {
      this.data.activities.splice(0, 1);
      this.setData({
        has_subscribe: false,
        activities: this.data.activities,
        load_ok: true
      });
    }
  },
  keepActivity: function () {
    this.setData({
      load_ok: true
    });
  },
  goInvite: function() {
    this.setData({
      invite_tutorial_hidden: false
    })
    setTimeout(this.closeInvite, 3500)
  },
  closeInvite: function(){
    this.setData({
      invite_tutorial_hidden: true
    })
  },
  setInitActivityData: function(){
    this.closeSubscribe();
    this.closeInvite();
  },
  /**
   * 生命周期函数--监听页面加载
   */
  onLoad: function (options) {
    // let obj = wx.getLaunchOptionsSync();//获取当前小程序的场景值
    // if(!this.data.getLaunchOptionsSyncArr.includes(obj.scene)) {
    //   this.data.activities.splice(0, 1);
    //   this.setData({
    //     activities: this.data.activities
    //   })
    // }
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
    this.setInitActivityData();
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
      this.setDefaultUserInfo()
    } else {
      // 注册后端获取
      util.getNewRecommend((data) => {
        this.setData({
          total_new: data.total_new
        })
      });
      let cb_complete = (userInfo) => {
        this.setData({
          hasQrcode: userInfo['has_qr_code'],
          userInfo: userInfo
        })
      };
      //已经注册了获取用户信息
      simpleMemberInfo(cb_complete, this.setDefaultUserInfo)
    }
  },
  setDefaultUserInfo: function(){
    let userInfo = app.globalData.unRegUserInfo;
    this.setData({
      total_new: 0,
      hasQrcode: userInfo['has_qr_code'],
      userInfo: userInfo
    })
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
    return {
      title: '快来鲟回失物招领获取你的专属寻物码吧',
      path: '/pages/Mine/userinfo/index',
      success: function (res) {
        wx.showToast({
          title: '分享成功！',
          icon: 'success',
          duration: 700
        })
      }
    }
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
});