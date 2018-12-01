FROM centos:7.4.1708
MAINTAINER Pavel Kiselev "pskiselev97@gmail.com"

RUN yum -y install epel-release
RUN yum -y install https://centos7.iuscommunity.org/ius-release.rpm
RUN yum -y install python36u python36u-pip
RUN yum -y install yum-utils gcc python36u-devel postgresql-devel which openldap-devel
RUN yum -y install python-imaging
RUN yum -y install python-setuptools libsox-fmt-mp3 libsox-fmt-all mpg321 dir2ogg

RUN ln -s /bin/pip3.6 /bin/pip
RUN ln -s /usr/bin/python3.6 /usr/bin/python3
RUN pip install pipenv

ENV SRC_PROJECT_PATH /code
RUN mkdir -p $SRC_PROJECT_PATH
RUN mkdir -p /var/games/storage/media

WORKDIR $SRC_PROJECT_PATH

ADD ./src/Pipfile $SRC_PROJECT_PATH/
ADD ./src/Pipfile.lock $SRC_PROJECT_PATH/

ENV LANG=en_US.utf8
RUN pipenv install --deploy

ADD ./src $SRC_PROJECT_PATH/
ADD ./scripts /scripts/
ADD ./conf /conf/

CMD [ "uwsgi", "--module", "games.wsgi:application", "--env", "DJANGO_SETTINGS_MODULE=games.settings", "--master", "--http", ":8080", "--py-autoreload", "1"]

EXPOSE 8080