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
        # A0123 =  ‘皮夹’, ‘腰包’, ‘钱包’  <==>  0 -> ‘皮夹’, ‘腰包’, ‘钱包’
        # A0124 =  ‘人’, ‘成年’, ‘男人’  <==>  1 -> ‘人’, ‘成年’, ‘男人’
        sym_words_matrix = []
        sym_search_words_matrix = []
        # sym_class_words = []
        # ‘钱包’ -> [0]
        # ‘人’ -> [1, 655]
        sym_words_index = {}
        words_set = set()
        with open(filename, 'r', encoding="utf-8") as f:
            for row in f:
                row = row.replace('\n', '')
                items = row.split(' ')
                cls = items[0]
                line_words = items[1:]
                line_search_words = ['%' + '%'.join([i for i in w]) + '%' for w in line_words]
                # 同义词
                if cls[-1] == '=':
                    sym_search_words_matrix.append(line_search_words)
                    sym_words_matrix.append(line_words)
                    index = len(sym_words_matrix) - 1
                    for w in line_words:
                        words_set.add(w)
                        bf.add(w)
                        if w not in sym_words_index:
                            sym_words_index[w] = [index]
                        else:
                            sym_words_index[w].append(index)

        # ‘钱包’ -> ‘皮夹’, ‘腰包’, ‘钱包’
        # 原来 ‘钱包’ -> [0, 1] ->  ‘皮夹’, ‘腰包’, ‘钱包’
        res_dict = {}
        for w in words_set:
            # '' -> [0, 1, 2]
            for i in sym_words_index[w]:
                if w not in res_dict:
                    # 0 -> '', '', ''
                    res_dict[w] = set(sym_words_matrix[i])
                else:
                    # 0 -> '', '', ''
                    res_dict[w] = res_dict[w].union(sym_words_matrix[i])

        output1 = "synonyms_dict.pk"
        with open(output1, 'wb') as f:
            pickle.dump(res_dict, f)

        # ‘钱包’ -> ‘%皮%夹%’, ‘%腰%包%’, ‘%钱%包%’
        # 原来  # ‘钱包’ -> ‘皮夹’, ‘腰包’, ‘钱包’
        res_dict_search = {}
        for w in words_set:
            # ''-> [0, 1, 2]
            for i in sym_words_index[w]:
                if w not in res_dict_search:
                    # 0 -> '', '', ''
                    res_dict_search[w] = set(sym_search_words_matrix[i])
                else:
                    # 0 -> '', '', ''
                    res_dict_search[w] = res_dict_search[w].union(sym_search_words_matrix[i])

        output2 = "synonyms_dict_for_sql_search.pk"
        with open(output2, 'wb') as f:
            pickle.dump(res_dict_search, f)

    @staticmethod
    def file2dic_for_redis():
        import pickle
        filename = "HIT-IRLab-utf-8.txt"
        # A0123 =  ‘皮夹’, ‘腰包’, ‘钱包’  <==>  0 -> ‘皮夹’, ‘腰包’, ‘钱包’
        # A0124 =  ‘人’, ‘成年’, ‘男人’  <==>  1 -> ‘人’, ‘成年’, ‘男人’

        word_cls_map = {}
        # ‘钱包’ -> [0]
        # ‘人’ -> [1, 655]
        with open(filename, 'r', encoding="utf-8") as f:
            for row in f:
                row = row.replace('\n', '')
                items = row.split(' ')
                cls = items[0]
                line_words = items[1:]
                # 同义词
                if cls[-1] in ('=', '@'):
                    for w in line_words:
                        if w not in word_cls_map:
                            word_cls_map[w] = [cls[:-1]]
                        else:
                            word_cls_map[w].append(cls[:-1])
        output = "synonyms_dict_for_redis_search.pk"
        with open(output, 'wb') as f:
            pickle.dump(word_cls_map, f)

    @staticmethod
    def loadSymDict():
        """

        :return:
        """
        import pickle
        from application import APP_ROOT
        pickle_input1 = APP_ROOT+"/common/libs/recommend/preprocess/synonyms_dict_for_sql_search.pk"
        with open(pickle_input1, 'rb') as f:
            synonym_dict = pickle.load(f)
        return synonym_dict

    @staticmethod
    def loadSymDictV2():
        """

        :return:
        """
        import pickle
        from application import APP_ROOT
        pickle_input1 = APP_ROOT + "/common/libs/recommend/preprocess/synonyms_dict_for_redis_search.pk"
        pickle_input2 = APP_ROOT + "/common/libs/recommend/preprocess/synonyms_dict.pk"
        with open(pickle_input1, 'rb') as f:
            synonym_key = pickle.load(f)
        with open(pickle_input2, 'rb') as f:
            synonym_dict = pickle.load(f)
        return synonym_key, synonym_dict


if __name__ == "__main__":

    #pass
    #SynonymsProcess.file2dic_for_redis()
    #sym_words = SynonymsProcess.loadSymDict()
    #a,b  =SynonymsProcess.loadSymDictV2()
    #c = a.get('外套')
    print("")
    # if '钱包' in sym_words:
    #     print(sym_dict.get('钱包', ''))
    # else:
    #     print("no recommend")
