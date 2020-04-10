# encoding: utf-8
"""
@author: github/100101001
@contact: 17702113437@163.com
@time: 2020/4/10 下午3:42
@file: SynonymsService.py
@desc:
"""


class SynonymsProcess:

    # @staticmethod
    # def gbk2utf8():
    #     filename = "C:\\Users\\\I354829\\PycharmProjects\\utils\\HIT-IRLab-gb2312.txt"
    #     filename2 = "C:\\Users\\\I354829\\PycharmProjects\\utils\\HIT-IRLab-utf-8.txt"
    #     with open(filename, 'r', encoding="GBK") as f:
    #         with open(filename2, 'w', encoding='utf-8') as f2:
    #             for row_ in f:
    #                 row = row_.encode('utf-8').decode('utf-8')
    #                 f2.write(row)

    @staticmethod
    def file2dic():
        import pickle
        from pybloom_live import BloomFilter
        bf = BloomFilter(capacity=100000, error_rate=0.0001)
        filename = "HIT-IRLab-utf-8.txt"
        sym_words = []
        # sym_class_words = []
        sym_dict = {}
        words_set = set()
        with open(filename, 'r', encoding="utf-8") as f:
            for row in f:
                row = row.replace('\n', '')
                items = row.split(' ')
                cls = items[0]
                words = items[1:]
                # 同义词
                if cls[-1] == '=':
                    sym_words.append(words)
                    index = len(sym_words) - 1
                    for w in items:
                        words_set.add(w)
                        bf.add(w)
                        if w not in sym_dict:
                            sym_dict[w] = [index]
                        else:
                            sym_dict[w].append(index)
        err_hit = 0
        for w in words_set:
            if w not in bf:
                err_hit += 1
        print("error_hits" + str(err_hit))
        print("err_rate" + str(err_hit * 100 / len(words_set)))
        output1 = "synonyms_index.pk"
        output2 = "synonyms_dict.pk"
        output3 = "synonyms_words.pk"
        with open(output1, 'wb') as f:
            pickle.dump(sym_dict, f)
        with open(output2, 'wb') as f:
            pickle.dump(sym_words, f)
        with open(output3, 'wb') as f:
            pickle.dump(bf, f)

    @staticmethod
    def loadSymDict():
        """

        :return:
        """
        import pickle
        pickle_input1 = "synonyms_index.pk"
        pickle_input2 = "synonyms_dict.pk"
        pickle_input3 = "synonyms_words.pk"
        with open(pickle_input1, 'rb') as f:
            index = pickle.load(f)
        with open(pickle_input2, 'rb') as f:
            synonym_dict = pickle.load(f)
        with open(pickle_input3, 'rb') as f:
            words = pickle.load(f)
        return words, index, synonym_dict


if __name__ == "__main__":
    pass
    # SynonymsProcess.file2dic()
    # import jieba
    #
    # a = jieba.cut('nike鞋')
    # a = list(a)
    # sym_words, sym_index, sym_dict = SynonymsProcess.loadSymDict()
    # if 'nike鞋' in sym_words:
    #     for i in sym_index['nike鞋']:
    #         print(sym_dict[i])
    # else:
    #     print("no synonyms")
