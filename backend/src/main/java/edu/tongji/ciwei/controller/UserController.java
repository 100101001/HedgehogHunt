package edu.tongji.ciwei.controller;

import cn.hutool.core.codec.Base64Encoder;
import edu.tongji.ciwei.pojo.dto.response.UserInfo;
import edu.tongji.ciwei.service.rest3rd.WxService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.*;

import java.math.BigDecimal;
import java.util.Base64;

/**
 * @author 100101001
 * @date 11/3/2019 3:07 PM
 */
@RestController
@CrossOrigin(origins = "*")
@RequestMapping("user")
public class UserController {

    @Autowired
    private WxService wxService;

    @GetMapping("{id}")
    public UserInfo getUserInfo(@PathVariable("id") Integer userId) {
        return UserInfo.builder().
                username("李依璇").
                address("同濟大學嘉定校區").
                telephone("17717090831").
                qrCode("待生成").
                accountBalance(new BigDecimal(5.1)).build();
    }

    @GetMapping(value = "qrcode/{id}")
    public String getQrcode(@PathVariable("id") Integer userId){
        System.out.println(userId);
        return Base64Encoder.encode(wxService.getQrcode("27_GpIDTuHrccTv9frh-m1fKJZXQRyLyuqkx18Jm9TRUPJrLOGXPaNL11uIS1HGyXHAvaOzlunu78Fu61FxIQ1Xg2gYyfTxj0_XTPXyN4Dv7yoAH5eDHP8j750jqx8TZBfAIAEKM"));
    }
}
