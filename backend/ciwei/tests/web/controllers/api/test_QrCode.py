import json
from unittest import TestCase
import requests

from tests.util import TestHelper


# TODO:开辟测试环境OR数据库回滚
class TestQrCode(TestCase):
    def setUp(self):
        db

    def test_get_wx_qr_code(self):
        headers = {
            'Authorization': 'opLxO5Q3CloBEmwcarKrF_kSA574#100000',
            'Content-type': 'application/json'
        }
        image_url_resp = requests.get(TestHelper.build_api_url('/qrcode/wx'), headers=headers).json()
        url = image_url_resp['data']['qr_code_url']['qr_code_url']
        image_resp = requests.get(url)
        self.assertTrue(image_resp.status_code == 200, "返回微信二维码图片失败")
        self.assertTrue(image_resp.headers.get('Content-Type') == 'image/jpeg', "返回的不是二维码图片")

    def test_get_db_qr_code(self):
        headers = {
            'Authorization': 'opLxO5Q3CloBEmwcarKrF_kSA574#100000',
            'Content-type': 'application/json'
        }
        no_db_qr_code_resp_body = requests.get(TestHelper.build_api_url('qrcode/db'), headers=headers).json()
        self.assertDictEqual(no_db_qr_code_resp_body, {'code': -1, 'msg': '会员无二维码', 'data': {}}, "没有二维码时返回的提示信息错误")
        headers['Authorization'] = ''
        image_url_resp = requests.get(TestHelper.build_api_url('qrcode/db'), headers=headers).json()
        url = image_url_resp['data']['qr_code_url']['qr_code_url']
        image_resp = requests.get(url)
        self.assertTrue(image_resp.status_code == 200, "返回微信二维码图片失败")
        self.assertTrue(image_resp.headers.get('Content-Type') == 'image/jpeg', "返回的不是二维码图片")

