// pages/Release/Release.js
var util = require("../../../utils/util.js");
Page({
  data: {
    imageList: [],
    countIndex: 0,
    isEmpty: true,
    list: '',

    imgs: [],
    upload_picture_list: [],
    count: 1,
    url: '',
    notli: false,
    pic_status: true

  },
  onLoad: function(options) {
    var textArray = {
      text1: "温馨提示：信息填写得越完整，物归原主的几率越大",
      text2: "辛苦了"
    };
    var inputTextArray = [{
        labelText: "失主姓名",
        placeholderText: "未知",
      },
      {
        labelText: "联系方式",
        placeholderText: "电话号码，可以不填",
      },
      {
        labelText: "放置位置",
        placeholderText: "物品预计放置位置",
      },
      {
        labelText: "物品种类",
        placeholderText: "输入物品",
        value: ""
      },
    ];
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
        type: "书",
        id: 3
      },
      {
        type: "雨伞",
        id: 4
      },
    ];

    this.setData({
      inputTextArray: inputTextArray,
      typeArray: typeArray
    });
  },
  onReady: function(event) {
    wx.setNavigationBarTitle({
      title: '寻物启事信息发布',
    })
  },

  formSubmit: function(event) {
    console.log("提交数据为：", event.detail.value);
    //数据提交成功后显示提示页面
    wx.navigateTo({
      url: '../remind/remind',
    })
  },

  formReset: function(event) {
    console.log("执行Reset事件")
  },

  //点击物品种类
  onTypeChooseTap: function(event) {
    wx.showModal({
      title: '选择物品',
      content: '',
    })
    var id = event.currentTarget.dataset.id;
    var type = this.data.typeArray[id].type;
    this.setData({
      value: type
    })
  },

  //预览图片
  previewImage: function(e) {
    var current = e.target.dataset.src;
    wx.previewImage({

      current: current,
      urls: this.data.imageList
    })
  },

  //选择图片方法
  uploadpic: function(e) {
    var that = this //获取上下文
    var upload_picture_list = that.data.upload_picture_list
    //选择图片
    wx.chooseImage({
      count: 9 - that.data.upload_picture_list.length,
      sizeType: ['compressed'],
      sourceType: ['album', 'camera'],
      success: function(res) {
        wx.showToast({
          //没有真正的上传数据
          title: '正在上传...',
          icon: 'loading',
          mask: true,
          duration: 2000,
          success: function(res) {
            console.log('成功加载动画');
          }
        })
        var tempFiles = res.tempFiles
        //把选择的图片 添加到集合里
        for (var i in tempFiles) {
          tempFiles[i]['upload_percent'] = 0
          tempFiles[i]['path_server'] = ''
          upload_picture_list.push(tempFiles[i])
        }
        //显示
        that.setData({
          upload_picture_list: upload_picture_list,
        });
        if (upload_picture_list.length >= 9) {
          that.setData({
            pic_status: false,
          });
        } else {
          console.log("已经超过了九张")
          that.setData({
            pic_status: true,
          });
        }
      }
    })
  },
  //点击上传事件
  uploadimage: function() {
    var page = this
    var upload_picture_list = page.data.upload_picture_list
    //循环把图片上传到服务器 并显示进度       
    for (var j in upload_picture_list) {
      if (upload_picture_list[j]['upload_percent'] == 0) {　　　　　　 //调用函数
        app.util.upload_file_server(app.api.up_pic, page, upload_picture_list, j)
      }
    }
  },
  // 删除图片
  deleteImg: function(e) {
    let upload_picture_list = this.data.upload_picture_list;
    let index = e.currentTarget.dataset.index;
    upload_picture_list.splice(index, 1);
    this.setData({
      upload_picture_list: upload_picture_list
    });
    if (upload_picture_list.length >= 9) {
      this.setData({
        pic_status: false,
      });
    } else {
      console.log("已经超过了九张")
      this.setData({
        pic_status: true,
      });
    }
  },


  /*上传方法
  function upload_file_server(url, that, upload_picture_list, j) {
    //上传返回值
    const upload_task = wx.uploadFile({
      // 模拟https
      url: url, //需要用HTTPS，同时在微信公众平台后台添加服务器地址  
      filePath: upload_picture_list[j]['path'], //上传的文件本地地址    
      name: 'file',
      formData: {
        'num': j
      },
      //附近数据，这里为路径     
      success: function (res) {

        var data = JSON.parse(res.data);
        // //字符串转化为JSON  
        if (data.Success == true) {

          var filename = data.file //存储地址 显示

          upload_picture_list[j]['path_server'] = filename
        } else {
          upload_picture_list[j]['path_server'] = filename
        }
        that.setData({
          upload_picture_list: upload_picture_list
        });

        wx.setStorageSync('imgs', upload_picture_list);
      }
    })
    //上传 进度方法
    upload_task.onProgressUpdate((res) => {
      upload_picture_list[j]['upload_percent'] = res.progress
      that.setData({
        upload_picture_list: upload_picture_list
      });
    });
  }
  */
})