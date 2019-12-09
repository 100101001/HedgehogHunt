import random


def thankQrcode(codeId, orderId):
    """
       fill in  order_id to a qrcode record with specific id
       :return:
       """
    # add orderId to qrCodeId
    pass


def generateSmsVerCode():
    """
    generate six-bit verification code
    :return:  verification code
    """

    code = []
    for i in range(6):
        code.append(str(random.randint(0, 9)))
    return ''.join(code)
