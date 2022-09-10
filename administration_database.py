import sqlite3


def create_admin_database():
    db = sqlite3.connect("admin_database.db")
    c = db.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS admin_data(

        name text,
        password text,
        subject_choice_enabled text,
        departments_locked text,
        result_published text,
        primary_department_choice text

    )""")
    db.commit()

    c.execute("""CREATE TABLE IF NOT EXISTS std_data(

        name text,
        password text,
        marks integer,
        dept_choice integer,
        obtained_department text


    )""")
    db.commit()

    c.execute("""CREATE TABLE IF NOT EXISTS departments(

        dept_name text,
        seat_capacity integer,
        left_seat integer

    )""")
    db.commit()
    db.close()


def query_left_seat(dept_name):
    db = sqlite3.connect("admin_database.db")
    c = db.cursor()
    c.execute("SELECT left_seat FROM departments WHERE dept_name = (?)", (dept_name,))
    data = c.fetchall()[0][0]
    db.close()
    return data


def get_merit():
    db = sqlite3.connect("admin_database.db")
    c = db.cursor()
    c.execute("SELECT name,marks FROM std_data ORDER BY marks DESC")
    data = c.fetchall()
    db.close()
    return data


def query_admin_data(query):
    db = sqlite3.connect("admin_database.db")
    c = db.cursor()
    c.execute(f"SELECT {query} FROM admin_data")
    data = c.fetchall()
    db.close()
    return data


def input_std_data(name, password, marks, dept_choice, obtained_dept):
    db = sqlite3.connect("admin_database.db")
    c = db.cursor()
    c.execute("INSERT INTO std_data VALUES(?,?,?,?,?)", (name, password, marks, dept_choice, obtained_dept))
    db.commit()
    db.close()


def input_departments(dept, seat_capacity, left_seat):
    db = sqlite3.connect("admin_database.db")
    c = db.cursor()
    c.execute("INSERT INTO departments VALUES(?,?,?)", (dept, seat_capacity, left_seat,))
    db.commit()
    db.close()


def input_primary_department_choice(value):
    choices = eval(fetch_admin_data()[0][5])
    choices.append(value)
    db = sqlite3.connect("admin_database.db")
    c = db.cursor()
    c.execute("UPDATE admin_data SET primary_department_choice = (?) WHERE rowid = 1", (repr(choices),))
    db.commit()
    db.close()


def fetch_admin_data():
    db = sqlite3.connect("admin_database.db")
    c = db.cursor()
    c.execute("SELECT * FROM admin_data")
    data = c.fetchall()
    db.close()
    return data


def fetch_student():
    db = sqlite3.connect("admin_database.db")
    c = db.cursor()
    c.execute("SELECT * FROM std_data")
    data = c.fetchall()
    db.close()
    return data


def fetch_departments():
    db = sqlite3.connect("admin_database.db")
    c = db.cursor()

    # fetching department names
    c.execute("SELECT * FROM departments")
    data = c.fetchall()

    # fetching row id for primary subject choice
    c.execute("SELECT rowid FROM departments")
    primary_keys = c.fetchall()
    row_id = []
    for v in primary_keys:
        row_id.append(v[0])

    db.close()
    return data, row_id


def update_admin_data(table, name, new_data):
    db = sqlite3.connect("admin_database.db")
    c = db.cursor()
    c.execute(f"UPDATE {table} SET {name} = (?) where rowid = 1", (new_data,))
    db.commit()
    db.close()


def lock_departments():
    db = sqlite3.connect("admin_database.db")
    c = db.cursor()
    c.execute("UPDATE admin_data SET departments_locked = 'TRUE'")
    db.commit()
    db.close()


def update_left_seat(dept_name):
    new_data = 0
    for v in fetch_departments()[0]:
        if v[0] == dept_name:
            new_data = v[2] - 1
    db = sqlite3.connect("admin_database.db")
    c = db.cursor()
    c.execute(f"UPDATE departments SET left_seat = (?) WHERE dept_name = (?)", (new_data, dept_name))
    db.commit()
    db.close()


def update_obtained_dept(student_name, dept_name):
    db = sqlite3.connect("admin_database.db")
    c = db.cursor()
    c.execute(f"UPDATE std_data SET obtained_department = (?) WHERE name = (?)", (dept_name, student_name))
    db.commit()
    db.close()


def update_std_data(table, col_name, new_data, std_name):
    db = sqlite3.connect("admin_database.db")
    c = db.cursor()
    c.execute(f"UPDATE {table} SET {col_name} = (?) WHERE name = (?)", (new_data, std_name))
    db.commit()
    db.close()


def cancel_student(student_name):
    adm_db = sqlite3.connect("admin_database.db")
    c = adm_db.cursor()
    c.execute("DELETE FROM std_data WHERE name = (?)", (student_name,))
    adm_db.commit()

    for v in fetch_departments()[0]:
        seat_cap = v[1]
        c.execute("UPDATE departments SET left_seat = (?) WHERE dept_name = (?)", (seat_cap, v[0]))
        adm_db.commit()

    adm_db.close()

    std_db = sqlite3.connect("st_database.db")
    c = std_db.cursor()
    c.execute("DELETE FROM std_data WHERE name = (?)", (student_name,))
    std_db.commit()
    std_db.close()
