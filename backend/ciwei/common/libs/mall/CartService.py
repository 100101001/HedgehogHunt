
from application import db
from common.libs.Helper import getCurrentDate
from common.models.ciwei.mall.Cart import Cart


class CartService:

    @staticmethod
    def deleteItem(member_id=0, items=None):
        """
        :param member_id:
        :param items:
        :return: 会员是否存在
        """
        if member_id < 1 or not items:
            return False
        for item in items:
            Cart.query.filter_by(product_id=item['id'], member_id=member_id).delete()
        db.session.commit()
        return True

    @staticmethod
    def setItems(member_id=0, product_id=0, number=0):
        """
        :param member_id:
        :param product_id:
        :param number:
        :return:向购物车添加/更新数量成功与否
        """
        # 校验参数
        if member_id < 1 or product_id < 1 or number < 1:
            return False
        # 更新数量/添加
        cart_info = Cart.query.filter_by(product_id=product_id, member_id=member_id).first()
        if cart_info:
            model_cart = cart_info
        else:
            model_cart = Cart()
            model_cart.member_id = member_id
            model_cart.created_time = getCurrentDate()

        model_cart.product_id = product_id
        model_cart.product_num = number
        model_cart.updated_time = getCurrentDate()
        db.session.add(model_cart)
        db.session.commit()
        return True
