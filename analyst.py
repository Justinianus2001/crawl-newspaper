import os
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

lst = pd.read_csv(os.getenv("CSV_FILE"))
# lst.dropna(axis=0, inplace=True)
lst = lst.values

# Get number of posts for each tag
tag = [doc[4] for doc in lst]
val1 = dict(sorted(dict((x, tag.count(x))
                        for x in set(tag)).items(), key=lambda item: item[1]))
print(val1)

# Get list of unique title length
title = [doc[1] for doc in lst]
val2 = sorted(set(len(x.split(" ")) for x in title if str(x) != "nan"))
print(val2)

# Get list of unique timestamp
timestamp = [doc[7] for doc in lst]
val3 = sorted(set(datetime.strptime(time[:time.find(" ")], "%d/%m/%Y").strftime("%Y-%m-%d")
                  for time in timestamp if time != "Unknown" and str(time) != "nan"))
print(val3)