import pymysql
from dbutils.pooled_db import PooledDB

DB_CONFIG = {
    'host': "gateway01.ap-southeast-1.prod.alicloud.tidbcloud.com", 
    'port': 4000,
    'user': "dWvV6NjZWtDcYdR.root",                 
    'password': "bma7yOw0fsh9exQM",           
    'database': "seminar_reservasi",       
    'cursorclass': pymysql.cursors.DictCursor,
    'ssl': {
        'min_version': 'TLSv1.2' 
    }
}

pool = PooledDB(pymysql, maxconnections=5, **DB_CONFIG)

def get_db_connection():
    return pool.connection()