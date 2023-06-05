from datetime import datetime

import psycopg2
from flask import Flask, render_template, request, redirect, url_for
import config


year = datetime.now().year
date_today = datetime.today().strftime('%Y-%m-%d')
params = config.sql_db
app = Flask(__name__)
app.config['SECRET_KEY'] = "my secret key"

# Create headers
headers_list = ["COMPANY", "CLIENT", "PHONE NUMBER", "ORDER NAME", "ORDER TERM",
                "STATUS", "COMMENTS", "UPDATED"]
headers = [item for item in headers_list]


@app.route('/')
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

    return render_template('index.html', headers=headers, year=year, data=data, show_names=show_names)


@app.route("/filter/<order_name>")
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

    return render_template('index.html', headers=headers, year=year, data=data, show_names=show_names)


@app.route("/sort/<sort_name>")
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
    dict_sort = {headers[i]: headers_sql_[i] for i in range(0, len(headers))}
    # print(dict_sort)

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
            # print(sort_name)
            sort_name_ = dict_sort[key]
            # print(sort_name_)
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

    return render_template('index.html', headers=headers, year=year, data=data, show_names=show_names)


@app.route('/search', methods=['GET', 'POST'])
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

        return render_template('index.html', headers=headers, year=year, data=data, show_names=show_names)
    
    else:
        return redirect(url_for('order_table'))

@app.route('/add_new', methods=['GET', 'POST'])
def add_order():
    """ ADD NEW RECORD FORM """
    # name for "label" "id" "name". Look at add.html for loop
    label_names = ['Company', 'Client', 'Phone Number', 'Order Name', 'Order Term', 'Status', 'Comments']
    
    # if methos is POST get all data from FORM and add it to SQL. update_date doesnt have form, it just auto fills cell with current date
    if request.method == 'POST':  
        company = request.form['Company']
        client = request.form['Client']
        phone_number = request.form['Phone Number']
        order_name = request.form['Order Name']
        order_term = request.form['Order Term']
        status = request.form['Status']
        comments = request.form['Comments']
        update_date = f'{date_today}'
        
        conn = psycopg2.connect(
                **params
            )

        cur = conn.cursor()

        cur.execute('''INSERT INTO orders (company, client, phone_number, order_name,
            order_term, status, comments, update_date) VALUES
            (%s, %s, %s, %s, %s, %s, %s, %s)''',
            (company, client, phone_number, order_name,
            order_term, status, comments, update_date))

        conn.commit()
        conn.close()
        
        # if everything is ok, that you will be redirected to main page with table
        return redirect(url_for('order_table'))
        
    return render_template('add.html', label_names=label_names, date_today=date_today)













