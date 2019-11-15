package edu.tongji.ciwei.config.constant;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;


/**
 * @author 100101001
 * @date 11/10/2019 12:44 PM
 */
@SpringBootTest
class WxConstantTest {

    @Autowired
    private WxConstant constant;

    @Test
    void testWxConstantSuccessfullyLoaded(){
        System.out.println(constant);
    }

    @Test
    void testWxConstantUrlReplacement(){
        System.out.println(constant.getQrcode().get(WxConstant.PARAM_ATTRIBBUTE));
    }
}