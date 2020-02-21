# coding: utf-8
from sqlalchemy import Column, DateTime, Integer, Numeric, String
from sqlalchemy.schema import FetchedValue
from flask_sqlalchemy import SQLAlchemy
from application import db


class ThankOrder(db.Model):
    __tablename__ = 'thank_order'

    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, nullable=False)
    openid = db.Column(db.String(32), nullable=False)
    transaction_id = db.Column(db.String(64), server_default=db.FetchedValue())
    price = db.Column(db.Numeric(10, 2), nullable=False, server_default=db.FetchedValue())
    status = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())
    paid_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    updated_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    created_time = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())

    @property
    def status_desc(self):
        status_mapping = {
            '-1': 'fresh',
            '0': 'notpay',
            '1': 'success',
            '2': 'payerror',
            '3': 'closed',
        }
        return status_mapping[str(self.status)]

    @property
    def wx_payment_result_notified(self):
        return self.transaction_id != ''
