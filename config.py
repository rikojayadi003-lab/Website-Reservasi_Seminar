
import os
import pymysql
import certifi

def get_db_connection():
    return pymysql.connect(
        host=os.environ["gateway01.ap-southeast-1.prod.aws.tidbcloud.com"],
        port=4000,
        user=os.environ["2W4sHi5ewciZ98n.root"],
        password=os.environ["PEhLivq4HXSUgDAx"],
        database=os.environ.get(
            "TIDB_DATABASE", "reserv-seminardb"
        ),
        cursorclass=pymysql.cursors.DictCursor,
        connect_timeout=15,
        read_timeout=20,
        write_timeout=20,
        ssl_ca=certifi.where(),
        ssl_verify_cert=True,
        ssl_verify_identity=True
    )