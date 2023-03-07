import os
import pandas as pd
import subprocess
from elasticsearch import Elasticsearch, helpers

class ElasticSearchEngine:
    def __init__(self):
        # Check env elastic (cloud or local)
        if os.getenv("ELASTIC_ENV") == "cloud":
            # Start elasticsearch in cloud
            self.es = Elasticsearch(cloud_id=os.getenv("ELASTIC_CLOUD_ID"),
                            basic_auth=("elastic", os.getenv("ELASTIC_PASSWORD")))
        elif os.getenv("ELASTIC_ENV") == "local":
            # Start elasticsearch in local
            self.es = Elasticsearch([{"host": "localhost", "port": 9200, "scheme": "http"}], verify_certs=True)
            self.batch_elasticsearch = subprocess.Popen(r"{}".format(os.getenv("BATCH_ELASTICSEARCH")),
                                                        creationflags=subprocess.CREATE_NEW_CONSOLE)
            self.batch_kibana = subprocess.Popen(r"{}".format(os.getenv("BATCH_KIBANA")),
                                                 creationflags=subprocess.CREATE_NEW_CONSOLE)
        else:
            raise ValueError("ELASTIC_ENV must be either `cloud` or `local`")

        # Wait until elasticsearch server is online
        while not self.es.ping():
            print("Elasticsearch server offline.")

    def run(self):
        # Upload data to elasticsearch
        lst = pd.read_csv(os.getenv("CSV_FILE"))
        lst.dropna(axis=0, inplace=True)
        lst = lst.values

        if self.es.indices.exists(index="posts"):
            self.es.indices.delete(index="posts")

        self.es.indices.create(index="posts")

        # self.es.indices.create(index="posts", settings={
        #     "index": {
        #         "similarity": {
        #             "my_similarity": {
        #                 "type": "DFR",
        #                 "basic_model": "g",
        #                 "after_effect": "l",
        #                 "normalization": "h2",
        #                 "normalization.h2.c": "3.0"
        #             }
        #         }
        #     }
        # }, mappings={
        #     "properties": {
        #         "title": {
        #             "type": "text",
        #             "similarity": "my_similarity"
        #         },
        #     }
        # })

        helpers.bulk(self.es, [{
            "title": lst[i][1],
            "link": lst[i][2],
            "image": lst[i][3],
            "tag": lst[i][4],
            "preview": lst[i][5],
            "author": lst[i][6],
            "timestamp": lst[i][7],
        } for i in range(len(lst))], index="posts")

    def __del__(self):
        # If running in local, kill batch processes before exit
        if os.getenv("ELASTIC_ENV") == "local":
            self.batch_elasticsearch.kill()
            self.batch_kibana.kill()