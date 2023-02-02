FROM python:3.7
ENV PYTHONUNBUFFERED 1
RUN apt-get -y update
RUN apt-get -y install git nano
COPY /requirements.txt /incentive_server/requirements.txt
RUN pip install --upgrade pip && pip install -r incentive_server/requirements.txt
RUN pip install mysqlclient  uwsgi django-dotenv
COPY . /incentive_server

RUN cd incentive_server
WORKDIR /incentive_server