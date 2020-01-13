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
    "/pages/homepage/homepage",
    "/pages/Find/Find",
    "/pages/Release/Release",
    "/pages/Lost/Lost",
    "/pages/Mine/Mine",
  ]
  return [isSelecteds, urls];
}
module.exports = {
  formatTime: formatTime,
  showMessage: showMessage,
  onNavigateTap: onNavigateTap,
}