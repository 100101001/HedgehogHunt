from application import app


def get_wx_token():
    from flask import session
    import requests
    import time

    if not hasattr(session, 'token'):
        setattr(session, 'token', {})
    token = session.token

    if not token or token['expires'] > time.time() - 5 * 60 * 1000:
        # get new token
        url = "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={}&secret={}".format(
            app.config['OPENCS_APP']['appid'], app.config['OPENCS_APP']['appkey'])

        wxResp = requests.get(url)
        if 'access_token' not in wxResp.json().keys():
            data = wxResp.json()
            app.logger.error("failed to get token! Errcode: %s, Errmsg:%s", data['errcode'], data['errmsg'])
            session.token = None
            return None
        else:
            data = wxResp.json()
            token['token'] = data['access_token']
            token['expires'] = data['expires_in'] + time.time()
            session.token = token
            return session.token['token']


