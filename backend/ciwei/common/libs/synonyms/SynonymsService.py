# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/4/10 下午5:43
@file: SynonymsService.py
@desc: 
"""
from common.libs.synonyms.preprocess.SynonymProcess import SynonymsProcess


class SynonymsService:

    def __init__(self):
        self.sym_words, self.sym_index, self.sym_dict = SynonymsProcess.loadSymDict()

    def getSearchWords(self, input_word):
        if input_word not in self.sym_words:
            return input_word
        synonyms = set()
        for i in self.sym_index['nike鞋']:
            synonyms.add(self.sym_dict[i])
        return synonyms


if __name__ == "__main__":
    pass
