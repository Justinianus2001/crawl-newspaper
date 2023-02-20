#!/usr/bin/env python3
# -*- coding: utf_8 -*-
import os
import pip
pip.main(["install", "-r", "setup.txt"])

import sqlite3
# import tensorflow as tf
from dotenv import load_dotenv
from flask import Flask, render_template, request
from flask_cors import CORS, cross_origin

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
        search = request.form.get("search")
        cur.execute(f"SELECT * FROM `posts` WHERE `title` LIKE ?", ("%" + search + "%",))
        result = cur.fetchall()
    else:
        result = []
    return render_template("./index.html", records = result)

if __name__ == "__main__":
    # Start backend server
    app.run(host = "0.0.0.0", port = "2306", debug = True)
    connect.close()