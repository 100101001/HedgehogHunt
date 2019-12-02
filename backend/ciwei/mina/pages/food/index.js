//index.js
//获取应用实例
var app = getApp();
Page({
    data: {
        indicatorDots: true,
        autoplay: true,
        interval: 3000,
        duration: 1000,
        loadingHidden: false, // loading
        swiperCurrent: 0,
        categories: [],
        activeCategoryId: 0,
        goods: [],
        scrollTop: "0",
        loadingMoreHidden: true,
        searchInput: '',
        p:1,
        processing:false
    },
    onLoad: function () {
        var that = this;

        wx.setNavigationBarTitle({
            title: app.globalData.shopName
        });
    },
    onShow:function(){
        this.getBannerAndCat();
    },
    scroll: function (e) {
        var that = this, scrollTop = that.data.scrollTop;
        that.setData({
            scrollTop: e.detail.scrollTop
        });
    },
    //事件处理函数
    swiperchange: function (e) {
        this.setData({
            swiperCurrent: e.detail.current
        })
    },
	listenerSearchInput:function( e ){
	        this.setData({
	            searchInput: e.detail.value
	        });
	 },
    toSearch:function( e ){
	        this.setData({
	            p:1,
	            goods:[],
	            loadingMoreHidden:true
	        });
	        this.getFoodList();
	},
    tapBanner: function (e) {
        if (e.currentTarget.dataset.id != 0) {
            wx.navigateTo({
                url: "/pages/food/info?id=" + e.currentTarget.dataset.id
            });
        }
    },
    toDetailsTap: function (e) {
        wx.navigateTo({
            url: "/pages/food/info?id=" + e.currentTarget.dataset.id
        });
    },
    getBannerAndCat:function () {
        var that = this;
        wx.request({
            url: app.buildUrl("/food/index"),
            header: app.getRequestHeader(),
            success: function (res) {
                var resp = res.data;
                if (resp.code != 200) {
                    app.alert({'content': resp.msg});
                    return
                }
                that.setData({
                    banners: resp.data.banner_list,
                    categories: resp.data.cat_list
                });
                that.getFoodList();
            }
        })
    },
    catClick:function(e){
        //选择一次分类时返回选中值
        this.setData({
            activeCategoryId:e.currentTarget.id,
            p:1,
            goods:[],
            loadingMoreHidden:true
        });
        this.getFoodList();
    },
    onReachBottom:function(e){
        var that=this;
        //延时500ms处理函数
        setTimeout(function () {
            that.getFoodList();
        },500)
    },
    getFoodList:function (e) {
        var that = this;

        if (!that.data.loadingMoreHidden){
            return;
        }

        if (that.data.processing){
            return;
        }
        that.setData({
           processing:true
        });
        wx.request({
            url: app.buildUrl("/food/search"),
            header: app.getRequestHeader(),
            data:{
                cat_id:that.data.activeCategoryId,
                mix_kw:that.data.searchInput,
                p:that.data.p
            },
            success: function (res) {
                var resp = res.data
                if (resp.code !== 200) {
                    app.alert({'content': resp.msg});
                    return
                }
                var goods=resp.data.list;
                that.setData({
                    goods:that.data.goods.concat(goods),
                    p:that.data.p+1,
                    processing: false
                });
                if(res.data.has_more===0){
                    that.setData({
                        loadingMoreHidden:false
                    })
                }
            }
        })
    },

});
