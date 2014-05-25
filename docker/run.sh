#!/bin/bash
# prerequisites
# Test installation 

sudo docker stop c-es c-redis c-ocd-celery
sudo docker rm c-es c-redis c-ocd-celery

#Run Elastic Search as a single daemon, persistance by file mount on host
IMAGE=i-es
CONTAINER=c-es
HOSTPATH=$(pwd)/../../data/elasticsearch
LOCALPATH=/var/lib/elasticsearch
mkdir -p $HOSTPATH
sudo docker run --name $CONTAINER -v $HOSTPATH:$LOCALPATH:rw \
 -t -i -d $IMAGE

#Run Redis, inpersistant
IMAGE=i-redis
CONTAINER=c-redis
sudo docker run --name $CONTAINER -t -i -d $IMAGE

#Run Celery OCD Worker
IMAGE=i-ocd-python
CONTAINER=c-ocd-celery
HOSTPATH=$(pwd)/..
LOCALPATH=/mnt/data
LINK="--link c-redis:redis"
LINK2="--link c-es:es"
RUNCMD="/bin/sh /start-celery.sh"
sudo docker run $LINK $LINK2 --name $CONTAINER \
-v $HOSTPATH:$LOCALPATH:rw  -t -i -d $IMAGE $RUNCMD

sleep 10
# install template on Elastic Search
CONTAINER=tmp
sudo docker run $LINK $LINK2  --name $CONTAINER \
-v $HOSTPATH:$LOCALPATH:rw  \
-t -i $IMAGE /bin/sh -c "cd /mnt/data && ./manage.py elasticsearch put_template"
sudo docker rm $CONTAINER


echo
echo All Daemon containers started
echo Do stuff to run the API
echo Start harvesting data with XXX
echo sudo sh docker/run-ocd-cmd.sh
