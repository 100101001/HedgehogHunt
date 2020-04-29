// /controls/pages/index.js
const app = getApp();
Page({
  data: {
    items: [
      {
        label: "物品举报",
        icons: "/images/icons/next.png",
        act: "toCheckReport",
      },
      {
        label: "答谢举报",
        icons: "/images/icons/next.png",
        act: "toCheckThanksReport",
      },
      {
        label: "物品申诉",
        icons: "/images/icons/next.png",
        act: "toCheckGoodsAppeal",
      }
    ],
    items1: [
      {
        label: "添加管理员",
        icons: "/images/icons/next.png",
        act: "toAddAdm",
      },
      {
        label: "黑名单",
        icons: "/images/icons/next.png",
        act: "toCheckBlockMember",
      }
    ],
    items2: [
      {
        label: "反馈信息",
        icons: "/images/icons/next.png",
        act: "toCheckFeedback",
      },
      {
        label: "统计数据",
        icons: "/images/icons/next.png",
        act: "toCheckStat",
      }
    ]

  },
  onLoad: function (options) {
    this.setData({
      is_adm: app.globalData.is_adm
    })
  },
  // toReleaseAdv: function () {
  //   wx.navigateTo({
  //     url: '/pages/adv/release/adv-release',
  //   })
  // },
  /**
   * 添加管理员
   */
  toAddAdm: function () {
    wx.navigateTo({
      url: 'add_adm/index',
    })
  },
  /**
   * 物品举报
   */
  toCheckReport: function () {
    wx.navigateTo({
      url: '/pages/Record/index?op_status=4',
    })
  },
  /**
   * 检查申诉记录
   */
  toCheckGoodsAppeal: function () {
    wx.navigateTo({
      url: 'goods_appeal/index',
    })
  },
  /**
   * 答谢举报
   */
  toCheckThanksReport: function () {
    wx.navigateTo({
      url: '/pages/Thanks/record/index?op_status=4',
    })
  },
  /**
   * 数据统计
   */
  toCheckStat: function () {
    wx.navigateTo({
      url: 'static/index',
    })
  },
  /**
   * 反馈检查
   */
  toCheckFeedback: function () {
    wx.navigateTo({
      url: 'feedback_msg/index',
    })
  },
  /**
   * 会员黑名单
   */
  toCheckBlockMember: function () {
    wx.navigateTo({
      url: 'blockmember/blockmember',
    })
  }
});