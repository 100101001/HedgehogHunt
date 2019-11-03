package edu.tongji.ciwei.pojo.dto.response;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Builder;
import lombok.Data;

import java.math.BigDecimal;

/**
 * @author 100101001
 * @date 11/3/2019 3:05 PM
 */
@Data
@Builder
@JsonInclude(JsonInclude.Include.NON_EMPTY)
public class UserInfo {

    @JsonProperty(value = "name")
    private String username;

    @JsonProperty(value = "tel" )
    private String telephone;

    @JsonProperty(value = "address" )
    private String address;

    @JsonProperty(value = "qrcode" )
    private String qrCode;

    @JsonProperty(value = "balance")
    private BigDecimal accountBalance;

}
