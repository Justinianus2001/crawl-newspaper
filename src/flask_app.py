import locale
import os
from flask import Flask, render_template, request
from flask_cors import CORS, cross_origin

class FlaskApp:
    def __init__(self, elasticsearch):
        # Init elasticsearch
        self.elastic = elasticsearch

        # Init flask backend server
        self.app = Flask(__name__)
        CORS(self.app)
        self.app.config.update(
            CACHE_TYPE = "null",
            CORS_HEADERS = "Content-Type",
            SECRET_KEY = os.urandom(32),
            SESSION_COOKIE_SECURE = True,
            SESSION_COOKIE_HTTPONLY = True,
            SESSION_COOKIE_SAMESITE = "Lax",
            STATIC_FOLDER = "static",
            TEMPLATE_FOLDER = "templates"
        )

        # Add routes
        self.app.add_url_rule('/', view_func=self.dashboard, methods=['GET', 'POST'])

    @cross_origin(origins="*")
    def dashboard(self):
        result = self.elastic.es.search(index="posts", query={
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
                result = self.elastic.es.search(index="posts", query={
                    "match": {
                        "title": search
                    }
                }, size=os.getenv("QUERY_MAX_ROWS"))

                # result = self.elastic.es.search(index="posts", query={
                #     "more_like_this": {
                #         "fields": ["title"],
                #         "like": search,
                #         "min_term_freq": 1,
                #         "min_doc_freq": 1
                #     }
                # }, size=os.getenv("QUERY_MAX_ROWS"))

            if tag != "ALL":
                # Delete all posts that don't match the tag from the result list
                # in reverse order to avoid index out of range error
                for i in range(len(result["hits"]["hits"]) - 1, -1, -1):
                    if result["hits"]["hits"][i]["_source"]["tag"] != tag:
                        del result["hits"]["hits"][i]

        return render_template("./index.html",
                                records=result["hits"]["hits"][:int(os.getenv("QUERY_PAGINATION"))],
                                tags=tags, cur_tag=tag, cur_search=search)

    def run(self):
        # Start backend server
        self.app.jinja_env.auto_reload = True
        self.app.config['TEMPLATES_AUTO_RELOAD'] = True
        self.app.run(host = "0.0.0.0", port=8080)