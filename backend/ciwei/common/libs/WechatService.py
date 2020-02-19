from application import app, cache


def get_wx_token():
    from flask import session
    import requests
    import time

    token = cache.get("token")

    if not token or token['expires_at'] > time.time():
        # get new token
        url = "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={}&secret={}".format(
            app.config['OPENCS_APP']['appid'], app.config['OPENCS_APP']['appkey'])

        wxResp = requests.get(url)
        if 'access_token' not in wxResp.json().keys():
            data = wxResp.json()
            app.logger.error("failed to get token! Errcode: %s, Errmsg:%s", data['errcode'], data['errmsg'])
            return None
        else:
            data = wxResp.json()
            token = {'token': data['access_token'], 'expires_at': data['expires_in'] + time.time()}
            cache.set("token", token)
            return token['token']
    else:
        return token

