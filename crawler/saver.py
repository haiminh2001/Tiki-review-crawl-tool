import pandas as pd
import os
import time
import pyarrow.parquet as pq
import pyarrow as pa
from elasticsearch import Elasticsearch
import json

DIR_PATH = '/crawler/'
HDFS_FOLDER = '/hadoop/dfs/data/review/'
HDFS_FOLDER_ITEM = '/hadoop/dfs/data/item/'
INDEX="review"
INDEX_ITEM = 'item'
TYPE= "record"
BATCH_SIZE = 100000

def rec_to_actions(df, index):
    for record in df.to_dict(orient="records"):
        yield ('{ "index" : { "_index" : "%s", "_type" : "%s" }}'% (index, TYPE))
        yield (json.dumps(record, default=int))
        
def read():
    folder = DIR_PATH + 'tmpdata/'
    result = []
    for filename in os.listdir(folder):
        f = os.path.join(folder, filename)
        if os.path.isfile(f) and ".parquet" in f:
            result.append(pd.read_parquet(f))
            os.remove(f)
    folder_item = DIR_PATH + 'tmpdata_item/'
    result_item = []
    for filename in os.listdir(folder_item):
        f = os.path.join(folder_item, filename)
        if os.path.isfile(f) and ".parquet" in f:
            result_item.append(pd.read_parquet(f))
            os.remove(f)
    return pd.concat(result), pd.concat(result_item)

def write_hdfs(df, folder):
    file_name = str(time.ctime(time.time()).lower()) + '.parquet'
    file_name = file_name.replace(' ', '_')
    file_name = file_name.replace(':', '_')
    fs = pa.fs.HadoopFileSystem('hdfs://namenode', port = 9000)
    for i in range(0, df.shape[0], BATCH_SIZE):
        end = min(i + BATCH_SIZE, df.shape[0])
        table = pa.Table.from_pandas(df.iloc[i:end])
        try:
            pq.write_to_dataset(table, root_path= folder + file_name, filesystem=fs)
        except:
            pass

def write_es(df, index):
    e = Elasticsearch('172.18.0.1:9200') # no args, connect to localhost:9200
    for i in range(0, df.shape[0], BATCH_SIZE):
        end = min(i + BATCH_SIZE, df.shape[0])
        try:
            e.bulk(rec_to_actions(df.iloc[i:end], index)) # return a dict
        except:
            pass

if __name__ == '__main__':
    df, df_item = read()
    try:
        write_hdfs(df, HDFS_FOLDER)
    except:
        pass
    try:
        write_hdfs(df_item, HDFS_FOLDER_ITEM)
    except:
        pass
    try:
        write_es(df, INDEX)
    except:
        pass
    try:
        write_es(df_item, INDEX_ITEM)
    except:
        pass