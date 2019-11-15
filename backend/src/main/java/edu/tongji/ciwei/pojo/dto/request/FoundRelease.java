package edu.tongji.ciwei.pojo.dto.request;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Data;
import lombok.extern.slf4j.Slf4j;

/**
 * @author 100101001
 * @date 11/3/2019 7:02 PM
 */
@Data
@Slf4j
public class FoundRelease {
    @JsonProperty(value = "goods_detail")
    private String goodsDetail;

    @JsonProperty(value = "goods_owner" )
    private String goodsOwner;

    @JsonProperty(value = "goods_type" )
    private String goodsType;

    @JsonProperty(value = "phone_number")
    private String phoneNumber;

    @JsonProperty(value = "set_location" )
    private String location;
}
