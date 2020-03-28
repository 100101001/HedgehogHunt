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
    phone: /^1(3|4|5|7|8)\d{9}$/
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

module.exports = {
  formatTime: formatTime,
  onNavigateTap: onNavigateTap,
  regexConfig: regexConfig,
  toFixed: toFixed,
  toFixedStr: toFixedStr
}