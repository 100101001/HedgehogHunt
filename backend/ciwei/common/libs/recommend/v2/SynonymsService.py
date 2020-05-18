# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/4/16 上午3:07
@file: SynonymsService.py
@desc: 
"""
import jieba.analyse

from common.libs.recommend.preprocess.SynonymProcess import SynonymsProcess
from common.loggin.time import time_log


class SynonymsService:

    def __init__(self):
        self.sym_key, self.sym_dict = SynonymsProcess.loadSymDictV2()

    @time_log
    def getWordClasses(self, input_word):
        key_words = self.extractKeywords(input_word)
        if len(key_words) > 0:
            noun = key_words[0]
        else:
            noun = input_word
        ret_dict = {
            'noun': self.sym_key.get(noun, []),  # ['类别KEY1', '类别KEY2'...]
            'adj': []   # ['类别KEY11', '类别KEY12', '类别KEY21', '类别KEY22'...]
        }
        for kw in key_words[1:]:
            vec = self.sym_key.get(kw, None)
            if vec:
                ret_dict['adj'].extend(vec)
        return ret_dict

    @time_log
    def getSearchWords(self, input_word):
        key_words = self.extractKeywords(input_word)
        if len(key_words) > 0:
            noun = key_words[0]
        else:
            noun = input_word
        ret_dict = {
            'noun': self.sym_dict.get(noun, [noun]),  # ['长裙', '长纱'...]
            'adj': []  # [淡黄', '嫩黄'..., '蓝色', '青色'...]
        }
        for kw in key_words[1:]:
            vec = self.sym_dict.get(kw, [kw])  # ['淡黄']
            ret_dict['adj'].extend(vec)
        return ret_dict

    @classmethod
    @time_log
    def extractKeywords(cls, search_words):
        key_words = jieba.analyse.extract_tags(search_words)
        return key_words

    def getWordClassesSync(self, input_word):
        """
        同步物品到redis需要,不分词性的返回
        :param input_word:
        :return:
        """
        key_words = self.extractKeywords(input_word)
        ret_list = []
        for kw in key_words:
            vec = self.sym_key.get(kw, None)
            if vec:
                ret_list.extend(vec)
        return ret_list


if __name__ == "__main__":
    pass