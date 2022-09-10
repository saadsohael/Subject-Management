import sqlite3


# creating a database
def create_st_database():
    db = sqlite3.connect("st_database.db")
    c = db.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS std_data (
            name text,
            dept_choice integer,
            auto_migration_status text,
            obtained_dept text
        )""")
    db.commit()
    db.close()


def add_std_data(name, dept_choice, auto_migration, obtained_dept):
    db = sqlite3.connect("st_database.db")
    c = db.cursor()
    c.execute("INSERT INTO std_data VALUES(?,?,?,?)", (name, dept_choice, auto_migration, obtained_dept))
    db.commit()
    db.close()


def auto_migration_status(name):
    db = sqlite3.connect("st_database.db")
    c = db.cursor()
    c.execute("SELECT auto_migration_status from std_data WHERE name = (?)", (name,))
    data = c.fetchall()[0][0]
    db.close()
    return data


def fetch_dept_choice(student_name):
    db = sqlite3.connect("st_database.db")
    c = db.cursor()
    c.execute("SELECT dept_choice FROM std_data WHERE name = (?)", (student_name,))
    data = eval(c.fetchall()[0][0])
    db.close()
    return data


def update_std_data(table, col_name, new_data, std_name):
    db = sqlite3.connect("st_database.db")
    c = db.cursor()
    c.execute(f"UPDATE {table} SET {col_name} = (?) WHERE name = (?)", (new_data, std_name))
    db.commit()
    db.close()


def query_std(table, query, col_name, std_name):
    db = sqlite3.connect("st_database.db")
    c = db.cursor()
    c.execute(f"SELECT {query} FROM {table} WHERE {col_name} = (?)", (std_name,))
    data = c.fetchall()
    db.close()
    return data


def update_dept(dept_name, student_name):
    std_db = sqlite3.connect("st_database.db")
    cursor = std_db.cursor()
    cursor.execute(f"UPDATE std_data SET obtained_dept = (?) WHERE name = (?)", (dept_name, student_name))
    std_db.commit()
    std_db.close()
