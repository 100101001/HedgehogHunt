def transform():
    filename = "C:\\Users\\\I354829\\PycharmProjects\\utils\\HIT-IRLab-gb2312.txt"
    filename2 = "C:\\Users\\\I354829\\PycharmProjects\\utils\\HIT-IRLab-utf-8.txt"
    with open(filename, 'r', encoding="GBK") as f:
        with open(filename2, 'w', encoding='utf-8') as f2:
            i = 0
            for row_ in f:
                row = row_.encode('utf-8').decode('utf-8')
                f2.write(row)


def file2dic():
    import pickle
    filename = "C:\\Users\\\I354829\\PycharmProjects\\utils\\HIT-IRLab-utf-8.txt"
    sym_words = []
    # sym_class_words = []
    sym_dict = {}
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
                    if w not in sym_dict:
                        sym_dict[w] = [index]
                    else:
                        sym_dict[w].append(index)
    output1 = "synonyms_index.pk"
    output2 = "synonyms_words.pk"
    with open(output1, 'wb') as f:
        pickle.dump(sym_dict, f)
    with open(output2, 'wb') as f:
        pickle.dump(sym_words, f)


def loadSymDict():
    """

    :return:
    """
    import pickle
    pickle_input1 = "synonyms_index.pk"
    pickle_input2 = "synonyms_words.pk"
    with open(pickle_input1, 'rb') as f:
        index = pickle.load(f)
    with open(pickle_input2, 'rb') as f2:
        words = pickle.load(f2)
    return index, words


if __name__ == "__main__":
    #file2dic()
    import jieba
    a = jieba.cut('nike鞋')
    a = list(a)
    sym_index, sym_words = loadSymDict()
    for i in sym_index['nike鞋']:
        print(sym_words[i])
    # print(sym_words[sym_index['钱包']])


