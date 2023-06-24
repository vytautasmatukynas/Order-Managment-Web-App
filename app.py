from datetime import datetime

import psycopg2
from flask import Flask, render_template, request, redirect, url_for, flash
import config
from time import sleep


# Import current date
year = datetime.now().year
date_today = datetime.today().strftime('%Y-%m-%d')

# Import DB conn
params = config.sql_db

# Create Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = "my secret key"

# Create headers list
HEADERS = ["COMPANY", "CLIENT", "PHONE NUMBER", "ORDER NAME", "ORDER TERM",
            "STATUS", "COMMENTS", "UPDATED", "", ""]

# name for "label" "id" "name". Look at add.html for loop
LABEL_NAMES = ['Company', 'Client', 'Phone Number', 'Order Name', 'Order Term', 'Status', 'Comments']


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

    return render_template('index.html', headers=HEADERS, year=year, data=data, show_names=show_names)


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

    return render_template('index.html', headers=HEADERS, year=year, data=data, show_names=show_names)


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

    return render_template('index.html', headers=HEADERS, year=year, data=data, show_names=show_names)


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

        return render_template('index.html', headers=HEADERS, year=year, data=data, show_names=show_names)
    
    else:
        return redirect(url_for('order_table'))


@app.route('/add_new', methods=['GET', 'POST'])
def add_order():
    """ ADD NEW RECORD FORM """
    # if methods is POST get all data from FORM and add it to SQL. Update_date doesn't have request.form,
    # it just auto fills cell with current date.
    if request.method == 'POST':  
        company = request.form['Company']
        client = request.form['Client']
        phone_number = request.form['Phone Number']
        order_name = request.form['Order Name']
        order_term = request.form['Order Term']
        status = request.form['Status']
        comments = str(request.form['Comments'])
        update_date = f'{date_today}'
        
        conn = psycopg2.connect(
                **params
            )

        cur = conn.cursor()

        cur.execute('''INSERT INTO orders (company, client, phone_number, order_name,
            order_term, status, comments, update_date) VALUES
            (%s, %s, %s, %s, %s, %s, %s, %s)''',
            (company, client, phone_number, order_name,
            order_term, status, comments, update_date,))

        conn.commit()
        conn.close()
        
        # if everything is ok, then you will be redirected to main page with table
        return redirect(url_for('order_table'))
        
    return render_template('add.html', label_names=LABEL_NAMES, date_today=date_today)


@app.route('/update_order/<int:row_id>', methods=['GET', 'POST'])
def update_order(row_id):
    """ UPDATE RECORD FORM """
    # if methods is POST get all data from FORM and add it to SQL.
    # if method is GET, gets all data from SQL and fills form with that data,
    # look at html file update.html
    # Update_date doesn't have request.form, it just auto fills cell with current date.
    row_id_ = None
    
    if request.method == 'POST':  
        row_id_ = row_id
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

        cur.execute('''UPDATE orders SET company = %s, client = %s, phone_number = %s, order_name = %s, 
                    order_term = %s, status = %s, comments = %s, update_date = %s WHERE id = %s''',
            (company, client, phone_number, order_name,
            order_term, status, comments, update_date, row_id_))

        conn.commit()
        conn.close()
        
        # if everything is ok, then you will be redirected to main page with table
        return redirect(url_for('order_table'))
    
    if request.method == "GET":
        row_id_ = row_id
        con = psycopg2.connect(**params)
        cur = con.cursor()
        cur.execute(
            f"""SELECT * FROM orders WHERE ID=%s""", (row_id_,))
        order_items = cur.fetchone()
        con.close()
        order_data_dict = {LABEL_NAMES[i]:order_items[i+1] for i in range(0, len(LABEL_NAMES))}

        
    return render_template('update.html', label_names=LABEL_NAMES, date_today=date_today, order_data_dict=order_data_dict, order_items=order_items)


@app.route('/delete/<int:row_id>', methods=['GET', 'POST'])
def delete_order(row_id):
    """ DELETE RECORD """
    row_id_ = None
    
    if request.method == "POST":
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        cur.execute("DELETE FROM orders WHERE id = %s", (row_id,))
        conn.commit()
        conn.close()
        flash(f"Row with id:{row_id} was deleted.")
        # after deleting row, redict to main page
        return redirect(url_for('order_table'))
    
    elif request.method == "GET":
        row_id_ = row_id
    
    return render_template('delete.html', row_id = row_id_)


if __name__ == "__main__":
    app.run(debug=True, port=8000)