闪寻
=====================
## 启动

    uwsgi --ini uwsgi-local.ini # 启动
    uwsgi --reload logs/uwsgi.pid # 重启
    uwsgi --stop logs/uwsgi.pid # 关闭


##启动

     export ops_config=local|production && python manage.py runserver

##flask-sqlacodegen

    flask-sqlacodegen 'mysql://root:123456@127.0.0.1/goods_db' --outfile "common/models/model.py"  --flask
    flask-sqlacodegen 'mysql://root:wcx9517530@127.0.0.1/goods_db' --tables  --outfile "common/models/Image.py"  --flask

## flask-migration
    export FLASK_APP=manager.py            # 设置环境变量
    flask db init                          # 执行一次生成migrations目录即可
    flask db migrate -m "新增匹配次数列"     # 生成数据库迁移脚本
    flask db upgrade                      # 运行迁移脚本
    flask db downgrade                    # 回滚迁移

## API 测试
    # create new test class -> CTRL+SHIFT+T ->  target_directory(under tests package)
    # write a test class
    from tests.utils.TestHelper import ApiBaseTest  
    class testXXX(ApiBaseTest):
        def setUp(self)->None:
            super.setUp()
            # customize data preparaotion here
            
        def test_method1(self):
            res = do_something
            self.assrtTrue(res.statusCode == 200, "msg")
        
        def tearDown(self):
            super().tearDown()
            # customize operations here
    

##可参考资料
* [python-Flask（jinja2）语法：过滤器](https://www.jianshu.com/p/3127ac233518)
* [SQLAlchemy 各种查询语句写法](https://wxnacy.com/2017/08/14/python-2017-08-14-sqlalchemy-filter/)
* [SQLAlchemy 高级用法](https://www.cnblogs.com/coder2012/p/4746941.html)
* [flask-migration 操作指南](migrations/操作指南.md)
* [uwsgi文件参数解释](https://www.cnblogs.com/tortoise512/p/10825075.html)
* [uwsgi配置](https://www.jianshu.com/p/07458e99198a)