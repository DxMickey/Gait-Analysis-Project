from msilib.schema import Error
import sqlite3


def database(name):
    conn = connect("oldData.db")
    createTable(conn, name)
    #insertData(conn, name)

# Connect to database file
def connect(dbFile):
    try:
        connection = sqlite3.connect(dbFile)
    except Error as e:
        print(e)
    return connection

# Creates a new table in the database with raw data from file
def createTable(conn, name):
    try:
        cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS {} (time DECIMAL, stamp DECIMAL, battery DECIMAL, pressure DECIMAL, temperature DECIMAL, ax DECIMAL, ay DECIMAL, az DECIMAL, gx DECIMAL, gy DECIMAL, gz DECIMAL, mx DECIMAL, my DECIMAL, mz DECIMAL, averagea DECIMAL);".format(name))
        conn.close()
    except Error as e:
        print(e)

# Inserts raw data into created table
def insertData(conn, name):
    try:
        cur = conn.cursor()
        cur.execute("INSERT INTO {} VALUES (1,2,3,4,5,6,7,8,9,10,11,12,13)".format(name))
        conn.commit()
    except Error as e:
        print(e)  
