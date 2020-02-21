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
    "/pages/Release/Release",
    "/pages/Find/Find?business_type=0",
    "/pages/Mine/Mine",
  ]
  return [isSelecteds, urls];
}


//初始化底部导航栏状态
function onNavigateTap1(id) {
  var isSelecteds = {
    isSelected0: false,
    isSelected1: false,
    isSelected2: false
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
  }
  var urls = [
    "/pages/Homepage/product/index",
    "/pages/Homepage/product/cart",
    "/pages/Homepage/product/mine",
  ]
  return [isSelecteds, urls];
}

/*参考文章：https://segmentfault.com/q/1010000008005954/a-1020000008187652*/
/*获取当前页url*/
function getCurrentPageUrl() {
  var pages = getCurrentPages()    //获取加载的页面
  var currentPage = pages[pages.length - 1]    //获取当前页面的对象
  var url = currentPage.route    //当前页面url
  return url
}

/*获取当前页带参数的url*/
function getCurrentPageUrlWithArgs() {
  var pages = getCurrentPages()    //获取加载的页面
  var currentPage = pages[pages.length - 1]    //获取当前页面的对象
  var url = currentPage.route    //当前页面url
  var options = currentPage.options    //如果要获取url中所带的参数可以查看options

  //拼接url的参数
  var urlWithArgs = url + '?'
  for (var key in options) {
      var value = options[key]
      urlWithArgs += key + '=' + value + '&'
  }
  urlWithArgs = urlWithArgs.substring(0, urlWithArgs.length - 1)

  return urlWithArgs
}

//检查电话号码
function regexConfig() {
  var reg = {
    email: /^(\w-*\.*)+@(\w-?)+(\.\w{2,})+$/,
    phone: /^1(3|4|5|7|8)\d{9}$/
  }
  return reg;
}

module.exports = {
  formatTime: formatTime,
  showMessage: showMessage,
  onNavigateTap1: onNavigateTap1,
  onNavigateTap: onNavigateTap,
  regexConfig: regexConfig,
  getCurrentPageUrl: getCurrentPageUrl,
  getCurrentPageUrlWithArgs: getCurrentPageUrlWithArgs
}