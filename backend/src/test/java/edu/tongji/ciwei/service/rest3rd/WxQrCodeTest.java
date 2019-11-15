package edu.tongji.ciwei.service.rest3rd;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;

/**
 * @author 100101001
 * @date 11/10/2019 2:32 PM
 */
@SpringBootTest
class WxQrCodeTest {

    @Autowired
    private WxService wxService;


    @Test
    public void testGetAccessToken(){

        System.out.println(wxService.getAccessToken());
    }
}
