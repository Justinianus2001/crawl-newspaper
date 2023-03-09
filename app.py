#!/usr/bin/env python3
# -*- coding: utf_8 -*-
import os
import pip

# Install packages
# pip.main(["install", "-r", "requirements.txt"])

import locale
from dotenv import load_dotenv
from flask import Flask, render_template, request
from flask_cors import CORS, cross_origin
from pyvi.ViTokenizer import tokenize

from src.elastic_search_engine import ElasticSearchEngine

def setup():
    # Load global variable from .env file
    load_dotenv()

    # Set threads for numexpr
    os.environ["NUMEXPR_NUM_THREADS"] = "8"
    os.environ["NUMEXPR_MAX_THREADS"] = "8"

    # Set locale for sorting Vietnamese characters (Windows only)
    if os.name == "nt":
        # Windows
        locale.setlocale(locale.LC_COLLATE, "vi_VN")

setup()

# Start flask server
app = Flask(__name__, template_folder="./src/templates", static_folder="./src/static")
CORS(app)
app.config.update(
    CACHE_TYPE = "null",
    CORS_HEADERS = "Content-Type",
    SECRET_KEY = os.urandom(32),
    SESSION_COOKIE_SECURE = True,
    SESSION_COOKIE_HTTPONLY = True,
    SESSION_COOKIE_SAMESITE = "Lax",
    TEMPLATE_AUTO_RELOAD = True
)

# Start elasticsearch server
elastic = ElasticSearchEngine()

if os.getenv("ENV") == "local":
    elastic.run()

@app.route("/", methods = ["GET", "POST"])
@cross_origin(origins="*")
def dashboard():
    result = elastic.es.search(index="posts", query={
        "match_all": {}
    }, size=os.getenv("QUERY_MAX_ROWS"))

    tags = list({post["_source"]["tag"] for post in result["hits"]["hits"]})
    tags.sort(key=locale.strxfrm)
    tags.insert(0, "ALL")

    tag = None
    search = None

    if request.method == "POST":
        tag = request.form.get("tag")
        search = request.form.get("search")

        if search:
            result = elastic.es.search(index="posts", query={
                "match": {
                    "title": search
                }
            }, size=os.getenv("QUERY_MAX_ROWS"))

            query_vector = embed_text_query([tokenize(search)])[0]
            result = elastic.es.search(index="posts", query={
                "script_score": {
                    "query": {
                        "match_all": {}
                    },
                    "script": {
                        "source": "cosineSimilarity(params.query_vector, 'title_vector') + 1.0",
                        "params": {"query_vector": query_vector}
                    }
                }
            }, size=os.getenv("QUERY_MAX_ROWS"))

        if tag != "ALL":
            # Delete all posts that don't match the tag from the result list
            # in reverse order to avoid index out of range error
            for i in range(len(result["hits"]["hits"]) - 1, -1, -1):
                if result["hits"]["hits"][i]["_source"]["tag"] != tag:
                    del result["hits"]["hits"][i]

    return render_template("./index.html",
                            records=result["hits"]["hits"][:int(os.getenv("QUERY_PAGINATION"))],
                            tags=tags, cur_tag=tag, cur_search=search)

def embed_text_query(text):
    text_embedding = elastic.model_embedding.encode(text)
    return text_embedding.tolist()

if __name__ == "__main__":
    # Start backend server
    app.jinja_env.auto_reload = True
    app.run(host = "0.0.0.0", port=8080)

    del app
    del elastic