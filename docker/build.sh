#!/bin/bash
# prerequisites
# docker.io
# git

#Build Elastic Search
IMAGE=i-es
sudo docker build -t $IMAGE github.com/ajslaghu/docker-elasticsearch

#Build Redis
IMAGE=i-redis
sudo docker build -t $IMAGE github.com/dockerfile/redis

#Build OCD Python, for celery (transformers) and cmd (extractors)
IMAGE=i-ocd-python
sudo docker build -t $IMAGE ocd-python/.

#Build Nginx / Python webApp for the API
IMAGE=i-ocd-api
sudo docker build -t $IMAGE ocd-api/.

echo
echo Installation finished
echo To Do stuff to run the API
echo Start the stack with
echo "sh run.sh"
echo and continue with Loading data with:
echo 'sh run-ocd-cmd.sh' 