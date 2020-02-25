FROM python:3.6

ENV PYTHONUNBUFFERED 1

ADD ./ciwei /code

WORKDIR /code

RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

#CMD ["python","/code/manager.py","runserver"]


