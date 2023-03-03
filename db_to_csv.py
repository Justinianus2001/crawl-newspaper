import csv
import os
import sqlite3
from dotenv import load_dotenv

# Load global variable from .env file
load_dotenv()

# Connect to the SQLite database
conn = sqlite3.connect(os.getenv("DB_FILE"))

# Retrieve data from the database
c = conn.cursor()
c.execute('SELECT * FROM `posts`')
data = c.fetchall()

# Write the data to a CSV file
with open(os.getenv("CSV_FILE"), 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['id', 'title', 'link', 'image', 'tag', 'preview', 'author', 'timestamp'])
    writer.writerows(data)