from datetime import datetime

import psycopg2
from flask import Flask, render_template

import config

year = datetime.now().year
params = config.sql_db
app = Flask(__name__)

# Create headers
headers_list = ["COMPANY", "CLIENT", "PHONE NUMBER", "ORDER NAME", "ORDER TERM",
                "STATUS", "COMMENTS", "UPDATED"]

headers = [item for item in headers_list]


@app.route('/')
def order_table():
    """ HOME page TABLE """
    # Connect to SQL and fetch data
    con = psycopg2.connect(**params)
    cur = con.cursor()
    cur.execute(
        """SELECT id, company, client, phone_number, order_name,
        order_term, status, comments, update_date
        FROM orders 
        ORDER BY status ASC, order_term ASC, order_name ASC, client ASC""")
    query = cur.fetchall()
    con.close()

    # Create list of data from SQL
    row_data = []

    for data in enumerate(query):
        row_data.append(data)

    # List of name to drop-down sort_by_name
    show_by_name = []
    for name in query:
        if name[4] != "" and name[4] != None:
            show_by_name.append(name[4])

    return render_template('index.html', head=headers, data=row_data, date=year, show_names=show_by_name)


if __name__ == '__main__':
    app.run(debug=True)
