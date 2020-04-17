### 预处理数据说明

synonyms_dict.pk

    映射关系:
    原来的词 -> 同义词列表
    '人' -> ['人', '士', '人物', '人士', '人氏', '人选', '身体', ...]   
    

synonyms_dict_for_sql_search.pk
    
    映射关系：
    原来的词 -> 适用于模糊匹配的同义词列表
     '人' -> ['%人%', '%士%', '%人%物%', '%人%士%', '%人%氏%', '%人%选%', '%身%体%', ...]  
    
    用法：
    goods_name ——(查pickle)——> 可用于模糊匹配的同义词列表 ——(查Mysql)——> [goods_id list] 
    无同义词的处理：
    goods_name ——(查pickle)——> [goods_name] ——(查Mysql)——> [goods_id list] 
    
    
synonyms_dict_for_redis_search.pk

    pickle中的映射关系:
    原来的词 -> 所属类别列表
    ‘人’ -> ['Aa01A01', 'Dd17A02', ...]
    
    redis中的映射关系：
    redis分库存储失物和拾物,存储的映射关系：
    类别 -> 所属类别的物品集合(可附带必要的数据信息)
    'Aa01A01' -> {'1', '10', '12',...} 
    
    用法：
    情况1、Noun有同义词的:
    goods_name的名词 ——(查pickle)——> noun.词所属类别列表 ——(查redis)——> {good_id set1} ∪ {goods_id set2} = {Noun set}
    goods_name的定语 ——(查pickle)——> adj.词所属类别列表 ——(查redis)——> {good_id set1} ∪ {goods_id set2} = {Adjective set}
    综上：得到 {Noun匹配的id}, {Adj匹配的id}，接着做以下步骤
    × 对{Noun}进行地理筛选，得到初步的集合 {Target Noun}，集合内所有goods权重为1。
    × 最后逐一与 {Adj} 进行交集运算，每做一次存留下来的goods，权重加1，最后记录到Recommend表中，加上权重列。
 
    情况2、Noun无同义词的处理： fallback逻辑只能靠ES增强
    × goods_name的名词 ——(查pickle)——> fallback ——(抽取的关键词{Noun和Adj}和类别索引查ES)——> {goods_ids}
    综上：得到同类别的 {Noun 匹配的id}, {Adj 匹配的id}, 接着做的步骤同上，不再赘述
    
    存储工作：
    goods_name抽取的关键词 ——> 建立反向索引存ES 
    goods_name所属的同义词类别列表——> 循环加入对应的redis的set ——> sadd 'Aa01A01' "id, lng, lat"
    
    
    
 