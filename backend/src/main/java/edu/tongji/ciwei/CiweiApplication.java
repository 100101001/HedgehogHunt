package edu.tongji.ciwei;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import springfox.documentation.swagger2.annotations.EnableSwagger2;

/**
 * @author 100101001
 * @date 11/3/2019 1:36 PM
 */
@SpringBootApplication
@EnableSwagger2
public class CiweiApplication {

    public static void main(String[] args) {
        SpringApplication.run(CiweiApplication.class, args);
    }

}
