# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/5/14 上午9:57
@file: performance_test_base.py
@desc: 
"""
import random
from concurrent.futures.thread import ThreadPoolExecutor
from threading import Lock

import requests
from concurrent.futures import wait, ALL_COMPLETED

from tests.performance import response_time, log_api_param


class ApiAsyncCallExecutor:
    def __init__(self):
        self.pool = ThreadPoolExecutor(max_workers=10, thread_name_prefix='test_')
        self.tasks = []
        self._lock = Lock()
        self.total_cost = 0
        self.call_num = 0

    def run(self, func, *args):
        # 同步的代码，不需要做线程安全处理
        future = self.pool.submit(func, *args)
        future.add_done_callback(self._calResponseTimeCallback)
        self.tasks.append(future)

    def _calResponseTimeCallback(self, future):
        # 异步的代码块，需要做线程安全处理
        with self._lock:
            self.call_num += 1
            self.total_cost += future.result()

    def avgResponseTime(self):
        # 异步的代码块，需要等待任务全部完成
        wait(self.tasks, return_when=ALL_COMPLETED)
        print(self.call_num)
        return round(self.total_cost / self.call_num, 4)


class RestfulApisCallerAsync:
    # 单模块并发，runMixed通过反射随机调用模块内的API，利用线程池进行并发测试
    def __init__(self, TEST_LOG_FILE_PATH, API_LOG_FILE_PATH):
        self.f = open('outputs/{}'.format(TEST_LOG_FILE_PATH), 'w')
        self.arg_gen = GoodsArgGen()
        self.test_executor = ApiAsyncCallExecutor()
        self.apis = RestfulApis(API_LOG_FILE_PATH)
        self._callers = self.getAllCallers()

    def __del__(self):
        self.f.close()

    def callSearchGoods(self):
        self.test_executor.run(self.apis.searchGoods, *self.arg_gen.genSearchArgs())

    def callReleaseGoods(self):
        self.test_executor.run(self.apis.releaseGoods, *self.arg_gen.genReleaseArgs())

    def callGetNewHintsGoods(self):
        self.test_executor.run(self.apis.getNewHintGoods)

    def callSearchRecordsGoods(self):
        self.test_executor.run(self.apis.searchRecordGoods, *self.arg_gen.genRecordSearchArgs())

    def callGetInfoMember(self):
        self.test_executor.run(self.apis.getInfoMember)

    def avgResponseTime(self):
        return self.test_executor.avgResponseTime()

    def getAllModuleCallers(self, module_name='Goods'):
        return list(filter(lambda m: m.startswith("call") and m.endswith(module_name)
                                     and callable(getattr(self, m)), dir(self)))

    def getAllCallers(self):
        return list(filter(lambda m: m.startswith("call")
                                     and callable(getattr(self, m)), dir(self)))

    def random_call(self):
        target_api_caller = getattr(self, random.choice(self._callers), None)
        if target_api_caller:
            target_api_caller()



class GoodsArgGen:
    # 发布与搜索物品接口的意义汉字参数生成
    def __init__(self):
        goods = '储蓄卡 银行卡 资金卡 支付卡 账户卡 金卡 龙卡 服务卡 联系卡 优惠卡 会员卡 指路卡 磁卡 纸卡 借记卡 负担卡 审批卡 监督卡 保险卡 记录卡 购票卡 记分卡 户口卡 胸卡 贺卡 贺年卡 生日卡 圣诞卡 纪念卡 爱心卡 的卡 登记卡 贺年片 信用卡 ' \
                '工作证 居留证 学生证 会员证 身份证 党证 选民证 复员证 合格证 假证 优惠证 上岗证 毕业证 牌证 下岗证 土地证 退休证 记者证 注册证 检疫证 优免证 单证 暂住证 结婚证 借书证 演出证 出生证 优待证 三证 驾驶证 准考证 使用证 登记证 团员证 独生子女证 服务证 准产证 产权证 所有权证 教师证 绿卡 出入证 ' \
                '跑鞋 钉鞋 球鞋 运动鞋 鼻烟 旱烟 水烟 烤烟 板烟 叶子烟 晒烟 雪茄烟 天线 地线 火线 高压线 裸线 专线 馈线 中继线 输电线 同轴电缆 纱包线 电力线 定向天线 通信线 广播线 电网 有线电 火具 挽具 坐具 餐具 茶具 灯具 雨具 文具 教具 道具 炊具 画具 交通工具 风动工具 网具 生产工具 窑具 厨具 猎具 牙具 浴具'
        self.goods_names = goods.split(' ')
        first = '赵钱孙李周吴郑王冯陈褚卫蒋沈韩杨朱秦尤许何吕施张孔曹严华金魏陶姜戚谢邹喻柏水窦章云苏潘葛奚范彭郎鲁韦昌马苗凤花方俞任袁柳酆鲍'
        self.owner_names = ['{}某'.format(i) for i in first]
        campus_loc = '上海市杨浦区达礼南路,同济大学-西南楼,31.283571799,121.499070899 ' \
                     '上海市杨浦区北大道与文远路交叉口东南方向50米,同济大学四平路校区北楼,31.283911349,121.504760674 ' \
                     '上海市杨浦区彰武路,同济大学四平路校区-图书馆,31.283310854,121.504270427 ' \
                     '上海市杨浦区友谊路,同济大学-文远楼,31.284911799,121.504610899 ' \
                     '上海市杨浦区南大道,同济大学四平路校区-经纬楼,31.284021349,121.500530674 ' \
                     '上海市杨浦区爱校路,同济大学四平路校区医学院,31.281692248,121.501351124 ' \
                     '上海市杨浦区行健路,同济大学-游泳馆,31.281041349,121.501570674 ' \
                     '上海市杨浦区爱校路,同济大学四平路校区-网球场,31.282830899,121.50161045 ' \
                     '上海市杨浦区赤峰路40号,上海市同济医院分院,31.280558,121.501004 ' \
                     '上海市杨浦区桓石路,同济大学-干训楼,31.281650899,121.50057045 ' \
                     '上海市杨浦区国康路46号,同济科技大厦,31.28674,121.5041 ' \
                     '上海市嘉定区栋梁路,同济大学嘉定校区-同心楼,31.283822698,121.211761349 ' \
                     '上海市嘉定区嘉园路,同济大学嘉定校区-济人楼,31.283091349,121.213720674 ' \
                     '上海市嘉定区中央大道,同济大学嘉定校区-足球场,31.288220809,121.215980405 ' \
                     '上海市杨浦区北大道,同济大学四平路校区汇文楼,31.284421349,121.505040674 ' \
                     '上海市杨浦区四平路,同济大学-一·二九礼堂,31.281300899,121.50457045 ' \
                     '上海市杨浦区四平路1251号同济大学内,同济大学-一二九运动场,31.280124899,121.50387545 ' \
                     '上海市杨浦区四平路,同济大学中法中心,31.281052248,121.505131124 ' \
                     '上海市杨浦区文远路,同济大学城规D楼,31.284944248,121.505217124'
        self.locations = campus_loc.split(' ')

    def genSearchArgs(self):
        return random.choice(self.goods_names), random.choice(self.owner_names), \
               random.choice(self.locations).split(',')[1]

    def genReleaseArgs(self):
        return random.choice(self.goods_names), random.choice(self.owner_names), random.choice(self.locations)


    def genRecordSearchArgs(self):
        return random.choice(self.goods_names), random.choice(self.owner_names)


class RestfulApis:
    domain = 'https://xunhui.opencs.cn/api'

    # 调用一次API，并记录响应时间
    def __init__(self, log_name=''):
        self.f = open('outputs/{}'.format(log_name), 'w')

    def __del__(self):
        self.f.close()

    @response_time
    def releaseGoods(self, goods_name='', owner_name='', loc=''):
        biz_typo = random.randint(0, 1)
        goods_id = self.initGoods(owner_name, goods_name, loc, biz_typo)
        self.endCreateGoods(goods_id, biz_typo)

    def initGoods(self, owner_name='测试者', goods_name='', loc='', business_type=0, summary='性能测试'):
        url = self.buildApi('/goods/create')
        # '上海市杨浦区彰武路,同济大学四平路校区-图书馆,31.283310854,121.504270427'
        data = {
            'os_location': loc if business_type else '',
            'goods_name': goods_name,
            'mobile': '17717852647',
            'owner_name': owner_name,
            'summary': summary,
            'business_type': business_type,
            'location': '' if business_type else loc,
            'img_list': 'http://tmp/wx3a7bac4ab0184c76.o6zAJsyTdR5-7tTXbaZ78VVTtlBI.wXE2trQcvPnab0bf49b34f7e854791e85f13e4b9e5b3.jpg',
            'is_top': 0 if business_type else random.randint(0, 1),
            'days': 7,
            'edit': 0
        }
        res = requests.post(url=url, data=data, headers=self.getRequestHeaders())
        data = res.json()
        return data.get('data').get('id')

    def endCreateGoods(self, goods_id=0, business_type=0):
        url = self.buildApi('/goods/end-create')
        data = {'id': goods_id, 'business_type': business_type}
        res = requests.post(url=url, data=data, headers=self.getRequestHeaders())
        return res

    @response_time
    def getNewHintGoods(self):
        url = self.buildApi('/member/new/hint')
        auth = 'jNssQ1flutxjBE7sbA/oFOWWffKmiGA5Lc8ET223kHMUfTx/DNXL8WFrOgjY+X19'
        resp = requests.get(url, headers={'Authorization': auth})
        if resp.status_code != 200:
            raise Exception('出错了')

    @response_time
    def searchGoods(self, mix_kw, owner_name, address):
        url = self.buildApi('/goods/search', {'status': random.randint(0, 4),
                                              'business_type': random.randint(0, 1),
                                              'p': random.randint(0, 90),
                                              'mix_kw': mix_kw,
                                              'owner_name': owner_name,
                                              'filter_address': address})
        resp = requests.get(url=url)
        if resp.status_code != 200:
            raise Exception('出错了')

    @response_time
    def infoGoods(self):
        op_status = random.randint(-1, 6)
        url = self.buildApi('/goods/info', {'id': random.randint(1, 1000),
                                            'read': random.randint(0, 1),
                                            'op_status': op_status})
        if not random.randint(0, 5):
            # 5个人中有1个注册
            resp = requests.get(url=url, headers=self.getRequestHeaders())
        else:
            resp = requests.get(url=url)
        if resp.status_code != 200:
            raise Exception('出错了')


    @response_time
    def searchRecordGoods(self, mix_kw='', owner_name=''):
        url = self.buildApi('/record/search', params={'status': 1,
                                                      'mix_kw': mix_kw,
                                                      'owner_name': owner_name,
                                                      'p':random.randint(0, 10),
                                                      'op_status': random.randint(0, 6),
                                                      'only_new': random.choice(['true', 'false']),
                                                      'business_type': random.randint(0, 2)})
        resp = requests.get(url, headers=self.getRequestHeaders())
        if resp.status_code != 200:
            raise Exception('出错了')

    @response_time
    def getInfoMember(self):
        url = self.buildApi('/member/info')
        resp = requests.get(url, headers=self.getRequestHeaders())
        if resp.status_code != 200:
            raise Exception('出错了')

    @response_time
    def scanFreqQrcode(self):
        url = self.buildApi('/qrcode/scan/freq')
        resp = requests.get(url, data={'openid': 'opLxO5Q3CloBEmwcarKrF_kSA574'})
        if resp.status_code != 200:
            raise Exception('出错了')


    @log_api_param
    def buildApi(self, suffix, params=None):
        def buildQueryString():
            if params:
                return '?{}'.format("&".join(['{}={}'.format(k, v) for k, v in params.items()]))
            return ''

        url = "{}{}{}".format(self.domain, suffix, buildQueryString())
        return url

    def getRequestHeaders(self, other=False):
        auth = 'nnba8zOmAxvgYJDy743sLeWWffKmiGA5Lc8ET223kHMUfTx/DNXL8WFrOgjY+X19' if not other else ''
        content_type = 'application/x-www-form-urlencoded'
        return {'Authorization': auth, 'content-type': content_type}



