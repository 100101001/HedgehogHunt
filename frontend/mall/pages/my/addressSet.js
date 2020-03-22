//获取应用实例
var commonCityData = require('../../utils/city.js');
var app = getApp();
Page({
    data: {
        info: [],
        provinces: [],
        citys: [],
        districts: [],
        selProvince: '请选择',
        selCity: '请选择',
        selDistrict: '请选择',
        selProvinceIndex: -1,
        selCityIndex: -1,
        selDistrictIndex: -1
    },
    onLoad: function (e) {
        var that = this;
        that.setData({
            id: e.id
        });
        this.initCityData(1);
    },
    onShow: function () {
        this.getInfo();
    },
    //初始化城市数据
    initCityData: function (level, obj) {
        if (level == 1) {
            var pinkArray = [];
            for (var i = 0; i < commonCityData.cityData.length; i++) {
                pinkArray.push(commonCityData.cityData[i].name);
            }
            this.setData({
                provinces: pinkArray
            });
        } else if (level == 2) {
            var pinkArray = [];
            var dataArray = obj.cityList
            for (var i = 0; i < dataArray.length; i++) {
                pinkArray.push(dataArray[i].name);
            }
            this.setData({
                citys: pinkArray
            });
        } else if (level == 3) {
            var pinkArray = [];
            var dataArray = obj.districtList
            for (var i = 0; i < dataArray.length; i++) {
                pinkArray.push(dataArray[i].name);
            }
            this.setData({
                districts: pinkArray
            });
        }
    },
    bindPickerProvinceChange: function (event) {
        var selIterm = commonCityData.cityData[event.detail.value];
        this.setData({
            selProvince: selIterm.name,
            selProvinceIndex: event.detail.value,
            selCity: '请选择',
            selCityIndex: -1,
            selDistrict: '请选择',
            selDistrictIndex: -1
        });
        this.initCityData(2, selIterm);
    },
    bindPickerCityChange: function (event) {
        var selIterm = commonCityData.cityData[this.data.selProvinceIndex].cityList[event.detail.value];
        this.setData({
            selCity: selIterm.name,
            selCityIndex: event.detail.value,
            selDistrict: '请选择',
            selDistrictIndex: -1
        });
        this.initCityData(3, selIterm);
    },
    bindPickerChange: function (event) {
        var selIterm = commonCityData.cityData[this.data.selProvinceIndex].cityList[this.data.selCityIndex].districtList[event.detail.value];
        if (selIterm && selIterm.name && event.detail.value) {
            this.setData({
                selDistrict: selIterm.name,
                selDistrictIndex: event.detail.value
            })
        }
    },
    bindCancel: function () {
        wx.navigateBack({});
    },
    bindSave: function (e) {
        var that = this;
        var nickname = e.detail.value.nickname;
        var address = e.detail.value.address;
        var mobile = e.detail.value.mobile;

        if (nickname == "") {
            app.tip({ content: '请填写联系人姓名~~' });
            return
        }
        if (mobile == "") {
            app.tip({ content: '请填写手机号码~~' });
            return
        }
        if (this.data.selProvince == "请选择") {
            app.tip({ content: '请选择地区~~' });
            return
        }
        if (this.data.selCity == "请选择") {
            app.tip({ content: '请选择地区~~' });
            return
        }
        var selProvinceIndex = this.data.selProvinceIndex
        var selCityIndex = this.data.selCityIndex
        var selDistrictIndex = this.data.selDistrictIndex

        //-1表示没有选择过省市，但省市有具体值（不是请选择），说明编辑地址时没有动过原来的值
        if (selProvinceIndex == -1) {
            var province_id = this.data.province_id
        } else {
            var province_id = commonCityData.cityData[this.data.selProvinceIndex].id
        }
        //-1表示没有选择过城市，但城市有具体值（不是请选择），说明编辑地址时没有动过原来的值
        if (selCityIndex == -1) {
            var city_id = this.data.city_id
        } else {
            var city_id = commonCityData.cityData[selProvinceIndex].cityList[selCityIndex].id;
        }
        //-1表示没有选择过区域，但区域有具体值（不是请选择），说明编辑地址时没有动过原来的值
        if (selDistrictIndex == -1 && this.data.selDistrict != "请选择") {
            var district_id = this.data.district_id
        } else {
            if (this.data.selDistrict == "请选择" || !this.data.selDistrict) {
                var district_id = '';
            } else {
                var district_id = commonCityData.cityData[this.data.selProvinceIndex].cityList[this.data.selCityIndex].districtList[this.data.selDistrictIndex].id;
            }
        }

        if (address == "") {
            app.tip({ content: '请填写详细地址~~' });
            return
        }

        wx.request({
            url: app.buildUrl("/my/address/set"),
            header: app.getRequestHeader(),
            method: "POST",
            data: {
                id: that.data.id,
                province_id: province_id,
                province_str: that.data.selProvince,
                city_id: city_id,
                city_str: that.data.selCity,
                district_id: district_id,
                district_str: that.data.selDistrict,
                nickname: nickname,
                address: address,
                mobile: mobile,
            },
            success: function (res) {
                var resp = res.data;
                if (resp.code != 200) {
                    app.alert({ "content": resp.msg });
                    return;
                }
                // 跳转
                wx.navigateBack({});
            }
        })
    },
    deleteAddress: function (e) {
        var that = this;
        var params = {
            "content": "确定删除？",
            "cb_confirm": function () {
                wx.request({
                    url: app.buildUrl("/my/address/ops"),
                    header: app.getRequestHeader(),
                    method: 'POST',
                    data: {
                        id: that.data.id,
                        act: 'del'
                    },
                    success: function (res) {
                        var resp = res.data;
                        app.alert({ "content": resp.msg });
                        if (resp.code == 200) {
                            // 跳转
                            wx.navigateBack({});
                        }
                    }
                });
            }
        };
        app.tip(params);
    },
    getInfo: function () {
        var that = this;
        if (that.data.id < 1) {
            return;
        }
        wx.request({
            url: app.buildUrl("/my/address/info"),
            header: app.getRequestHeader(),
            data: {
                id: that.data.id
            },
            success: function (res) {
                var resp = res.data;
                if (resp.code != 200) {
                    app.alert({ "content": resp.msg });
                    return;
                }
                var info = resp.data.info;
                that.setData({
                    info: info,
                    selProvince: info.province_str ? info.province_str : "请选择",
                    selCity: info.city_str ? info.city_str : "请选择",
                    selDistrict: info.area_str ? info.area_str : "请选择",
                    province_id: info.province_id ? info.province_id : -1,
                    city_id: info.city_id ? info.city_id : -1,
                    district_id: info.area_id ? info.area_id : -1,
                });
            }
        });
    }
});
