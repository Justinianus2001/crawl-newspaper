#!/usr/bin/env python3
# -*- coding: utf_8 -*-
import os
import pip
pip.main(["install", "-r", "setup.txt"])

import sqlite3
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.support.ui import Select
from time import sleep
from webdriver_manager.microsoft import EdgeChromiumDriverManager

# Load global variable from .env file
load_dotenv()

# Declear browser use
browser = webdriver.Edge(service = EdgeService(EdgeChromiumDriverManager().install()))
browser.maximize_window()

# Connect to database
connect = sqlite3.connect(os.getenv("DB_FILE"), check_same_thread = False)
cur = connect.cursor()

# Create table if not exist
cur.execute("CREATE TABLE IF NOT EXISTS posts (title TEXT, link TEXT UNIQUE, image TEXT)")

def pause():
    sleep(int(os.getenv("TIME_SLEEP")))

if __name__ == "__main__":
    # Open site in browser
    browser.get(os.getenv("WEBSITE"))
    pause()

    # Value | Type
    # all     All
    # 1       Day
    # 2       Week
    # 3       Month
    # 4       Year
    time_select = Select(browser.find_element(By.CLASS_NAME, "filter-select-big"))
    time_select.select_by_value("2")
    pause()

    while True:
        posts = browser.find_elements(By.CLASS_NAME, "feature-box__image")
        for post in posts:
            img_tag = post.find_element(By.CLASS_NAME, "lazy")
            a_tag = post.find_element(By.TAG_NAME, "a")

            image = img_tag.get_attribute("data-src")
            link = a_tag.get_attribute("href")
            title = a_tag.get_attribute("title")

            cur.execute(f"INSERT OR IGNORE INTO `posts` (title, link, image) VALUES (?, ?, ?)", (title, link, image))
            connect.commit()
        
        next_page = browser.find_elements(By.CLASS_NAME, "panination__content-item")[-1]
        if "active" in next_page.get_attribute("class").split():
            break
        else:
            next_page.click()
            pause()
    
    pause()
    browser.close()
    connect.close()