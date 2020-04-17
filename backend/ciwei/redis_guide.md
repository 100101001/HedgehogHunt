## Redis 操作约定

数据库清空指令
    
    127.0.0.1:6379[3]> flushdb
    OK


数据库存储约定

    数据库0 存放celery任务结果
    127.0.0.1:6379> keys *
    1) "celery-task-meta-1821eba0-f205-4e1f-8e7e-8713058f613f"
    2) "celery-task-meta-40f857d1-8c45-4f3d-8980-bc5c475561db"
    3) "celery-task-meta-dc2e619c-b50e-44ae-82d6-532e8a296b0a"
    4) "celery-task-meta-da5bf780-61d2-4a5a-b2a7-2ede5c9cb569"
    5) "celery-task-meta-826318e4-28c7-45f5-b698-b5c378cd93bc"
    6) "celery-task-meta-53a4a7ea-2e6c-49f9-8414-ae66cde27ef4"
    127.0.0.1:6379> get celery-task-meta-1821eba0-f205-4e1f-8e7e-8713058f613f
    "{\"status\": \"SUCCESS\", \"result\": \"can i be used by other celery task?\", \"traceback\": null,
    \"children\": [], \"date_done\": \"2020-04-14T17:22:42.207089\", \"parent_id\": \"40f857d1-8c45-4f3d-8980-bc5c475561db\",
    \"task_id\": \"1821eba0-f205-4e1f-8e7e-8713058f613f\"}"

    数据库1 存放数据缓存（mark+${good_id}=>{mark_member_id}）认领信息 （recommend_+${good_id}=>{recommend_member_id}）推荐数据 （member_${member_id}=>member_info）身份信息
    127.0.0.1:6379[1]> keys *
    1) "member_100001"
    2) "mark_31"
    3) "mark_3"
    4) "member_100002"
    127.0.0.1:6379[1]> smembers mark_3
    1) "-1"
    2) "100001"
    127.0.0.1:6379[1]> smembers mark_31
    1) "-1"
    127.0.0.1:6379[1]> get member_100001
    "{\"id\": 100001, \"user_id\": 0, \"nickname\": \"\\u7ba1\\u7406\\u5458\", \"salt\": \"\", \"credits\": 265, \"balance\"
    : 4.73, \"mobile\": \"bPk3u33u+sqUiuxJ/+ubfQ==\", \"name\": \"\\u674e\\u4f69\\u7487\", \"location\": \"\", \"sex\": 2,
     \"avatar\": \"https://wx.qlogo.cn/mmopen/vi_32/7jCR4QflwchksTBcyakicSepWVQdfbHIQL2glRrkY7ic52iaXqfuBb2tlQ8ELlaGWZDXFgKM4zAMeQZSiaaJtibI3gQ/132\",
     \"qr_code\": \"20200316/687bee77-e5bf-44b8-b341-d63f1abdc853.jpg\", \"left_notify_times\": 0, \"openid\": \"opLxO5fubMUl7GdPFgZOUaDHUik8\",
     \"status\": 1, \"updated_time\": \"2020-04-14 04:02:04\", \"created_time\": \"2020-03-08 09:31:56\"}"


    数据库2 用于物品状态cas
    127.0.0.1:6379[2]> keys *
    1) "29"
    2) "30"
    3) "3"
    4) "8"
    5) "31"
    6) "12"
    127.0.0.1:6379[2]> get 30
    "1"
    127.0.0.1:6379[2]> get 12
    "1"
    
    数据库4和3 存放匹配范围的捡到的东西和丢的东西
    127.0.0.1:6379[4]> select 4
    OK
    127.0.0.1:6379[4]> keys *
    1) "1"
    2) "Dd08A02"
    3) "Bq03A15"
    127.0.0.1:6379[4]> get 1
    "Bq03A15,Dd08A02"
    127.0.0.1:6379[4]> hvals Dd08A02
    1) "{\"id\": 1, \"lng\": 31.132386108, \"lat\": 121.423386047, 
    \"member_id\": 100002, \"name\": \"\\u5916\\u8863\",
     \"created_time\": \"2020-04-17 20:48\", 
     \"loc\": \"\\u6885\\u9647\\u5341\\u675147\\u53f7\"}"



参考指南
 * [redis入门](http://try.redis.io/)
 * [redis cas 实现](https://www.jianshu.com/p/458947bca341)