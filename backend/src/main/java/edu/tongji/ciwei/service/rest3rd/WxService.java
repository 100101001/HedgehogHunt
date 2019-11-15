package edu.tongji.ciwei.service.rest3rd;

import cn.hutool.core.util.StrUtil;
import cn.hutool.http.HttpUtil;
import cn.hutool.json.JSONObject;
import cn.hutool.json.JSONUtil;
import edu.tongji.ciwei.config.constant.WxConstant;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.Map;

/**
 * @author 100101001
 * @date 11/10/2019 10:24 AM
 */
@Service
public class WxService {

    @Autowired
    private WxConstant wxConstant;

    public String getAccessToken() {
        JSONObject result = JSONUtil.parseObj(HttpUtil.get((String) wxConstant.getToken().get(WxConstant.URL_ATTRIBBUTE), (Map<String, Object>) wxConstant.getToken().get(WxConstant.PARAM_ATTRIBBUTE)));
        return (String) result.get("access_token");
    }


    public byte[] getQrcode(String accessToken) {
        return HttpUtil.createPost( StrUtil.format(
                (CharSequence) wxConstant.getQrcode().get(WxConstant.URL_ATTRIBBUTE),
                accessToken)).header("Content-Type", "application/json")
                .body(JSONUtil.parseFromMap((Map<?, ?>) wxConstant.getQrcode().get(WxConstant.PARAM_ATTRIBBUTE)).toString())
                .execute()
                .bodyBytes();
    }
}
