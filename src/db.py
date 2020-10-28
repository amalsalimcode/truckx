import sqlite3 as sql
import pymongo


def get_db(read=False):
    con = sql.connect("database.db")
    if read:
        con.row_factory = sql.Row
    return con.cursor(), con

def get_mongo_db(col):
    m_client = pymongo.MongoClient("mongodb://localhost:27017/")
    m_db = m_client["mydb"]
    return m_db[col]


def create_location(imei, l_time, l_lat, l_long):
    mycol = get_mongo_db(imei)
    mycol.insert_one({"time": l_time, "lat": l_lat, "long": l_long})


def init_table():
    cur, con = get_db()
    # con.execute('DROP TABLE alarm')
    # con.execute('DROP TABLE video_file')

    con.execute('CREATE TABLE if not exists alarm '
                '(type varchar(100),'
                'imei TEXT,'
                'time DATETIME,'
                'lat TEXT,'
                'long TEXT)')

    con.execute('CREATE TABLE if not exists video_file'
                '(file_name VARCHAR(100),'
                'alarm_id INTEGER,'
                'FOREIGN KEY (alarm_id) REFERENCES alarm(id))')

    con.commit()
    con.close()

def create_alarm(imei, al_type, al_time, lat, long):
    cur, con = get_db()
    con.execute('INSERT INTO alarm (imei, type, time, lat, long) VALUES (?, ?, ?, ?, ?)',
                [imei, al_type, al_time, lat, long])
    row_id = con.execute('select last_insert_rowid()').fetchone()[0]
    con.commit()
    con.close()
    return row_id

def create_file(alarm_id, file_name):
    cur, con = get_db()
    con.execute('INSERT INTO video_file (alarm_id, file_name) VALUES (?, ?)',
                [alarm_id, file_name])
    row_id = con.execute('select last_insert_rowid()').fetchone()[0]
    con.commit()
    con.close()
    return row_id

def get_alarms():
    cur, con = get_db(True)
    rows = cur.execute("SELECT * from alarm").fetchall()
    con.close()
    return [[x[0], x[1], x[2], x[3], x[4]] for x in rows] if len(rows) else []

def get_alarm_from_args(st_dt, end_dt, alarm_type):
    """ex: select * from alarm where type = "CRASH" AND imei="234234" AND time BETWEEN "2019-08-18 12:00:00 AM"
            AND "2025-08-18 12:00:00 AM";"""
    cur, con = get_db(True)
    rows = cur.execute("SELECT * from alarm WHERE type=(?) AND imei=(?) AND time BETWEEN (?) AND (?)",
                       [st_dt, end_dt, alarm_type]).fetchall()
    con.close()
    return [[x[0], x[1], x[2], x[3], x[4]] for x in rows] if len(rows) else []

