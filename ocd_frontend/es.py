from elasticsearch import Elasticsearch

class ElasticsearchService(object):
    def __init__(self, host, port):
        self.es = Elasticsearch([{'host': host, 'port': port}])

    def search(self, *args, **kwargs):
        return self.es.search(*args, **kwargs)

    def get(self, *args, **kwargs):
        return self.es.get(*args, **kwargs)
