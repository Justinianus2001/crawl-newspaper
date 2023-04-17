[![pipeline status](https://gitlab.com/Justinianus2001/crawl-newspaper/badges/master/pipeline.svg)](https://gitlab.com/Justinianus2001/crawl-newspaper/-/commits/master)
[![coverage report](https://gitlab.com/Justinianus2001/crawl-newspaper/badges/master/coverage.svg)](https://gitlab.com/Justinianus2001/crawl-newspaper/-/commits/master)
[![Latest Release](https://gitlab.com/Justinianus2001/crawl-newspaper/-/badges/release.svg)](https://gitlab.com/Justinianus2001/crawl-newspaper/-/releases)
# Vietnamese News Scraper
This is a Python web scraping project that can be used to gather news articles from Vietnamese news websites such as https://vietnamnet.vn and https://zingnews.vn. With this program, you can scrape the content of news articles, including the title, link, image, tag, preview, author, and timestamp, and store them in an Elasticsearch database.
## Requirements
To use this program, you will need:
- Python 3 installed on your computer
- An Elasticsearch Cloud account or a local Elasticsearch setup
## Installation
To get started with the project, follow these steps:
1. Clone the repository onto your local machine with:
```
git clone https://github.com/Justinianus2001/crawl-newspaper.git
```
2. Install the required Python packages using pip:
```
pip install -r requirements.txt
```
3. Create a `.env` file in the root directory of the project with the following global environment variables:
```
BATCH_ELASTICSEARCH=your-local-elasticsearch-batch-file
BATCH_KIBANA=your-local-kibana-batch-file
BATCH_SIZE=128
DB_FILE=./data/database.db
CSV_FILE=./data/database.csv
ELASTIC_CLOUD_ID=your-elastic-cloud-id
ELASTIC_ENV=cloud
ELASTIC_INDEX=posts
ELASTIC_PASSWORD=your-elastic-cloud-password
ENV=cloud
PORT=5000
QUERY_MAX_ROWS=2000
QUERY_PAGINATION=30
SEARCH_THRESHOLD=0.4
TIME_SLEEP=2
WEBSITE=https://zingnews.vn/a-tim-kiem.html
```
**Note:** For the `ENV` variable in `.env`, we recommend setting this to `local` on the first run, which will push the database of this project into the Elasticsearch storage. So in subsequent runs, we don't need to push it again and can set `ENV=cloud` to improve the processing time. (This is important if you need to deploy this app to a cloud platform like Azure.)
## Usage
After completing the installation step, you can run the `app.py` file in the root directory with the command:
```
python app.py
```
This will launch the Flask application and allow you to search for keywords and scrape news articles from the configured websites.
## Python Files
This repository contains three main Python files:
### app.py
This Python Flask page application serves as the main file for the project. Running this file launches the Flask application that allows you to search for news articles and store them in an Elasticsearch database.
### crawl.py
`crawl.py` is a tool that uses Selenium to scrape news articles from the configured websites. This file contains the scrapers for both websites, `vietnamnet.vn` and `zingnews.vn`. It extracts the title, link, image, tag, preview, author, and timestamp of each article and stores them in a database.
### db_to_csv.py
`db_to_csv.py` is a tool that converts the `.db` SQLite database into a `.csv` file. This can be useful if you need to export the data to another platform or service.
## Website Demo
***Update:*** Unfortunately, my Elasticsearch trial has expired, which means that my website demo is currently unavailable. I apologize for any inconvenience this may cause.

You can view a demo of the website with scraped articles at the following links:
- Render: https://crawl-newspaper.onrender.com (Commit version #5)
- Azure: https://crawl-newspaper.azurewebsites.net (Latest commit)

Please note that these links may not always be available and may not reflect the latest version of the code.
## Contributing
If you find any bugs or would like to contribute to the project, please feel free to submit a pull request or issue in the GitHub repository.
## License
This program is licensed under the MIT License. You are free to use, modify, and distribute this program for any purpose, as long as you include the original copyright and license notice in any copy of the software.