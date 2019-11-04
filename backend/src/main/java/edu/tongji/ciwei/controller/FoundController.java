package edu.tongji.ciwei.controller;

import edu.tongji.ciwei.pojo.dto.request.FoundRelease;
import edu.tongji.ciwei.pojo.dto.response.GoodsDetail;
import edu.tongji.ciwei.pojo.dto.response.ReleaseDate;
import edu.tongji.ciwei.util.GoodsListFunction;
import io.swagger.annotations.ApiOperation;
import org.springframework.web.bind.annotation.*;

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
    @ApiOperation(value = "获取寻物发布项的详情信息")
    public GoodsDetail getGoodsDetail() {
        GoodsDetail goods = new GoodsDetail();
        goods.setReleaserName("韦朝旭");
        goods.setReleaseDate(ReleaseDate.builder().year(2019).month(5).day(26).build());
        return goods;
    }

    @ApiOperation(value = "分页获取寻物发布页面的列表")
    @GetMapping("{pageIndex}")
    public List<GoodsDetail> getFoundGoodsList(@PathVariable Integer pageIndex, @PathParam("pageCount") Integer pageCount) throws CloneNotSupportedException {
        Integer idxStart = pageIndex * pageCount;
        List<GoodsDetail> list = new ArrayList<>();
        GoodsDetail goods = new GoodsDetail();
        goods.setReleaserName("李依璇");
        goods.setAvatarUrl("/images/images/avatar/1.png");
        goods.setGoodsImageUrl("https://img3.doubanio.com/view/photo/s_ratio_poster/public/p2546335362.jpg");
        goods.setGoodsBriefIntroduction("拾物简介14个字..");
        goods.setGoodsDescription("拾物描述詳情");
        goods.setLocationDescription("杨浦区四平路1239号");
        goods.setGoodsOwner("李依璇");
        goods.setGoodsType("钱包");
        goods.setReleaseDate(ReleaseDate.builder().year(2019).month(5).day(26).build());
        list.add(goods);
        list.add(goods.clone());
        GoodsListFunction.forEach(list.iterator(), (index, item) -> item.setGoodsListIndex(index + idxStart));
        return list;
    }

    @PostMapping("release")
    public boolean releaseFound(@RequestBody FoundRelease foundRelease) {
        System.out.println(foundRelease);
        return false;
    }

    @PostMapping("notification")
    public boolean notifyRegisteredGoodsOwner(){
        return false;
    }
}
