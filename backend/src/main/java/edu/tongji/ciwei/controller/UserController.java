package edu.tongji.ciwei.controller;

import edu.tongji.ciwei.pojo.dto.response.UserInfo;
import org.springframework.web.bind.annotation.*;

import java.math.BigDecimal;

/**
 * @author 100101001
 * @date 11/3/2019 3:07 PM
 */
@RestController
@CrossOrigin(origins = "*")
@RequestMapping("user")
public class UserController {

    @GetMapping("{id}")
    public UserInfo getUserInfo(@PathVariable Integer id) {
        return UserInfo.builder().
                username("李依璇").
                address("同濟大學嘉定校區").
                telephone("17717090831").
                qrCode("待生成").
                accountBalance(new BigDecimal(5.1)).build();
    }
}
