FROM python:3.6

ENV PYTHONUNBUFFERED 1
ENV PRODUCTION 1
ENV PRODUCTION_TEST 0

ADD ./ciwei /code

WORKDIR /code

# https://pypi.tuna.tsinghua.edu.cn/simple 大包阿里云经常请求超时，更换下述豆瓣镜像源
RUN pip install -r requirements-versioned.txt -i https://pypi.doubanio.com/simple/

#CMD ["python","/code/manager.py","runserver"]
# ENTRYPOINT ["run_server.sh"] 

