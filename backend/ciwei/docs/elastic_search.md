### ES 使用示例


插入推荐数据

    es.create(index='goods', doc_type='recommend', id=2,
           body={
               'id': 2,
               'goods_name': '蓝色的长裙',
               'category': 10,
               'business_type': 1,
               'lng': '121.2121,
               'lat': '31.121',
           })
               
    es.create(index='goods', doc_type='recommend', id=1,
          body={
              'id': 1,
              'goods_name': '淡黄的长裙',
              'category': 10,
              'business_type': 1,
              'lng': '121.2121,
              'lat': '31.121'
          })
               
查询数据

    body = {
        'query': {
            'bool': {
                'must': [
                    {
                        'match': {
                            'goods_name': '长裙'
                        },

                    },
                    {
                        'match': {
                            'category': 6
                        }
                    }
                ],
                'should': [
                    {
                        'match': {
                            'goods_name': '淡黄'
                        }
                    }
                ]
            }
        }
    }
    
    res = es.search(index='goods', doc_type='recommend', body=body)
    耗时：10^-2级别
    redis耗时： 10^-3级别
    CPU计算耗时：10^-6级别
    
    
    res的结果：
    {
      "_shards": {
        "failed": 0, 
        "skipped": 0, 
        "successful": 1, 
        "total": 1
      }, 
      "hits": {
        "hits": [
          {
            "_id": "1", 
            "_index": "goods", 
            "_score": 2.7509375, 
            "_source": {
              "business_type": 1, 
              "category": 10, 
              "goods_name": "\u6de1\u9ec4\u7684\u957f\u88d9", 
              "id": 1, 
              "lng": '121.2121,
              "lat": '31.121',
            }, 
            "_type": "recommend"
          }, 
          {
            "_id": "2", 
            "_index": "goods", 
            "_score": 1.3646431, 
            "_source": {
              "business_type": 1, 
              "category": 10, 
              "goods_name": "\u84dd\u8272\u7684\u957f\u88d9", 
              "id": 2, 
              "lng": '121.2121,
              "lat": '31.121',
            }, 
            "_type": "recommend"
          }
        ], 
        "max_score": 2.7509375, 
        "total": {
          "relation": "eq", 
          "value": 2
        }
      }, 
      "timed_out": false, 
      "took": 10
    }
    
    
创建索引

        mappings = {
        "properties": {
            "appeal_time": {
                "type": "date"
            },
            "avatar": {
                "type": "keyword",
                "index": "false"
            },
            "business_type": {
                "type": "byte"
            },
            "confirm_time": {
                "type": "date",
            },
            "created_time": {
                "type": "date",
            },
            "finish_time": {
                "type": "date",
            },
            "id": {
                "type": "long"
            },
            "lat": {
                "type": "float",
                "index": "false"
            },
            "lng": {
                "type": "float",
                "index": "false"
            },
            "loc": {
                "type": "text"
            },
            "os_location": {
                "type": "text"
            },
            "location": {
                "type": "keyword",
                "index": "false"
            },
            "main_image": {
                "type": "keyword",
                "index": "false"
            },
            "member_id": {
                "type": "long"
            },
            "openid": {
                "type": "keyword"
            },
            "mobile": {
                "type": "keyword",
                "index": "false"
            },
            "name": {
                "type": "text"
            },
            "nickname": {
                "type": "keyword",
                "index": "false"
            },
            "owner_name": {
                "type": "text"
            },
            "pics": {
                "type": "keyword",
                "index": "false"
            },
            "qr_code_openid": {
                "type": "keyword"
            },
            "report_status": {
                "type": "byte"
            },
            "return_goods_id": {
                "type": "long"
            },
            "return_goods_openid": {
                "type": "keyword"
            },
            "status": {
                "type": "byte"
            },
            "summary": {
                "type": "text"
            },
            "thank_time": {
                "type": "date"
            },
            "top_expire_time": {
                "type": "date"
            },
            "updated_time": {
                "type": "date"
            },
            "view_count": {
                "type": "integer"
            },
            "user_id": {
                "type": "integer"
            }
        }
    }

    body = {
        "settings": {
            "number_of_shards": 3,
            "number_of_replicas": 1
        },
        "mappings": mappings
    }
    res = es.indices.create(index="goods", body=body)

curl 操作
    
    # 删除索引
    curl -XDELETE localhost:9200/goods?pretty
    # 删除所有记录
    curl -XPOST localhost:9200/goods/_delete_by_query -H "Content-Type:application/json" -d '{"query":{"match_all":{}}}'
    # 删除拾物   
    curl -XPOST localhost:9200/goods/_delete_by_query -H "Content-Type:application/json" -d '{"query":{"match":{"business_type":1}}}'
    # 删除寻物
    curl -XPOST localhost:9200/goods/_delete_by_query -H "Content-Type:application/json" -d '{"query":{"match":{"business_type":0}}}'
    # 按id删除
    curl -XDELETE localhost:9200/goods/_doc/${id}?pretty
    # 查询所有记录
    curl localhost:9200/goods/_doc?pretty -H "Content-Type:application/json" -d '{"query":{"match_all":{}}}'
    # 按id查询
    curl localhost:9200/goods/_doc/${id}?pretty
    # 按id更新
    curl -XPOST localhost:9200/goods/_doc/${id}/_update?pretty -H "Content-Type:application/json" -d '{"doc" : {"member_id": 100004 ,"openid":"opLxO5cE7MXKPxj2ndOxnvxkoek0", , "nickname": "lpx", "avatar":"https://wx.qlogo.cn/mmopen/vi_32/Q0j4TwGTfTKeoQUBJZ40FDibYOQKAYJJGXxMWZ8FehDrNZ4gYw98qwMaCyPBwDd1kbLqa1Z3mUTOdAZjchIYcLw/132"}}'
    update goods set member_id=100004,openid='opLxO5cE7MXKPxj2ndOxnvxkoek0',nickname='lpx',avatar='https://wx.qlogo.cn/mmopen/vi_32/Q0j4TwGTfTKeoQUBJZ40FDibYOQKAYJJGXxMWZ8FehDrNZ4gYw98qwMaCyPBwDd1kbLqa1Z3mUTOdAZjchIYcLw/132' where id=${id};

gitk --all $( git fsck --no-reflog | awk '/dangling commit/ {print $3}' )

