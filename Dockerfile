FROM ubuntu:14.04
MAINTAINER Open State Foundation <developers@openstate.eu>

# Use bash as default shell
RUN rm /bin/sh && ln -s /bin/bash /bin/sh

# Add multiverse to sources
RUN echo 'deb http://archive.ubuntu.com/ubuntu/ trusty multiverse' >> etc/apt/sources.list

# Set Dutch locale, needed to parse Dutch time data
RUN locale-gen nl_NL.UTF-8

#Set Timezone
RUN echo "Europe/Amsterdam" > /etc/timezone \
    && dpkg-reconfigure -f noninteractive tzdata

RUN apt-get update \
    && apt-get install -y \
        python-dev \
        python-setuptools \
        python-software-properties \
        openjdk-7-jre-headless \
        wget \
        curl \
        poppler-utils \
        software-properties-common \
        gettext \
        git \
        dnsutils \
        vim

RUN add-apt-repository ppa:mc3man/trusty-media \
    && apt-get update \
    && apt-get dist-upgrade -y

# according to http://www.monblocnotes.com/node/2057
RUN sed -i 's/exit 101/exit 0/' /usr/sbin/policy-rc.d

RUN apt-get install -y redis-server
RUN service redis-server start

# Install elasticsearch
ENV ES_VERSION 1.4.2
RUN wget https://download.elasticsearch.org/elasticsearch/elasticsearch/elasticsearch-${ES_VERSION}.deb
RUN dpkg -i elasticsearch-${ES_VERSION}.deb > /dev/null
RUN service elasticsearch start
RUN rm elasticsearch-${ES_VERSION}.deb

# Install elasticsearch head plugin
RUN /usr/share/elasticsearch/bin/plugin --install mobz/elasticsearch-head

RUN apt-get install -y \
        make \
        libxml2-dev \
        libxslt1-dev \
        libssl-dev \
        libffi-dev \
        libtiff4-dev \
        libjpeg8-dev \
        liblcms2-dev \
        python-dev \
        python-setuptools \
        python-virtualenv \
        git \
        supervisor \
        vim

RUN easy_install pip

##### Install dependencies for pyav #####
RUN apt-get update \
    && apt-get install -y \
        libfaac-dev \
        libgpac-dev \
        checkinstall \
        libmp3lame-dev \
        libopencore-amrnb-dev \
        libopencore-amrwb-dev \
        librtmp-dev \
        libtheora-dev \
        libvorbis-dev \
        libx264-dev \
        libfdk-aac-dev \
        libvpx-dev \
        libxvidcore-dev \
        pkg-config \
        yasm \
        zlib1g-dev \
        libavformat-dev \
        libavcodec-dev \
        libavdevice-dev \
        libavutil-dev \
        libswscale-dev \
        libavresample-dev
# Temporarily use /tmp as workdir for the pyav dependencies
# WORKDIR /tmp

RUN apt-get install -y ffmpeg
##########

WORKDIR /opt/ocd
# Create a virtualenv project
RUN echo 'ok'
RUN virtualenv -q /opt
RUN source ../bin/activate \
    && pip install pip --upgrade
RUN echo "source /opt/bin/activate; cd /opt/ocd;" >> ~/.bashrc

# Temporarily add files on the host to the container
# as it contains files needed to finish the base installation
ADD . /opt/ocd

# Install Python requirements
# Install Python requirements
RUN source ../bin/activate \
    && pip install pycparser==2.13 \
    && pip install Cython==0.21.2 \
    && pip install -r requirements.txt

# Initialize
RUN source ../bin/activate \
    && service elasticsearch start \
    && sleep 20 \
    && ./manage.py elasticsearch create_indexes es_mappings/ \
    && ./manage.py elasticsearch put_template

RUN apt-get install -y supervisor

# Generate documentation
RUN source ../bin/activate && cd docs && make html

# Delete all files again
RUN find . -delete

# When the container is created or started run start.sh which starts
# all required services and supervisor which starts celery and celerycam
CMD /opt/ocd/start.sh
