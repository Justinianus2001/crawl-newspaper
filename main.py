#!/usr/bin/env python3
# -*- coding: utf_8 -*-
import os
import pip
# pip.main(["install", "-r", "requirements.txt"])

import pandas as pd
import subprocess
from dotenv import load_dotenv
from elasticsearch import Elasticsearch, helpers
from flask import Flask, render_template, request
from flask_cors import CORS, cross_origin
from time import sleep

# Load global variable from .env file
load_dotenv()

# Init elasticsearch client
ELASTIC_PASSWORD = os.getenv("ELASTIC_PASSWORD")
CLOUD_ID = os.getenv("ELASTIC_CLOUD_ID")

# Check env elastic project
if os.getenv("ELASTIC_ENV") == "cloud":
    # Start elasticsearch and kibana server in cloud
    es = Elasticsearch(cloud_id = CLOUD_ID, basic_auth = ("elastic", ELASTIC_PASSWORD))
elif os.getenv("ELASTIC_ENV") == "local":
    # Start elasticsearch and kibana server in local
    es = Elasticsearch([{"host": "localhost", "port": 9200, "scheme": "http"}], verify_certs = True)
    batch_elasticsearch = subprocess.Popen(r"{}".format(os.getenv("BATCH_ELASTICSEARCH")),
                                           creationflags=subprocess.CREATE_NEW_CONSOLE)
    batch_kibana = subprocess.Popen(r"{}".format(os.getenv("BATCH_KIBANA")),
                                    creationflags=subprocess.CREATE_NEW_CONSOLE)
else:
    raise ValueError("ELASTIC_ENV must be either cloud or local")

# Wait for elasticsearch to be ready
while not es.ping():
    print("Elasticsearch server offline.")
    sleep(1)
    pass

# Upload data to elasticsearch
lst = pd.read_csv(os.getenv("CSV_FILE"))
lst.dropna(axis=0, inplace= True)
lst = lst.values

if es.indices.exists(index="posts"):
    es.indices.delete(index="posts")

es.indices.create(index="posts")

helpers.bulk(es, [{
    "title": lst[i][1],
    "link": lst[i][2],
    "image": lst[i][3],
    "tag": lst[i][4],
    "preview": lst[i][5],
    "author": lst[i][6],
    "timestamp": lst[i][7],
} for i in range(len(lst))], index="posts")

# Init flask backend server
app = Flask(__name__)
CORS(app)
app.config.update(
    CACHE_TYPE = "null",
    CORS_HEADERS = "Content-Type",
    SECRET_KEY = os.urandom(32),
    SESSION_COOKIE_SECURE = True,
    SESSION_COOKIE_HTTPONLY = True,
    SESSION_COOKIE_SAMESITE = "Lax",
    STATIC_FOLDER = "static",
    TEMPLATE_FOLDER = "templates"
)

@app.route("/", methods = ["GET", "POST"])
@cross_origin(origins="*")
def dashboard():
    result = es.search(index="posts", query={"match_all": {}},
                       size=os.getenv("QUERY_MAX_ROWS"))

    tags = set()
    for post in result["hits"]["hits"]:
        tags.add(post["_source"]["tag"])
    tags = list(tags)
    tags.sort()
    tags.insert(0, "ALL")
    
    tag = None
    search = None

    if request.method == "POST":
        tag = request.form.get("tag")
        search = request.form.get("search")

        # Query get posts
        if search:
            if tag == "ALL":
                result = es.search(index="posts", query={"match": {"title": search}},
                                   size=os.getenv("QUERY_MAX_ROWS"))
            else:
                result = es.search(index="posts", query={
                    "bool": {
                        "must": [
                            {"match": {"title": search}},
                            {"match": {"tag": tag}}
                        ]
                    }}, size=os.getenv("QUERY_MAX_ROWS"))
        elif tag != "ALL":
            result = es.search(index="posts", query={"match": {"tag": tag}},
                               size=os.getenv("QUERY_MAX_ROWS"))

    return render_template("./index.html", records = result["hits"]["hits"],
                           tags = tags, cur_tag = tag, cur_search = search)

if __name__ == "__main__":
    # Start backend server
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(host = "0.0.0.0", port=8080)

    # serve(app, host='0.0.0.0', port=10000)
    # cmd: waitress-serve --host 0.0.0.0 --port 10000 main:app

    if os.getenv("ELASTIC_ENV") == "local":
        batch_elasticsearch.kill()
        batch_kibana.kill()