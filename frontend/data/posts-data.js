var localDataBase = [{
    avatar: "/images/images/avatar/1.png",
    main_image: "https://img3.doubanio.com/view/photo/s_ratio_poster/public/p2546335362.jpg",
    id: 0,
    updated_time: "2019-10-30 12:20:40",
    summary: "国立柱原是明清古建筑上的柱子，原计划用作校门，后来没有做成，之后被埋在地下，50年沉睡在地下，2007学校大建挖出，觉得很好看，就做了个顶，两根柱子上本别刻了继往、开来四个字，现在已经是学校的一个地标了",
    auther_name: "韦朝旭",
    onwer_name: "韦朝旭",
    goods_name: "钱包",
    selected:false,
  },
  {
    avatar: "/images/images/avatar/2.png",
    main_image: "https://img3.doubanio.com/view/photo/s_ratio_poster/public/p2549177902.jpg",
    content: "爱校路在图书馆后面，11月的枫叶很好看",
    id: 1,
    updated_time: "2019-10-30 12:20:40",
    summary: "一头连着图书馆，一头连着大礼堂，路的左侧是同心河，右侧是杜鹃花，每年3、4月份开放，爱校路是每个同济人都走过的四季",
    auther_name: "萧",
    onwer_name: "索隆",
    goods_name: "校园卡",
    selected: false,
  },
  {
    avatar: "/images/images/avatar/3.png",
    main_image: "https://img3.doubanio.com/view/photo/s_ratio_poster/public/p2545472803.jpg",
    content: "草坪的草还是很扎人的。。。。",
    id: 2,
    updated_time: "2019-10-30 12:20:40",
    summary: "嘉定的草坪是真的特别的多了10到12月，嘉定的草坪陆续变黄",
    auther_name: "韦朝旭",
    onwer_name: "乌索普",
    goods_name: "锤子",
    selected: false,
  },
  {
    avatar: "/images/images/avatar/4.png",
    main_image: "https://img3.doubanio.com/view/photo/s_ratio_poster/public/p2542973862.jpg",
    content: "真的是很好看的",
    id: 3,
    updated_time: "2019-10-30 12:20:40",
    summary: "只有在嘉定，才会有这么与世无争的一些石凳，就那么静静的在那里",
    auther_name: "韦朝旭",
    onwer_name: "乔巴",
    goods_name: "药箱",
    selected: false,
  },
  {
    avatar: "/images/images/avatar/5.png",
    main_image: "https://img1.doubanio.com/view/photo/s_ratio_poster/public/p2541901817.jpg",
    content: "随风飘动的芦苇",
    id: 4,
    updated_time: "2019-10-30 12:20:40",
    summary: "嘉定的湖边，芦苇丛生，看着随风摇曳的芦苇，一切宠辱似乎都不存在了，只感受到惬意。",
    auther_name: "萧",
    onwer_name: "路飞",
    goods_name: "帽子",
    selected: false,
  },
  {
    avatar: "/images/images/avatar/3.png",
    main_image: "https://img3.doubanio.com/view/photo/s_ratio_poster/public/p2541035591.jpg",
    content: "最老的宿舍楼,历史的见证",
    id: 5,
    updated_time: "2019-10-30 12:20:40",
    summary: "同济最老的宿舍楼，瓦楞上的落叶，墙上斑驳的印记，都是时光的见证，而楼里，走过了十几代同济人",
    auther_name: "朝旭",
    onwer_name: "香吉士",
    goods_name: "菜刀",
    selected: false,
  },
]

var userInfo={
  name: "韦朝旭",
  tel: "183****7403",
  address: "同济大学西北三",
  qrcode: "待生成",
  balance: "￥5.5",
}
var info = [{
    title: "姓名",
    img: "/images/icons/卡.png",
    id: 0
  },
  {
    title: "电话",
    img: "/images/icons/钥匙.png",
    id: 1
  },
  {
    title: "地址",
    img: "/images/icons/贴纸.png",
    id: 2
  },
  {
    title: "二维码",
    img: "/images/icons/贴纸.png",
    id: 3
  },
  {
    title: "账户",
    img: "/images/icons/卡.png",
    id: 4
  },
  {
    title: "设置",
    img: "/images/icons/钥匙.png",
    id: 5
  },
]

module.exports = {
  goodsList: localDataBase,
  userinfo: userInfo
}