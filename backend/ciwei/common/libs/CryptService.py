# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/4/10 下午9:06
@file: CryptService.py
@desc: 
"""

from Crypto.Cipher import DES3
from Crypto.Cipher import AES
import base64


class DesCrypt:

    @staticmethod
    def encrypt(data="", key="quick find aes23") -> str:
        """
        需要加密的明文字符串
        :param data:
        :param key:
        :return: 加密后的字符串
        """
        pad = 8 - len(data) % 8
        padStr = ""
        for i in range(pad):
            padStr = padStr + chr(pad)
        data = data + padStr
        des3 = DES3.new(key, DES3.MODE_ECB)
        des3_data = des3.encrypt(data.encode('utf-8'))
        base64_des3_data = base64.standard_b64encode(des3_data)
        return base64_des3_data.decode('utf-8')

    @staticmethod
    def decrypt(data="", key='quick find aes23') -> str:
        """
        需要解密的字符串
        :param data:
        :param key:
        :return: 解密后的明文字符串
        """
        pad = 8 - len(data) % 8
        padStr = ""
        for i in range(pad):
            padStr = padStr + chr(pad)
        data = data + padStr
        base64_data = base64.standard_b64decode(data)
        des = DES3.new(key, DES3.MODE_ECB)
        decrypt_data = des.decrypt(base64_data)
        return decrypt_data[0:decrypt_data[len(decrypt_data) - 1] * -1].decode('utf-8')


class AESCrypt:
    """
    对称加解密工具
    """

    def __init__(self, key='xunhui', model='ECB', iv=None, encode='utf8'):
        """
        初始AES加解密工具的秘钥，加密模式
        :param key: 加解密秘钥
        :param model: 默认采用ECB模式
        :param iv: CBC模式需要的额外向量
        :param encode: 字符串编码方式
        """
        self.encode_ = encode
        self.model = {'ECB': AES.MODE_ECB, 'CBC': AES.MODE_CBC}[model]
        self.key = self.add_16(key)
        if model == 'ECB':
            self.aes = AES.new(self.key, self.model)  # 创建一个aes对象
        elif model == 'CBC':
            self.aes = AES.new(self.key, self.model, iv)  # 创建一个aes对象

    def add_16(self, par):
        """
        字节填充
        :param par:
        :return:
        """
        # 这里的密钥长度必须是16、24或32，目前16位的就够用了
        par = par.encode(self.encode_)
        while len(par) % 16 != 0:
            par += b'\x00'
        return par

    # def padding_pkcs5(self, value):
    #     BS = AES.block_size
    #     return str.encode(value + (BS - len(value) % BS) * chr(BS - len(value) % BS))

    def encrypt(self, text=""):
        """
        加密方法
        :param text:
        :return:
        """
        text = self.add_16(text)
        encrypt_text = self.aes.encrypt(text)
        return base64.encodebytes(encrypt_text).decode().strip()

    def decrypt(self, text=""):
        """
        解密方法
        :param text:
        :return:
        """
        text = base64.decodebytes(text.encode(self.encode_))
        decrypt_text = self.aes.decrypt(text)
        return decrypt_text.decode(self.encode_).strip('\0')


# 单例暴露
Cipher = AESCrypt()

if __name__ == '__main__':
    # pr = AESCrypt('secretkey123', 'ECB', '', 'gbk')
    # en_text = pr.encrypt('李依璇')
    # print('密文:', en_text)
    # print('明文:', pr.decrypt(en_text))

    # pr = AESCrypt('xunhui', 'ECB', '', 'utf8')
    pr = DesCrypt()
    import urllib.parse as parser
    print(parser.quote(str('opLxO5Q3CloBEmwcarKrF_kSA574')))
    en_text = pr.encrypt('opLxO5Q3CloBEmwcarKrF_kSA574')
    #en_text = 'FEuNz7OnlvGGiV3s9PN14A=='
    #import urllib.parse as parser
    #print(parser.quote(en_text))
    print('密文:', en_text)
    print('密文:', len(en_text))
    print('明文:', pr.decrypt(en_text))
