const app = getApp();
const formatTime = date => {
  const year = date.getFullYear()
  const month = date.getMonth() + 1
  const day = date.getDate()
  const hour = date.getHours()
  const minute = date.getMinutes()
  const second = date.getSeconds()

  return [year, month, day].map(formatNumber).join('/') + ' ' + [hour, minute, second].map(formatNumber).join(':')
}

const formatNumber = n => {
  n = n.toString()
  return n[1] ? n : '0' + n
}

//显示提示语的函数
function showMessage(title, content) {
  wx.showModal({
    title: title,
    content: content,
  })
}

//初始化底部导航栏状态
function onNavigateTap(id) {
  var isSelecteds = {
    isSelected0: false,
    isSelected1: false,
    isSelected2: false,
    isSelected3: false,
    isSelected4: false,
  }
  switch (id) {
    case 0:
      isSelecteds.isSelected0 = true;
      break;
    case 1:
      isSelecteds.isSelected1 = true;
      break;
    case 2:
      isSelecteds.isSelected2 = true;
      break;
    case 3:
      isSelecteds.isSelected3 = true;
      break;
    case 4:
      isSelecteds.isSelected4 = true;
      break;
  }
  var urls = [
    "/pages/Homepage/homepage",
    "/pages/Find/Find?business_type=1",
    "/pages/Release/release/index",
    "/pages/Find/Find?business_type=0",
    "/pages/Mine/Mine",
  ]
  return [isSelecteds, urls];
}


//检查电话号码
function regexConfig() {
  var reg = {
    email: /^(\w-*\.*)+@(\w-?)+(\.\w{2,})+$/,
    phone: /^1(3|4|5|6|7|8|9)\d{9}$/  //10,11,12开头电话分配给固定机构使用
  }
  return reg;
}

function toFixed(num=0, fix_num=2){
  if (typeof num === 'number'){
    return parseFloat(num.toFixed(fix_num))
  }
  if(typeof num === 'string'){
    return parseFloat(parseFloat(num).toFixed(fix_num))
  }
  return 0.00
}

function toFixedStr(num=0, fix_num=2){
  if (typeof num === 'number'){
    return num.toFixed(fix_num)
  }
  if(typeof num === 'string'){
    return parseFloat(num).toFixed(fix_num)
  }
  return "0.00"
}

/**
 * 滚到可见point代表的元素的位置，用于去置顶，进入编辑页自动下拉到置顶组件
 * @param point
 */
function goToPoint(point = "") {
  const query = wx.createSelectorQuery();
  //在当前页面中，利用ID选择器，获得指定节点的信息
  query.select(point).boundingClientRect();
  //根据设备视区信息，动态计算滚动位置
  query.selectViewport().scrollOffset();
  query.exec((res) => {
    //res[0]是节点信息,res[1]是位置
    if (res[0] && res[1]) {
      //如果节点存在，并且位置可得
      wx.pageScrollTo({
        scrollTop: res[0].top + res[1].scrollTop,
        duration: 300
      })
    }
  })
}

/**
 * getNewRecommend 获取新消息计数
 * @param cb_complete
 */
const getNewRecommend = function(cb_complete=(data={})=>{}){
  wx.request({
    url: app.buildUrl('/member/get-new-recommend'),
    header: app.getRequestHeader(),
    success: (res) => {
      let resp = res.data
      if (resp['code'] !== 200) {
        cb_complete({})
        return
      }
      let data = resp['data']
      app.globalData.total_new = data.total_new;
      app.globalData.recommend_new = data.recommend_new;
      app.globalData.thanks_new = data.thanks_new;
      app.globalData.return_new = data.return_new;
      app.globalData.return = data.return;
      app.globalData.recommend = data.recommend;
      cb_complete(data)
    },
    fail: res => {
      app.serverBusy()
      cb_complete({})
    }
  })
};

module.exports = {
  formatTime: formatTime,
  onNavigateTap: onNavigateTap,
  regexConfig: regexConfig,
  toFixed: toFixed,
  toFixedStr: toFixedStr,
  goToPoint: goToPoint,
  getNewRecommend: getNewRecommend
}