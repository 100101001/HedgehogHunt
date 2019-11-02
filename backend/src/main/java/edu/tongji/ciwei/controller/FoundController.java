package edu.tongji.ciwei.controller;

import edu.tongji.ciwei.pojo.dto.response.GoodsDetail;
import edu.tongji.ciwei.pojo.dto.response.ReleaseDate;
import io.swagger.annotations.ApiImplicitParams;
import io.swagger.annotations.ApiOperation;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.bind.annotation.PathVariable;

import javax.websocket.server.PathParam;
import java.util.ArrayList;
import java.util.List;

/**
 * @author 100101001
 * @date 11/2/2019 3:46 PM
 */
@RestController
@CrossOrigin(origins = "*")
@RequestMapping("found")
public class FoundController {

    @GetMapping("test")
    @ApiOperation(value="获取寻物发布项的详情信息")
    public GoodsDetail getGoodsDetail(){
        GoodsDetail goods = new GoodsDetail();
        goods.setReleaserName("韦朝旭");
        goods.setReleaseDate(ReleaseDate.builder().year(2019).month(5).day(26).build());
        return goods;
    }

    @ApiOperation(value = "分页获取寻物发布页面的列表" )
    @GetMapping("{pageIndex}")
    public List<GoodsDetail> getFoundGoodsList(@PathVariable String pageIndex, @PathParam("pageCount")Integer pageCount){
        System.out.println(pageIndex);
        System.out.println(pageCount);
        List<GoodsDetail> list = new ArrayList<>();
        GoodsDetail goods = new GoodsDetail();
        goods.setReleaserName("李依璇");
        goods.setAvatarUrl("/images/images/avatar/1.png");
        goods.setGoodsImageUrl("https://img3.doubanio.com/view/photo/s_ratio_poster/public/p2546335362.jpg");
        goods.setGoodsDescription("我就测试一下好不好用");
        goods.setGoodsOwner("李依璇");
        goods.setGoodsType("钱包");
        goods.setReleaseDate(ReleaseDate.builder().year(2019).month(5).day(26).build());
        list.add(goods);
        list.add(goods);
        return list;
    }
}
