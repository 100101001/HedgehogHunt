# -*- coding: utf-8 -*-
from application import db
from common.models.ciwei.mall.ProductStockChangeLog import ProductStockChangeLog
from common.models.ciwei.mall.Product import Product
from common.libs.Helper import getCurrentDate


class ProductService:

    @staticmethod
    def setStockChangeLog(product_id=0, quantity=0, note=''):

        if product_id < 1:
            return False

        product_info = Product.query.filter_by(id=product_id).first()
        if not product_info:
            return False

        model_stock_change = ProductStockChangeLog()
        model_stock_change.product_id = product_id
        model_stock_change.unit = quantity
        model_stock_change.total_stock = product_info.stock_cnt
        model_stock_change.note = note
        model_stock_change.created_time = getCurrentDate()
        db.session.add(model_stock_change)
        db.session.commit()
        return True
