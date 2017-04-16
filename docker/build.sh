#!/bin/bash
# prerequisites
# docker.io
# git

I_ES=i-es
I_REDIS=i-redis
I_OCD_PYTHON=i-ocd-python
I_OCD_API=i-ocd-api


#Build Elastic Search
sudo docker build -t $I_ES github.com/ajslaghu/docker-elasticsearch

#Build Redis
sudo docker build -t $I_REDIS github.com/dockerfile/redis

#Build OCD Python, for celery (transformers) and cmd (extractors)
sudo docker build -t $I_OCD_PYTHON ocd-python/.

#Build Nginx / Python webApp for the API
sudo docker build -t $I_OCD_API ocd-api/.

echo
echo Installation finished
echo To Do stuff to run the API
echo Start the stack with
echo "sh run.sh"
echo and continue with Loading data with:
echo 'sh run-ocd-cmd.sh'
