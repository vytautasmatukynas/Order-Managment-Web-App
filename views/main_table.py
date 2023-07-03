from datetime import datetime

import psycopg2
from flask import Blueprint, render_template, request, redirect, url_for
import config


# Blueprint
main_table = Blueprint('main_table', __name__)

# Import DB conn
params = config.sql_db

# Import current date
year = datetime.now().year
date_today = datetime.today().strftime('%Y-%m-%d')

# Create headers list
HEADERS = ["COMPANY", "CLIENT", "PHONE NUMBER", "ORDER NAME", "ORDER TERM",
            "STATUS", "COMMENTS", "UPDATED", "", ""]


@main_table.route('/')
def order_table():
    """ TABLE ON HOMEPAGE """
    # Connect to SQL and fetch data
    con = psycopg2.connect(**params)
    cur = con.cursor()
    cur.execute(
        """SELECT id, company, client, phone_number, order_name,
        order_term, status, comments, update_date
        FROM orders 
        ORDER BY status ASC, order_term ASC, order_name ASC, client ASC""")
    query_start = cur.fetchall()
    con.close()

    # Create list of data from SQL, enumerate is for table row numbers -> look at table.html
    data = []

    for data_item in enumerate(query_start, 1):
        data.append(data_item)

    # List of names to drop-down sort_by_name menu
    show_names_list = []
    for name in query_start:
        if name[4] != "" and name[4] != None:
            show_names_list.append(name[4])

    show_names = set(show_names_list)

    return render_template('main_table/table.html', headers=HEADERS, year=year, data=data, show_names=show_names)


@main_table.route("/filter/<order_name>")
def filter_table(order_name):
    """ FILTER TABLE """
    order_name_ = None

    # Connect to SQL and fetch data
    con = psycopg2.connect(**params)
    cur = con.cursor()
    cur.execute(
        f"""SELECT id, company, client, phone_number, order_name,
        order_term, status, comments, update_date
        FROM orders""")
    query_start = cur.fetchall()

    # List of names to drop-down sort_by_name
    show_names_list = []
    for name in query_start:
        if name[4] != "" and name[4] != None:
            show_names_list.append(name[4])

    # Clean list
    show_names = set(show_names_list)

    # Fetch filtered table data
    data = []
    for item in show_names:
        if item == order_name:
            order_name_ = order_name
            cur.execute(
                f"""SELECT id, company, client, phone_number, order_name,
                order_term, status, comments, update_date
                FROM orders WHERE order_name = '{order_name_}'
                ORDER BY status ASC, order_term ASC, order_name ASC, client ASC""")
            query = cur.fetchall()

            # Create list of data from SQL
            for data_item in enumerate(query, 1):
                data.append(data_item)

            con.close()

    return render_template('main_table/table.html', headers=HEADERS, year=year, data=data, show_names=show_names)


@main_table.route("/sort/<sort_name>")
def sort_table(sort_name):
    """ SORT TABLE """
    sort_name_ = None

    # Connect to SQL and fetch data
    con = psycopg2.connect(**params)
    cur = con.cursor()
    cur.execute(
        f"""SELECT id, company, client, phone_number, order_name,
        order_term, status, comments, update_date
        FROM orders""")
    query_start = cur.fetchall()

    # Get headers names from sql for sorting
    headers_sql = cur.description
    headers_sql_ = [i[0] for i in headers_sql]
    headers_sql_.remove('id')
    dict_sort = {HEADERS[i]: headers_sql_[i] for i in range(0, len(HEADERS)-2)}
    print(dict_sort)

    # List of names to drop-down sort_by_name
    show_names_list = []
    for name in query_start:
        if name[4] != "" and name[4] != None:
            show_names_list.append(name[4])

    # Clean list
    show_names = set(show_names_list)

    # Fetch filtered table data
    data = []
    for key in dict_sort:
        # print(key)
        if key == sort_name:
            sort_name_ = dict_sort[key]

            cur.execute(
                f"""SELECT id, company, client, phone_number, order_name,
            order_term, status, comments, update_date
            FROM orders
            ORDER BY {sort_name_} ASC""")
            query = cur.fetchall()

            # Create list of data from SQL
            for data_item in enumerate(query, 1):
                data.append(data_item)
            con.close()

    return render_template('main_table/table.html', headers=HEADERS, year=year, data=data, show_names=show_names)


@main_table.route('/search', methods=['GET', 'POST'])
def search_table():
    """ SEARCH TABLE """
    search_form = request.form['search']
    
    if search_form != None and search_form != "":
        # Connect to SQL and fetch data
        con = psycopg2.connect(**params)
        cur = con.cursor()
        cur.execute(
            f"""SELECT id, company, client, phone_number, order_name,
            order_term, status, comments, update_date
            FROM orders""")
        query_start = cur.fetchall()

        # Connect to SQL and fetch data
        con = psycopg2.connect(**params)
        cur = con.cursor()
        cur.execute(
            f"""SELECT * FROM orders WHERE company ILIKE '%{search_form}%' OR client ILIKE '%{search_form}%' 
            OR phone_number ILIKE '%{search_form}%' OR order_name ILIKE '%{search_form}%' 
            OR comments ILIKE '%{search_form}%'
            ORDER BY status ASC, order_term ASC, order_name ASC, client ASC""")
        query = cur.fetchall()
        con.close()
        
        # Create list of data from SQL
        data = []
        for data_item in enumerate(query, 1):
            data.append(data_item)

        # List of name to drop-down sort_by_name
        show_names_list = []
        for name in query_start:
            if name[4] != "" and name[4] != None:
                show_names_list.append(name[4])

        show_names = set(show_names_list)

        return render_template('main_table/table.html', headers=HEADERS, year=year, data=data, show_names=show_names)
    
    else:
        return redirect(url_for('order_table'))