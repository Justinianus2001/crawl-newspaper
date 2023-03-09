import os
import pandas as pd
import subprocess
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from pyvi.ViTokenizer import tokenize
from sentence_transformers import SentenceTransformer

class ElasticSearchEngine:
    def __init__(self):
        self.model_embedding = SentenceTransformer("VoVanPhuc/sup-SimCSE-VietNamese-phobert-base")

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
        self.es.indices.delete(index="posts", ignore=[404])

        self.es.indices.create(index="posts", mappings={
            "dynamic": "true",
            "_source": {
                "enabled": "true"
            },
            "properties": {
                "id": {
                    "type": "text"
                },
                "title": {
                    "type": "text"
                },
                "title_vector": {
                    "type": "dense_vector",
                    "dims": 768
                }
            }
        })

        self.indexed_data()

        # Refresh index to make changes available for search
        self.es.indices.refresh(index="posts")

    def indexed_data(self):
        # Upload data to elasticsearch
        lst = pd.read_csv(os.getenv("CSV_FILE"))
        lst.dropna(axis=0, inplace=True)
        lst = lst.values

        for i in range(0, len(lst), int(os.getenv("BATCH_SIZE"))):
            docs = lst[i:i+int(os.getenv("BATCH_SIZE"))]

            # Embedding title
            titles = [tokenize(doc[1]) for doc in docs]
            titles_vector = self.embed_text_title(titles)

            bulk(self.es, [{
                "title": docs[i][1],
                "link": docs[i][2],
                "image": docs[i][3],
                "tag": docs[i][4],
                "preview": docs[i][5],
                "author": docs[i][6],
                "timestamp": docs[i][7],
                "title_vector": titles_vector[i]
            } for i in range(len(docs))], index="posts")

    def embed_text_title(self, batch_text):
        batch_embedding = self.model_embedding.encode(batch_text)
        return [vector.tolist() for vector in batch_embedding]

    def __del__(self):
        # If running in local, kill batch processes before exit
        if os.getenv("ELASTIC_ENV") == "local":
            self.batch_elasticsearch.kill()
            self.batch_kibana.kill()