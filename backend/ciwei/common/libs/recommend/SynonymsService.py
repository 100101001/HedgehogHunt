# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/4/10 下午5:43
@file: SynonymsService.py
@desc: 
"""
from common.libs.recommend.preprocess.SynonymProcess import SynonymsProcess

import jieba.analyse


class SynonymsService:

    def __init__(self):
        self.sym_dict = SynonymsProcess.loadSymDict()

    def getSearchWords(self, input_word=""):
        """
        获取搜索同义词
        :param input_word:
        :return:
        """
        key_words = self.processSearchWords(input_word)
        synonyms = self.sym_dict.get(key_words, ['%' + ('%'.join([ch for ch in key_words]) + '%')])
        return list(synonyms)

    @classmethod
    def processSearchWords(cls, search_words):
        key_words = jieba.analyse.extract_tags(search_words)
        return key_words[0] if key_words else search_words


if __name__ == "__main__":
    pass
