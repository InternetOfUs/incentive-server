import traceback

# import MySQLdb
import pymysql


def err(logger, ecxeption, message=None):
    logger.error("{}. Error: {}".format(message if message else '', ecxeption))
    logger.error(traceback.format_exc())


def mysql_connect(**config):
    return pymysql.connect(host=config['host'], user=config['user'], passwd=config['password'], db=config['db'])


def get_stream_latest_id(mysql_cursor):
    mysql_cursor.execute("""
    SELECT id
    FROM stream
    ORDER BY  id DESC 
    LIMIT 1 
    """)
    rows = mysql_cursor.fetchall()
    row = rows[0]
    latest_id = row[0]
    return latest_id


def get_stream_latest_time(mysql_cursor):
    mysql_cursor.execute("""
    SELECT created_at
    FROM incentive_usersactivity
    ORDER BY  created_at DESC 
    LIMIT 1 
    """)
    rows = mysql_cursor.fetchall()
    row = rows[0]
    latest_time = row[0]
    return latest_time

