package edu.tongji.ciwei;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import springfox.documentation.swagger2.annotations.EnableSwagger2;

@SpringBootApplication
@EnableSwagger2
public class CiweiApplication {

    public static void main(String[] args) {
        SpringApplication.run(CiweiApplication.class, args);
    }

}
