import psycopg2
from configparser import ConfigParser

import config

params = config.sql_db

# # create a parser
# parser = ConfigParser()
# # read config file
# parser.read('config.ini')
#
# params = {}
# if 'postgreDB' in parser:
#     for key in parser['postgreDB']:
#         params[key] = parser['postgreDB'][key]
# else:
#     raise Exception(
#         'Section {0} not found in the {1} file'.format('postgreDB', 'config.ini'))

# Orders DB Table
conn = psycopg2.connect(**params)
cur = conn.cursor()

cur.execute(("""CREATE TABLE IF NOT EXISTS orders (
            ID INT GENERATED ALWAYS AS IDENTITY,
            company TEXT,
            client TEXT,
            phone_number TEXT,
            order_name TEXT,
            order_term TEXT,
            status TEXT,
            comments TEXT,
            update_date TEXT
            )
            """))

conn.commit()

conn.close()
