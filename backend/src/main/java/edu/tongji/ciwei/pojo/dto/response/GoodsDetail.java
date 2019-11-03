package edu.tongji.ciwei.pojo.dto.response;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Data;

/**
 * @author 100101001
 * @date 11/2/2019 3:45 PM
 */
@Data
@JsonInclude(JsonInclude.Include.NON_EMPTY)
public class GoodsDetail implements Cloneable{

    @JsonProperty(value = "id")
    private Integer goodsListIndex;

    @JsonProperty(value = "avatarSrc")
    private String avatarUrl;

    @JsonProperty(value = "authorName" )
    private String releaserName;

    @JsonProperty(value = "releaseDate" )
    private ReleaseDate releaseDate;

    @JsonProperty(value = "imageSrc")
    private String goodsImageUrl;

    @JsonProperty(value = "goodsType")
    private String goodsType;

    @JsonProperty(value = "goodsOwner")
    private String goodsOwner;

    @JsonProperty(value = "location" )
    private String locationDescription;

    @JsonProperty(value = "content" )
    private String goodsBriefIntroduction;

    @JsonProperty(value = "goodsDetail" )
    private String goodsDescription;

    @Override
    public GoodsDetail clone() throws CloneNotSupportedException {
        return (GoodsDetail) super.clone();
    }
}
