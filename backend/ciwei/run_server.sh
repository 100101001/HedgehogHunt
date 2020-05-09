#!/bin/bash

#启动flask
# python /code/manager.py runserver &
uwsgi --ini uwsgi-local.ini &
#启动worker
#celery worker -A celery_tasks.main -l info -f /opt/hrms/logs/celery.log &   #这里注意日志位置要写绝对路径
celery -A application.celery worker -Q log_queue,sync_queue,recommend_queue,subscribe_queue,sms_queue,mall_queue -l info &
#启动beat
celery -A application.celery beat -l info
