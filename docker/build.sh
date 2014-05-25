#!/bin/bash
# prerequisites
# docker.io
# git

#Build Elastic Search
IMAGE=i-es
#sudo docker build -t $IMAGE github.com/orchardup/docker-elasticsearch
sudo docker build -t $IMAGE github.com/ajslaghu/docker-elasticsearch
#https://github.com/ajslaghu/docker-elasticsearch.git

#Build Redis
IMAGE=i-redis
sudo docker build -t=$IMAGE github.com/dockerfile/redis

#Build OCD Python, for celery (transformers) and cmd (extractors)
IMAGE=i-ocd-python
sudo sudo docker build -t $IMAGE ocd-python/.

echo
echo Installation finished
echo To Do stuff to run the API
echo Start the stack with
echo "sh run.sh"
echo and continue with loading by
echo 'sh run-ocd-cmd.sh' 