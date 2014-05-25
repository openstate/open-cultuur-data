echo "Provisioning"
sudo apt-get update -qq
sudo apt-get install -y -qq python-software-properties
sudo add-apt-repository -y ppa:rwky/redis > /dev/null
sudo apt-get update -qq
sudo apt-get install -y -qq redis-server
sudo apt-get install -y -qq openjdk-7-jre-headless

echo "Installing Elasticsearch"
wget -q https://download.elasticsearch.org/elasticsearch/elasticsearch/elasticsearch-1.2.0.deb
sudo dpkg -i elasticsearch-1.2.0.deb > /dev/null
sudo service elasticsearch start

sudo apt-get install -y libxml2-dev libxslt1-dev python-dev python-setuptools python-virtualenv git > /dev/null
sudo easy_install -q pip
virtualenv -q ocd

source ocd/bin/activate

echo "Installing requirements"
cd /vagrant
pip install -q -r requirements.txt

echo "Starting"
./manage.py elasticsearch put_template


echo ". ocd/bin/activate"
echo "python ./manage.py frontend runserver"
echo "python ./manage.py extract list_sources"
echo "python ./manage.py extract start rijksmuseum"
echo "celery --app=ocd_backend:celery_app worker --loglevel=info --concurrency=2"
