#!/usr/bin/env python3
# -*- coding: utf_8 -*-
import os
import pip
# pip.main(["install", "-r", "requirements.txt"])

import sqlite3
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service
from selenium.webdriver.support.ui import Select
from time import sleep
from webdriver_manager.microsoft import EdgeChromiumDriverManager

# Load global variable from .env file
load_dotenv()

# Declear browser use
edge_options = Options()
edge_options.use_chromium = True
# edge_options.add_argument("headless")
# edge_options.add_argument("disable-gpu")
# edge_options.add_argument("disable-extensions")
# edge_options.add_argument("disable-dev-shm-usage")
# edge_options.add_argument("no-sandbox")
# edge_options.add_argument("log-level=3")
# edge_options.add_argument("silent")
# edge_options.add_argument("disable-logging")
# edge_options.add_argument("disable-infobars")
# edge_options.add_argument("window-size=1920,1080")

browser = webdriver.Edge(service = Service(EdgeChromiumDriverManager().install()), options=edge_options)
browser.maximize_window()

# Connect to database
connect = sqlite3.connect(os.getenv("DB_FILE"), check_same_thread = False)
cur = connect.cursor()

# Function to pause script for a while (in second)
def pause():
    sleep(int(os.getenv("TIME_SLEEP")))

if __name__ == "__main__":
    # Create table if not exist
    cur.execute('''CREATE TABLE IF NOT EXISTS posts 
        (id INTEGER PRIMARY KEY, title TEXT, link TEXT UNIQUE, image TEXT, 
        tag TEXT, preview TEXT, author TEXT, timestamp TEXT)''')
    
    # Open site in browser
    browser.get(os.getenv("WEBSITE"))
    pause()

    if os.getenv("WEBSITE") == "https://vietnamnet.vn/tim-kiem":
        # Select time range to crawl
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
            posts = browser.find_elements(By.CLASS_NAME, "feature-box")
            for post in posts:
                # Get post data
                img_tag = post.find_element(By.CLASS_NAME, "lazy")
                post_tag = post.find_element(By.TAG_NAME, "a")
                div_tag = post.find_element(By.CLASS_NAME, "feature-box__content--desc")
                a_tag = post.find_element(By.CLASS_NAME, "feature-box__content--brand").find_element(By.TAG_NAME, "a")

                title = post_tag.get_attribute("title")
                link = post_tag.get_attribute("href")
                image = img_tag.get_attribute("data-src")
                tag = a_tag.text
                preview = div_tag.text

                # Open post in new tab
                browser.execute_script(f"window.open('{link}');")
                browser.switch_to.window(browser.window_handles[-1])
                pause()

                # Get post timestamp and author
                try:
                    timestamp = browser.find_element(By.CLASS_NAME, "breadcrumb-box__time").find_element(By.TAG_NAME, "span").text
                except:
                    try:
                        timestamp = browser.find_element(By.CLASS_NAME, "bread-crumb__detail-time").find_element(By.TAG_NAME, "p").text
                    except:
                        timestamp = "Unknown"

                try:
                    author = browser.find_element(By.CLASS_NAME, "newsFeature__author-info").find_element(By.TAG_NAME, "a").text
                except:
                    author = "Anonymous"

                # Close post tab
                browser.close()
                browser.switch_to.window(browser.window_handles[0])

                cur.execute(fr'''INSERT OR IGNORE INTO `posts` (title, link, image, tag, preview, author, timestamp) 
                    VALUES (?, ?, ?, ?, ?, ?, ?)''', (title, link, image, tag, preview, author, timestamp))
                connect.commit()

            # Go to next page if exist
            next_page = browser.find_elements(By.CLASS_NAME, "panination__content-item")[-1]
            if "active" in next_page.get_attribute("class").split():
                break
            else:
                next_page.click()
                pause()
    elif os.getenv("WEBSITE") == "https://zingnews.vn/a-tim-kiem.html?date=30daysago":
        # Get scroll height
        last_height = browser.execute_script("return document.body.scrollHeight")

        while False:
            # Scroll down to bottom
            browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # Wait to load page
            pause()

            # Calculate new scroll height and compare with last scroll height
            new_height = browser.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
        
        posts = browser.find_elements(By.CLASS_NAME, "article-item")
        for post in posts:
            img_tag = post.find_element(By.CLASS_NAME, "article-thumbnail")
            post_tag = post.find_element(By.TAG_NAME, "header")

            title = post_tag.find_element(By.CLASS_NAME, "article-title").find_element(By.TAG_NAME, "a").text
            link = img_tag.find_element(By.TAG_NAME, "a").get_attribute("href")
            image = img_tag.find_element(By.TAG_NAME, "img").get_attribute("src")
            preview = post_tag.find_element(By.CLASS_NAME, "article-summary").text

            # Open post in new tab
            browser.execute_script(f"window.open('{link}');")
            browser.switch_to.window(browser.window_handles[-1])
            pause()

            # Get post info
            link = browser.current_url
            tag = browser.find_element(By.CLASS_NAME, "parent_cate").text
            author = browser.find_element(By.CLASS_NAME, "the-article-author").text
            timestamp = browser.find_element(By.CLASS_NAME, "the-article-publish").text

            timestamp = timestamp[timestamp.find(",") + 2:]

            # Close post tab
            browser.close()
            browser.switch_to.window(browser.window_handles[0])

            cur.execute(fr'''INSERT OR IGNORE INTO `posts` (title, link, image, tag, preview, author, timestamp) 
                VALUES (?, ?, ?, ?, ?, ?, ?)''', (title, link, image, tag, preview, author, timestamp))
            connect.commit()
    
    pause()
    browser.close()
    connect.close()