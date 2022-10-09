from msilib.schema import Error
import sqlite3

from pandas import DataFrame




def database(name):
    conn = connect("oldData.db")
    createTable(conn, name)

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