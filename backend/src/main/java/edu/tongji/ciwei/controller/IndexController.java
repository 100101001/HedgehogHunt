package edu.tongji.ciwei.controller;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * @author 100101001
 * @date 10/28/2019 11:07 AM
 */
@RestController
public class IndexController {

    @GetMapping(value = "hello")
    public String hello(){
        return "hello";
    }
}
