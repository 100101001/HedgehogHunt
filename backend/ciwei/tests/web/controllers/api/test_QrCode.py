import requests

# TODO:开辟测试环境OR数据库回滚
from application import db

from tests.util.TestHelper import ApiBaseTest


class TestQrCode(ApiBaseTest):

    def setUp(self) -> None:
        super().setUp()
        from common.models.ciwei.Member import Member
        self.member1 = Member()
        self.member1.openid = 'opLxO5Q3CloBEmwcarKrF_kSA574'
        self.member1.nickname = 'lyx'
        self.member2 = Member()
        self.member2.openid = 'opLxO5fubMUl7GdPFgZOUaDHUik8'
        self.member2.nickname = 'ellen li'
        db.session.add(self.member1)
        db.session.add(self.member2)
        db.session.commit()

    def test_get_wx_qr_code(self):
        """
        从wx获取二维码
        :return:
        """
        image_url_resp = self.client.get('/api/qrcode/wx',
                                         headers=self.get_api_headers(openid=self.member1.openid,
                                                                      member_id=str(self.member1.id))).json
        with self.client.get(image_url_resp['data']['qr_code_url']['qr_code_url']) as image_resp:
            self.assertTrue(image_resp.status_code == 200, "返回微信二维码图片失败")
            self.assertTrue(image_resp.headers.get('Content-Type') == 'image/jpeg', "返回的不是二维码图片")

    def test_get_db_qr_code(self):
        """
        从db获取二维码
        :return:
        """
        no_db_qr_code_resp_body = self.client.get('/api/qrcode/db',
                                                  headers=self.get_api_headers(openid=self.member2.openid,
                                                                               member_id=str(self.member2.id))).json
        self.assertDictEqual(no_db_qr_code_resp_body, {'code': 201, 'msg': '会员无二维码', 'data': {}}, "没有二维码时返回的提示信息错误")

        self.client.get('/api/qrcode/wx',
                        headers=self.get_api_headers(openid=self.member2.openid,
                                                     member_id=str(self.member2.id)))
        image_url_resp = self.client.get('/api/qrcode/db',
                                         headers=self.get_api_headers(openid=self.member2.openid,
                                                                      member_id=str(self.member2.id))).json
        with self.client.get(image_url_resp['data']['qr_code_url']) as image_resp:
            self.assertTrue(image_resp.status_code == 200, "返回微信二维码图片失败")
            self.assertTrue(image_resp.headers.get('Content-Type') == 'image/jpeg', "返回的不是二维码图片")
