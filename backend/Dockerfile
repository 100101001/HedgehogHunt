FROM python:3.6

ENV PYTHONUNBUFFERED 1
ENV FLASK_APP application.py
ENV FLASK_RUN_HOST 0.0.0.0


ADD ./ciwei /code

WORKDIR /code

RUN pip install -r requirements-versioned.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

#CMD ["python","/code/manager.py","runserver"]


