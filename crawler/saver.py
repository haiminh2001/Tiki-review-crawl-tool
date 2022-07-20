from tqdm import tqdm
import pandas as pd
import os
import time
import pyarrow.parquet as pq
import pyarrow as pa

DIR_PATH = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)) 
HDFS_FOLDER = 'hadoop1/dfs/data/'
def read():
    folder = DIR_PATH + '/tmpdata/'
    result = []
    for filename in tqdm(os.listdir(folder)):
        f = os.path.join(folder, filename)
        if os.path.isfile(f) and ".parquet" in f:
            result.append(pd.read_parquet(f))
  
    return pd.concat(result)

def write_hdfs():
    file_name = str(time.ctime(time.time()).lower()) + '.parquet.gzip'

    fs = pa.fs.HadoopFileSystem('hdfs://namenode', port = 9000)
    with fs.open(HDFS_FOLDER + file_name, "wb") as fw:
        pq.write_table(read(), fw)


if __name__ == '__main__':
    write_hdfs()
