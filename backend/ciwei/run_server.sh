#!/bin/bash

#启动flask
# python /code/manager.py runserver &
uwsgi --ini /code/uwsgi_docker.ini &
#启动worker
celery -A application.celery worker -Q log_queue,sync_queue,recommend_queue,subscribe_queue,sms_queue,mall_queue -l info &
#启动beat
celery -A application.celery beat -l info
