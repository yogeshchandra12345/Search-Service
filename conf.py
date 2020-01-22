import os
from elasticsearch import Elasticsearch


class BaseConf(object):

    # ElasticSearch configurations
    ES_HOST = os.environ.get("ES_HOST", "localhost")
    ES_PORT = os.environ.get("ES_PORT", 9200)
    
    @staticmethod
    def get_es_url(indices):
        return "http://{es_host}:{es_port}/{indices}/_search". \
            format(es_host=str(BaseConf.ES_HOST), es_port=str(BaseConf.ES_PORT), indices=str(indices))

    @classmethod
    def get_es_conn(cls):
        return Elasticsearch("{}:{}".format(BaseConf.ES_HOST, BaseConf.ES_PORT))
