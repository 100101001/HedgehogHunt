package edu.tongji.ciwei.controller;

import edu.tongji.ciwei.pojo.dto.response.GoodsDetail;
import edu.tongji.ciwei.pojo.dto.response.ReleaseDate;
import io.swagger.annotations.ApiOperation;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * @author 100101001
 * @date 11/2/2019 3:46 PM
 */
@RestController
@CrossOrigin(origins = "*")
@RequestMapping("find")
public class FoundController {

    @GetMapping("test")
    @ApiOperation(value="获取寻物发布项")
    public GoodsDetail getGoodsDetail(){
        GoodsDetail goods = new GoodsDetail();
        goods.setReleaserName("韦朝旭");
        goods.setReleaseDate(ReleaseDate.builder().year(2019).month(5).day(26).build());
        return goods;
    }
}
