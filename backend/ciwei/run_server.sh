#!/bin/bash
uwsgi --ini /code/uwsgi_docker.ini & \
sleep 10s & \
celery -A application.celery worker -Q log_queue,sync_queue,recommend_queue,subscribe_queue,sms_queue,mall_queue -l info & \
celery -A application.celery beat -l info  -s "logs/celery/celerybeat-schedule" --pidfile=
