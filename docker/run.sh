#!/bin/bash
# prerequisites
# Test installation

###Shared vars
PY_HOSTPATH=$(pwd)/..
# next: this could be changed to /data but then update start_celery.sh though
PY_LOCALPATH=/mnt/data
C_OCD_ES=c-ocd-es
C_OCD_REDIS=c-ocd-redis
C_OCD_CELERY=c-ocd-celery
C_OCD_API=c-ocd-api
RLINK="--link $C_OCD_REDIS:redis"
ELINK="--link $C_OCD_ES:es"

##### CLEAN OUT 
sudo docker rm -f $C_OCD_ES $C_OCD_REDIS $C_OCD_CELERY $C_OCD_API

##### RUN 1 ES INSTANCE
I_ES=i-es
ES_HOSTPATH=$(pwd)/../../data/elasticsearch
ES_LOCALPATH=/var/lib/elasticsearch

mkdir -p $ES_HOSTPATH
sudo docker run --name $C_OCD_ES -v $ES_HOSTPATH:$ES_LOCALPATH:rw \
 -t -i -d $I_ES
C_OCD_ES_IP=$(docker inspect $C_OCD_ES | grep IPAddress | cut -d '"' -f 4)

#####Run Redis, inpersistant
I_REDIS=i-redis

sudo docker run --name $C_OCD_REDIS -t -i -d $I_REDIS
REDISIP=$(docker inspect $C_OCD_REDIS | grep IPAddress | cut -d '"' -f 4)

#####Run Celery OCD Worker
I_OCD_PYTHON=i-ocd-python
CEL_RUNCMD="/bin/sh /start-celery.sh"

echo "CELERY_CONFIG = {\n   'BROKER_URL': 'redis://$REDISIP:6379/0', \n   'CELERY_RESULT_BACKEND': 'redis://$REDISIP:6379/0' \n}\nELASTICSEARCH_HOST = '$ESIP'\n" > $PY_HOSTPATH/ocd_backend/local_settings.py
sudo docker run $RLINK $ELINK --name $C_OCD_CELERY \
-v $PY_HOSTPATH:$PY_LOCALPATH:rw -t -i -d $I_OCD_PYTHON $CEL_RUNCMD

##### PUT TEMPLATE IN ES
###sleep 30
#implement ES ready monitor
# docker logs c-ocd-es watch "started"
sudo docker run $RLINK $ELINK -v $PY_HOSTPATH:$PY_LOCALPATH:rw  \
-t -i $I_OCD_PYTHON /bin/sh -c "cd /mnt/data && ./manage.py elasticsearch put_template"
###sudo docker rm $TMP

##### INSERT API STUFF
I_OCD_API=i-ocd-api

echo "ELASTICSEARCH_HOST = '$ESIP' \n " > $PY_HOSTPATH/ocd_frontend/local_settings.py
docker run $EXPOSE $ELINK -v $PY_HOSTPATH:$PY_LOCALPATH  --name $C_OCD_API -t -i -d $DAEMON $I_OCD_API
APIIP=$(docker inspect $C_OCD_API | grep IPAddress | cut -d '"' -f 4)


##### Time to demo
sleep 5
curl -XPOST http://$APIIP/v0/search  -d '{"query": "fiets"}'

echo
echo All Daemon containers started
echo sudo sh docker/run-ocd-cmd.sh
echo to expose your API, expose it to port 80 or use a reverse proxy
echo "It's now available at $APIIP ."
echo 
