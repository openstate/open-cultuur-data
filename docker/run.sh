#!/bin/bash
# prerequisites
# Test installation 

sudo docker rm -f c-es c-redis c-ocd-celery c-ocd-api

#Run Elastic Search as a single daemon, persistance by file mount on host
IMAGE=i-es
CONTAINER=c-es
HOSTPATH=$(pwd)/../../data/elasticsearch
LOCALPATH=/var/lib/elasticsearch
mkdir -p $HOSTPATH
sudo docker run --name $CONTAINER -v $HOSTPATH:$LOCALPATH:rw \
 -t -i -d $IMAGE
ESIP=$(docker inspect $CONTAINER | grep IPAddress | cut -d '"' -f 4)

#Run Redis, inpersistant
IMAGE=i-redis
CONTAINER=c-redis
sudo docker run --name $CONTAINER -t -i -d $IMAGE
REDISIP=$(docker inspect $CONTAINER | grep IPAddress | cut -d '"' -f 4)

#Run Celery OCD Worker
IMAGE=i-ocd-python
CONTAINER=c-ocd-celery
HOSTPATH=$(pwd)/..
LOCALPATH=/mnt/data
LINK="--link c-redis:redis"
LINK2="--link c-es:es"
RUNCMD="/bin/sh /start-celery.sh"

STR="CELERY_CONFIG = {\n   'BROKER_URL': 'redis://$REDISIP:6379/0', \n   'CELERY_RESULT_BACKEND': 'redis://$REDISIP:6379/0' \n}\nELASTICSEARCH_HOST = '$ESIP'\n"
#ELASTICSEARCH_PORT = 9200 \n "
echo $STR > $HOSTPATH/ocd_backend/local_settings.py

sudo docker run $LINK $LINK2 --name $CONTAINER \
-v $HOSTPATH:$LOCALPATH:rw  -t -i -d $IMAGE $RUNCMD

sleep 30
#implement ES ready monitor
#curl es:9200/somthin and parse it
#error: "Read-only file system" setting key "vm.max_map_count"
# "started"
# install template on Elastic Search
CONTAINER=tmp
sudo docker run $LINK $LINK2  --name $CONTAINER \
-v $HOSTPATH:$LOCALPATH:rw  \
-t -i $IMAGE /bin/sh -c "cd /mnt/data && ./manage.py elasticsearch put_template"
sudo docker rm $CONTAINER

# INSERT API STUFF
ES=c-es
IMAGE=i-ocd-api
CONTAINER=c-ocd-api
HOSTPATH=$(pwd)/..
LOCALPATH=/mnt/data
LINK2="--link c-es:es"
EXPOSE="-p 80:80"
DAEMON=-d

echo $ESIP
# Script that updates local_settings.py in the ocd_frontend directory
echo "ELASTICSEARCH_HOST = '$ESIP' \n " > $HOSTPATH/ocd_frontend/local_settings.py
docker run $EXPOSE $LINK2 -v $HOSTPATH:$LOCALPATH  --name $CONTAINER -t -i $DAEMON $IMAGE
APIIP=$(docker inspect $CONTAINER | grep IPAddress | cut -d '"' -f 4)
echo $APIIP
sleep 5
curl -XPOST http://$APIIP/v0/search  -d '{"query": "fiets"}'
curl -XPOST http://localhost/v0/search  -d '{"query": "fiets"}'




echo
echo All Daemon containers started
echo Do stuff to run the API
echo Start harvesting data with XXX
echo sudo sh docker/run-ocd-cmd.sh
