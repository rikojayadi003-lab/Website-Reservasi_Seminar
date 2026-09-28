import os
import pymysql
import certifi

def get_db_connection():
    return pymysql.connect(
        host=os.environ["TIDB_HOST"],
        port=4000,
        user=os.environ["TIDB_USER"],
        password=os.environ["TIDB_PASSWORD"],
        database=os.environ.get("TIDB_DATABASE", "seminar_reservasi"),
        cursorclass=pymysql.cursors.DictCursor,
        connect_timeout=15,
        read_timeout=20,
        write_timeout=20,
        ssl_ca=certifi.where(),
        ssl_verify_cert=True,
        ssl_verify_identity=True
    )