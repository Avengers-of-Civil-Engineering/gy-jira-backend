FROM python:3.9-slim

RUN sed -i "s@http://ftp.debian.org@https://repo.huaweicloud.com@g" /etc/apt/sources.list && \
    sed -i "s@http://security.debian.org@https://repo.huaweicloud.com@g" /etc/apt/sources.list && \
    sed -i "s@http://deb.debian.org@https://repo.huaweicloud.com@g" /etc/apt/sources.list && \
    apt-get install -y apt-transport-https ca-certificates


RUN apt-get update -y && apt-get -y install default-libmysqlclient-dev gcc && \
    mkdir -p /app/gy-jira-backend && \
    pip3 install -i https://mirrors.aliyun.com/pypi/simple \
      asgiref==3.5.0 \
      certifi==2021.10.8 \
      charset-normalizer==2.0.12 \
      Django==3.2.12 \
      django-environ==0.8.1 \
      django-filter==21.1 \
      djangorestframework==3.13.1 \
      gunicorn==20.1.0 \
      idna==3.3 \
      python-dateutil==2.8.2 \
      pytz==2021.3 \
      requests==2.27.1 \
      six==1.16.0 \
      sqlparse==0.4.2 \
      urllib3==1.26.8 \
      whitenoise==5.3.0 \
      mysqlclient==2.1.0 \
      Pillow==8.4.0 \
      djangorestframework-camel-case==1.3.0


WORKDIR /app/gy-jira-backend

COPY . /app/gy-jira-backend

RUN pip3 install -i https://mirrors.aliyun.com/pypi/simple -r requirements.txt

EXPOSE 8000

CMD ["python3", "bootstrap.py"]

