# Getting Started

This repository used to crawl and search for newspaper info (title, link, image, tag, preview, author, timestamp) from website https://vietnamnet.vn, https://zingnews.vn use flask, selenium and elasticsearch library in python 3.

**Note:** Before use this project, you need an elasticsearch cloud account, or have local setup instead. To switch mode, there are two option in *.env* file variable *ELASTIC_ENV* (cloud, local).

First, create a *.env* file in the root directory and fill some global environment variable:

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
QUERY_MAX_ROWS=2000
QUERY_PAGINATION=30
SEARCH_THRESHOLD=0.4
TIME_SLEEP=2
# WEBSITE=https://vietnamnet.vn/tim-kiem
WEBSITE=https://zingnews.vn/a-tim-kiem.html
```

**Note:** For ENV variable in *.env*. In the first time run, I recommend set this ***ENV=local*** to push database of this project into elasticsearch storage. So when next times, we don't need to push it again and can set ***ENV=cloud*** to improve time processing. (Importance if you need to deploy this app into cloud like Azure, ...)

After configuration process, run file *app.py* in root directory and search for the keywork you want to find.

```
python app.py
```

In root directory, there are some python files:

- *app.py*: Python Flask page application (main)
- *crawl.py*: Tool selenium crawl newspaper
- *db_to_csv*: Tool convert .db sqlite into .csv file

Website demo:
- Render: https://crawl-newspaper.onrender.com (Commit version #5)
- Azure: https://crawl-newspaper.azurewebsites.net (Latest commit)

> Star repository if you like it. Have a nice day !!!