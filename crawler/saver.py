import pandas as pd
import os
import time
import pyarrow.parquet as pq
import pyarrow as pa

DIR_PATH = '/crawler/'
HDFS_FOLDER = '/hadoop/dfs/data/'
def read():
    folder = DIR_PATH + 'tmpdata/'
    result = []
    for filename in os.listdir(folder):
        f = os.path.join(folder, filename)
        if os.path.isfile(f) and ".parquet" in f:
            result.append(pd.read_parquet(f))
  
    return pd.concat(result)

def write_hdfs():
    file_name = str(time.ctime(time.time()).lower()) + '.parquet'
    file_name = file_name.replace(' ', '_')
    file_name = file_name.replace(':', '_')
    fs = pa.fs.HadoopFileSystem('hdfs://namenode', port = 9000)
    table = pa.Table.from_pandas(read())
    
    pq.write_to_dataset(table, root_path= HDFS_FOLDER + file_name, filesystem=fs)


if __name__ == '__main__':
    write_hdfs()

