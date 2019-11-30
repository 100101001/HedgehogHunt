//app.js
App({
    onLaunch: function () {
    },
    globalData: {
        userInfo: null,
        version: "1.0",
        shopName: "Python3 + Flask 订餐全栈系统",
        domain:"http://0.0.0.0:8999/api"
    },
    tip:function( params ){
        var that = this;
        var title = params.hasOwnProperty('title')?params['title']:'提示信息';
        var content = params.hasOwnProperty('content')?params['content']:'';
        wx.showModal({
            title: title,
            content: content,
            success: function(res) {

                if ( res.confirm ) {//点击确定
                    if( params.hasOwnProperty('cb_confirm') && typeof( params.cb_confirm ) == "function" ){
                        params.cb_confirm();
                    }
                }else{//点击否
                    if( params.hasOwnProperty('cb_cancel') && typeof( params.cb_cancel ) == "function" ){
                        params.cb_cancel();
                    }
                }
            }
        })
    },
    alert:function( params ){
        var title = params.hasOwnProperty('title')?params['title']:'提示信息';
        var content = params.hasOwnProperty('content')?params['content']:'';
        wx.showModal({
            title: title,
            content: content,
            showCancel:false,
            success: function(res) {
                if (res.confirm) {//用户点击确定
                    if( params.hasOwnProperty('cb_confirm') && typeof( params.cb_confirm ) == "function" ){
                        params.cb_confirm();
                    }
                }else{
                    if( params.hasOwnProperty('cb_cancel') && typeof( params.cb_cancel ) == "function" ){
                        params.cb_cancel();
                    }
                }
            }
        })
    },
    console:function( msg ){
        console.log( msg);
    },
    getRequestHeader:function(){
        return {
            'content-type': 'application/x-www-form-urlencoded;charset=utf-8',
            'Authorization':this.getCache("token")
        }
    },
    buildUrl:function (path,params) {
        var url=this.globalData.domain+path;
        var _paramUrl="";
        if(params){

            //循环params里面的变量，取key为变量k，然后将k与其对应的值用等号链接起来
            //如果params={a:'b',c:'d'}
            //拼接结果的格式如a=b&c=d,GET方法都是使用‘=’来区分的
            _paramUrl=Object.keys(params).map(function (k) {
                return [encodeURIComponent(k),encodeURIComponent(params[k])].join("=");
            }).join("&");

            _paramUrl="?"+_paramUrl
        }

        return url+_paramUrl;
    },
    getCache:function (key) {
        var value=undefined;
        try{
            value=wx.getStorageSync(key);
        }
        catch (e) {

        }
        return value;
    },
    setCache:function (key,value) {
        wx.setStorage({
            key:key,
            data:value
        });
    }
});