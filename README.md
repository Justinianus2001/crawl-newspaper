# Getting Started

This repository used to crawl and search for newspaper info (title, link, image, tag, preview, author, timestamp) from website https://vietnamnet.vn, https://zingnews.vn use flask, selenium and elasticsearch library in python 3.

**Note:** Before use this project, you need an elasticsearch cloud account, or have local setup instead. To switch mode, there are two option in *.env* file variable *ELASTIC_ENV* (cloud, local).

First, create a *.env* file in the root directory and fill some global environment variable:

```
BATCH_ELASTICSEARCH=your-local-elasticsearch-batch-file
BATCH_KIBANA=your-local-kibana-batch-file
DB_FILE=database.db
CSV_FILE=database.csv
ELASTIC_CLOUD_ID=your-elastic-cloud-id
ELASTIC_ENV=cloud
ELASTIC_PASSWORD=your-elastic-cloud-password
QUERY_MAX_ROWS=2000
QUERY_PAGINATION=30
TIME_SLEEP=2
# WEBSITE=https://vietnamnet.vn/tim-kiem
WEBSITE=https://zingnews.vn/a-tim-kiem.html
```

After configuration process, run file *app.py* in root directory and search for the keywork you want to find.

```
python app.py
```

Have a nice day !!!