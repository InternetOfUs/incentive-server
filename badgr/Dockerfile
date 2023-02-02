FROM ubuntu:18.04

# Preparation
RUN apt-get update --fix-missing

# Install server dependencies
RUN apt-get install -y curl git git-core python-virtualenv gcc python-pip python-dev libjpeg-turbo8 libjpeg-turbo8-dev zlib1g-dev libldap2-dev libsasl2-dev swig libxslt-dev automake autoconf libtool libffi-dev libcairo2-dev libssl-dev
RUN pip install virtualenv --upgrade
#RUN apt install libjpeg8-dev zlib1g-dev -y libcairo2
RUN pip install pillow

# Install database

Run apt-get install -y libmariadbclient-dev zlib1g-dev  libssl-dev
RUN apt-get install -y mariadb-server

# Install main dependencies
Run apt-get install -y libffi-dev libxslt-dev libsasl2-dev libldap2-dev
Run apt-get install -y libmariadbclient-dev zlib1g-dev python-dev libssl-dev python-virtualenv
RUN apt-get install -y mysql-server
# Install other useful tools
RUN apt-get install -y git vim sudo curl unzip


# Cleaning
RUN apt-get clean
RUN apt-get purge

# ADD settings_local.py /root/settings_local.py
# ADD settings.py /root/settings.py
# ADD wsgi.py /root/wsgi.py

# Install the backend

RUN mkdir ~/badgr \
  && cd ~/badgr \
  && git clone https://github.com/daniel-izmaylov/badgr_server.git code \
  && cd code \
  && pip install -r requirements.txt


RUN cd root/badgr/code

COPY settings.py root/badgr/code/apps/mainsite/
COPY settings_local.py root/badgr/code/apps/mainsite/
COPY wsgi.py   root/badgr/code/
COPY uwsgi.ini              root/badgr/code/
RUN  pip install django-dotenv \
  && pip install uwsgi
RUN apt-get install nano
WORKDIR root/badgr/code



