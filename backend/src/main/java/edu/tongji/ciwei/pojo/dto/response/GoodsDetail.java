package edu.tongji.ciwei.pojo.dto.response;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Data;

/**
 * @author 100101001
 * @date 11/2/2019 3:45 PM
 */
@Data
public class GoodsDetail {
    @JsonProperty(value = "avatarSrc")
    private String avatarUrl;

    @JsonProperty(value = "releaseDate" )
    private ReleaseDate releaseDate;

    @JsonProperty(value = "imageSrc")
    private String goodsImageUrl;

    @JsonProperty(value = "goodsDetail" )
    private String goodsDescription;

    @JsonProperty(value = "authorName" )
    private String releaserName;

    @JsonProperty(value = "goodsOwner")
    private String goodsOwner;

    @JsonProperty(value = "goodsType")
    private String goodsType;
}
