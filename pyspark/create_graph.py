#coding:utf-8

# Using pyspark select data from hive table which contains user-click-sku data, and create a user-item graph.
# Also hash user id and sku id and random feature for vertices.

from __future__ import print_function
import sys
import os

os.environ['PYSPARK_PYTHON'] = '/usr/bin/python'

# for python2
if sys.version_info.major == 2:
    reload(sys)
    sys.setdefaultencoding('utf-8')

from pyspark.sql import SparkSession
from pyspark.sql.functions import rand, randn
from pyspark.sql.functions import concat, col, udf, lit
from pyspark.sql import Row
from pyspark.sql.types import *
import random
import datetime
from timeit import default_timer as timer

master = 'yarn'
is_pre_load = False
is_cache = False
partition = 100
hive_table_name = ''
dt = 'dt="2021-00-00"'
max_hash = 2 * 10**7
limit = 5 * 10**7
base_path = 'hdfs://path'
executor_memory = '4g'
executor_core = '2'
driver_memory = '4g'

if master == 'yarn':
    # yarn-client
    spark = SparkSession.builder\
        .master('yarn')\
        .appName("name")\
        .enableHiveSupport()\
        .config("spark.executor.instances", "50")\
        .config("spark.executor.memory", executor_memory)\
        .config("spark.executor.cores", executor_core)\
        .config("spark.driver.memory", driver_memory)\
        .config("spark.sql.shuffle.partitions", "500")\
        .getOrCreate()
else:
    spark = SparkSession.builder\
     .master('local[*]')\
     .appName("name")\
     .enableHiveSupport()\
     .config("spark.executor.memory", executor_memory)\
     .config("spark.executor.cores", executor_core)\
     .config("spark.driver.memory", driver_memory)\
     .config("spark.memory.offHeap.enabled",true)\
     .config("spark.memory.offHeap.size","16g")\
     .getOrCreate()


def now(msg=''):
    print(msg, datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))


# 1. raw data use spark-submit create_graph.py
if is_pre_load:
    df = spark.read.parquet(base_path + '/cache_raw_data')
else:
    sql = 'SELECT user_id,sku_id FROM ' + hive_table_name

    if dt is not None:
        sql += ' where '
        sql += dt

    if limit is not None:
        sql += ' LIMIT {}'.format(limit)

    # select data
    df = spark.sql(sql).drop_duplicates()
    if is_cache:
        start = timer()
        now('cache_raw_data')
        df.write.parquet(base_path + '/cache_raw_data', mode='overwrite')
        end = timer()
        print(end - start, 'secs')

# 2. hash data use pyspark --master local[*] or spark-submit data.py with local[*]
# due to no numpy error when using yarn


@udf
def hash_user(x):
    return int(x.indices[0])


@udf
def hash_sku(x):
    if len(x.indices) > 1:
        return int(x.indices[1])
    else:
        return 0


if is_pre_load:
    dh = spark.read.parquet(base_path + '/cache_hash_data')
else:
    # hash user and sku
    from pyspark.ml.feature import FeatureHasher
    hasher = FeatureHasher(numFeatures=max_hash,
                           inputCols=['user_id', 'sku_id'],
                           outputCol='hash')

    ds = hasher.transform(df)
    dh = ds.select(
        hash_user('hash').alias('hash_user'),
        hash_sku('hash').alias('hash_sku'))

    if is_cache:
        start = timer()
        now('cache_hash_data')
        dh.write.parquet(base_path + '/cache_hash_data', mode='overwrite')
        end = timer()
        print(end - start, 'secs')

# 3. use spark-submit data.py with yarn

# swap user and sku to make undirected graph
dhs = dh.select(
    col('hash_sku').alias('hash_user'),
    col('hash_user').alias('hash_sku'))

edge = dh.union(dhs)

edge = edge.select(
    lit(0).alias('type'),
    col('hash_user').alias('src'),
    col('hash_sku').alias('dst'),
    lit(1.0).alias('weight'))


@udf
def rand_feature(s):
    rf = ['{:.8f}'.format(random.random()) for _ in range(8)]
    return ','.join(rf)


vertex = edge.groupby('src').count()
vertex = vertex.select(
    lit(0).alias('type'),
    col('src').alias('id'),
    lit(1.0).alias('weight'),
    rand_feature('src').alias('feature'))

start = timer()
now('save vertex')
vertex.coalesce(partition).write.csv(base_path + '/vertex',
                                     sep='\t',
                                     mode='overwrite')
end = timer()
print(end - start, 'secs')

start = timer()
now('save edge')
edge.coalesce(partition).write.csv(base_path + '/edge',
                                   sep='\t',
                                   mode='overwrite')
end = timer()
print(end - start, 'secs')

start = timer()
print('vertex count: {}, edge count: {}'.format(vertex.count(), edge.count()))
now('done')
end = timer()
print(end - start, 'secs')
