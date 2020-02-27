from unittest import TestCase

from mock import mock

from application import app, db


class BaseTest(TestCase):

    def setUp(self) -> None:
        self.app = app
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:wcx9517530@127.0.0.1/ciwei_db_test?charset=utf8mb4'
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client(use_cookies=True)

    def tearDown(self) -> None:
        db.session.remove()
        db.drop_all()
        self.app_context.pop()


class ApiBaseTest(BaseTest):

    def get_api_headers(self, openid='', member_id='', content_type='application/json') -> dict:
        return {
            'Authorization': openid + '#' + member_id,
            'Content-type': content_type
        }
