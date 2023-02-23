#!/usr/bin/env python3
# -*- coding: utf_8 -*-
import os
import pip
# pip.main(["install", "-r", "requirements.txt"])

import sqlite3
# import tensorflow as tf
from dotenv import load_dotenv
from flask import Flask, render_template, request
from flask_cors import CORS, cross_origin
from waitress import serve

# Load global variable from .env file
load_dotenv()

# Load keras model
# sess = tf.Session()
# graph = tf.get_default_graph()

# Use this when load or use model
# with sess.as_default():
#     with graph.as_default():
        # Load model here
        # pass

SECRET_KEY = os.urandom(32)

# Init flask backend server
app = Flask(__name__)
CORS(app)
app.config.update(
    CACHE_TYPE = "null",
    CORS_HEADERS = "Content-Type",
    SECRET_KEY = SECRET_KEY,
    SESSION_COOKIE_SECURE = True,
    SESSION_COOKIE_HTTPONLY = True,
    SESSION_COOKIE_SAMESITE = "Lax",
    STATIC_FOLDER = "static",
    TEMPLATE_FOLDER = "templates"
)

# Connect to database
connect = sqlite3.connect(os.getenv("DB_FILE"), check_same_thread = False)
cur = connect.cursor()

# GET request example
# @app.route("/get", methods = ["GET"])
# @cross_origin(origins="*")
# def get_get():
#     a = int(request.args.get("a"))
#     b = int(request.args.get("b"))
#     return "Answer is " + str(a + b) + "."

# POST request example
# @app.route("/post", methods = ["POST"])
# @cross_origin(origins="*")
# def post_post():
#     a = int(request.form.get("c"))
#     b = int(request.form.get("d"))
#     return "Answer is " + str(a + b) + "."

@app.route("/", methods = ["GET", "POST"])
@cross_origin(origins="*")
def dashboard():
    if request.method == "POST":
        tag = request.form.get("tag")
        search = request.form.get("search")

        # Query get posts
        if tag == "ALL":
            result = cur.execute(fr"SELECT * FROM `posts` WHERE `title` LIKE (?) LIMIT 30", ("%" + search + "%",))
        else:
            result = cur.execute(fr"SELECT * FROM `posts` WHERE `title` LIKE (?) AND `tag` = (?) LIMIT 30", 
                    ("%" + search + "%", tag,))
        result = result.fetchall()
    else:
        tag = None
        search = None
        result = []

    # Query get list tags
    tags = cur.execute("SELECT DISTINCT `tag` FROM `posts` ORDER BY `tag` ASC").fetchall()
    tags = [row[0] for row in tags]
    tags.insert(0, "ALL")

    return render_template("./index.html", records = result, tags = tags, cur_tag = tag, cur_search = search)

if __name__ == "__main__":
    # Start backend server
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(host = "0.0.0.0", port=8080)
    # serve(app, host='0.0.0.0', port=10000)
    # cmd: waitress-serve --host 0.0.0.0 --port 10000 main:app
    connect.close()