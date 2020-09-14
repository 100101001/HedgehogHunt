## Celery异步任务


#### RMQ的安装与使用
* RabbitMQ作异步任务的消息队列中间件


    # UBUNTU 安装
    sudo apt-get install rabbitmq-server
    # CENTOS7 安装
    yum -y update
    yum -y install epel-release
    yum -y update
    yum -y install erlang socat
    wget https://www.rabbitmq.com/releases/rabbitmq-server/v3.6.10/rabbitmq-server-3.6.10-1.el7.noarch.rpm
    rpm –import https://www.rabbitmq.com/rabbitmq-release-signing-key.asc
    rpm -Uvh rabbitmq-server-3.6.10-1.el7.noarch.rpm
    # 直接查看状态
    sudo service rabbitmq-server status
    # 开启web管理 http://192.168.0.116:15672/ 默认guest@guest
    ellen@ubuntu:~$ sudo rabbitmq-plugins enable rabbitmq_management
    The following plugins have been enabled:
      amqp_client
      cowlib
      cowboy
      rabbitmq_web_dispatch
      rabbitmq_management_agent
      rabbitmq_management
    
    Applying plugin configuration to rabbit@ubuntu... started 6 plugins.
    
    # 创建用户，host
    ellen@ubuntu:~$ sudo rabbitmqctl add_user root wcx9517530
    Creating user "root"
    ellen@ubuntu:~$ sudo rabbitmqctl add_vhost ciwei
    Creating vhost "ciwei"
    ellen@ubuntu:~$ sudo rabbitmqctl set_user_tags root celery_user
    Setting tags for user "root" to [celery_user]
    ellen@ubuntu:~$  sudo rabbitmqctl set_permissions -p ciwei root ".*" ".*" ".*"
    Setting permissions for user "root" in vhost "ciwei"
    ellen@ubuntu:/etc/rabbitmq$ sudo rabbitmqctl  change_password root  'qweasd123'
    Changing password for user "root"
    ellen@ubuntu:/etc/rabbitmq$ sudo rabbitmqctl set_user_tags root administrator
    Setting tags for user "root" to [administrator]

    # 修改配置文件 /etc/rabbitmq/rabbitmq.config 目配置可远程登录
    ellen@ubuntu:/etc/rabbitmq$ ll
    total 28
    drwxr-xr-x   2 rabbitmq rabbitmq  4096 4月  11 17:54 ./
    drwxr-xr-x 133 root     root     12288 4月  11 18:10 ../
    -rw-r--r--   1 root     root        23 4月  11 17:42 enabled_plugins
    -rw-r--r--   1 root     root       247 4月  11 17:54 rabbitmq.config
    -rw-r--r--   1 rabbitmq rabbitmq   535 4月  11 16:35 rabbitmq-env.conf
    ellen@ubuntu:/etc/rabbitmq$ cat rabbitmq.config 
    [
     {rabbit,
      [%%
      %% Network Connectivity
      %% ====================
      %%
      %% By default, RabbitMQ will listen on all interfaces, using
      %% the standard (reserved) AMQP port.
      %%
      {tcp_listeners, [5672]},
      {loopback_users, ["root"]}
      ]}
    ].

    

### Redis的安装与使用
* redis 作异步任务结果存储


    # 安装
    ellen@ubuntu:/etc/rabbitmq$ sudo apt-get install redis-server
    # 命令行界面
    ellen@ubuntu:/etc/rabbitmq$ redis-cli
    127.0.0.1:6379> keys *
    127.0.0.1:6379> get $(key) 
    ellen@ubuntu:/etc/rabbitmq$ redis-server


### Flask_Celery的安装与使用

* Flask_Celery在应用程序中向消息队列放任务，起Worker从消息队列中取任务后台异步运行，任务执行结果存到redis，也可将异步任务结果从redis取回到应用程序

在依赖文件中

    # 异步任务插件依赖(发送消息到消息队列,起后台worker,写结果,获取结果等)
    flask_celery
    # 存储异步任务执行结果
    flask-redis

在代码中

    # common.tasks.main.py
    import flask
    from celery import Celery
    
    
    class FlaskCelery(Celery):
    
        def __init__(self, *args, **kwargs):
    
            super(FlaskCelery, self).__init__(*args, **kwargs)
            self.patch_task()
    
            if 'app' in kwargs:
                self.init_app(kwargs['app'])
    
        def patch_task(self):
            TaskBase = self.Task
            _celery = self
    
            class ContextTask(TaskBase):
                abstract = True
    
                def __call__(self, *args, **kwargs):
                    if flask.has_app_context():
                        return TaskBase.__call__(self, *args, **kwargs)
                    else:
                        with _celery.app.app_context():
                            return TaskBase.__call__(self, *args, **kwargs)
    
            self.Task = ContextTask
    
        def init_app(self, app):
            self.app = app
            self.config_from_object(app.config)

在application.py中

    # 异步和定时任务
    celery = FlaskCelery()
    app = Application()
    # 在Application的构造__init__函数中加入,加载celery配置
    celery.init_app(self)

起worker和beat的命令
   
    celery -A application.celery worker -Q log_queue,sync_queue,recommend_queue,subscribe_queue,sms_queue -l info 
    celery -A application.celery beat  -l info --piddile=
    # celery beat -A celery_schedule -l info -f logging/schedule_tasks.log --detach
参考资料

* [Flask-Celery-Background-Task](https://flask.palletsprojects.com/en/1.1.x/patterns/celery/)
* [Flask-reids](https://pypi.org/project/flask-redis/)
* [Celery-Gettting-Started-Brokers](https://celery.readthedocs.io/en/latest/getting-started/brokers/rabbitmq.html#broker-rabbitmq)
* [消息队列之RMQ](https://www.jianshu.com/p/79ca08116d57/)
* [Celery-Getting-Started](https://celery.readthedocs.io/en/latest/getting-started/first-steps-with-celery.html#redis)
* [Celery-Distributed Task Queue](http://docs.celeryproject.org/en/latest/index.html)
* [空间距离计算](http://www.cocoachina.com/articles/10238)
* [Celery-Flask-RMQ最佳实践](https://www.jianshu.com/p/807efde55d81)
* [Celery-Flask 发短信](https://blog.csdn.net/weixin_40612082/article/details/81149592?fps=1&locationNum=2)
* [Celery 配置日志输出文件](https://www.cnblogs.com/zhangweijie01/p/11813215.html)