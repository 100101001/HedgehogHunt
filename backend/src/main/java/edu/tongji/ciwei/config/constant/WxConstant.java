package edu.tongji.ciwei.config.constant;

import lombok.Data;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Configuration;

import java.util.Map;

/**
 * @author 100101001
 * @date 11/10/2019 12:41 PM
 */
@Data
@Configuration
@ConfigurationProperties(prefix = "wx")
public class WxConstant {
    private String secret;
    private String appId;
    private Map<String, Object> token;
    private Map<String, Object> qrcode;
    public static String URL_ATTRIBBUTE = "url";
    public static String PARAM_ATTRIBBUTE = "params";
}
