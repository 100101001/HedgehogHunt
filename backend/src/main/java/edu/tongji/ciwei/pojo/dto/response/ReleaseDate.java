package edu.tongji.ciwei.pojo.dto.response;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Builder;
import lombok.Data;

/**
 * @author 100101001
 * @date 11/2/2019 5:29 PM
 */
@Data
@Builder
public class ReleaseDate {

    @JsonProperty(value = "year")
    private Integer year;

    @JsonProperty(value = "month")
    private Integer month;

    @JsonProperty(value = "day" )
    private Integer day;
}
