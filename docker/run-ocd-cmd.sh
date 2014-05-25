#!/bin/bash

IMAGE=i-ocd-python
CONTAINER=c-ocd-cmd
HOSTPATH=$(pwd)/..
LOCALPATH=/mnt/data
LINK="--link c-redis:redis"
LINK2="--link c-es:es"
DAEMON=
#-d

sudo docker rm $CONTAINER

sudo docker run $LINK  --name $CONTAINER \
-v $HOSTPATH:$LOCALPATH:rw  \
-t -i $DAEMON $IMAGE /bin/sh -c "cd /mnt/data && ./manage.py extract start openbeelden"






