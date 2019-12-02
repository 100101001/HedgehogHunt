
#使用hash以及base64来对密码进行加密
import hashlib,base64
import random,string

class UserService():

    @staticmethod
    def geneAuthCode(user_info=None):
        m=hashlib.md5()
        str="%s-%s-%s-%s"%(user_info.uid,user_info.login_name,user_info.login_pwd,user_info.login_salt)
        m.update(str.encode('utf-8'))
        return m.hexdigest

    #使用输入的密码pwd以及秘钥salt来进行加密
    @staticmethod
    def genePwd(pwd,salt):
        m=hashlib.md5()
        str="%s-%s"%(base64.encodebytes(pwd.encode('utf-8')),salt)

        m.update(str.encode('utf-8'))
        return m.hexdigest()

    #生成秘钥
    @staticmethod
    def geneSalt(length=16):
        keylist=[random.choice((string.ascii_letters+string.digits)) for i in range(length)]
        return ("".join(keylist))
