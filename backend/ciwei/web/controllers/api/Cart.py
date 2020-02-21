from flask import jsonify

from web.controllers.api import route_api


@route_api.route('/cart/index', methods=['GET', 'POST'])
def cartIndex():
    return jsonify({})
