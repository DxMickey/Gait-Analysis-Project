from msilib.schema import Error
import sqlite3


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

def additionalDataTable(tableName, subject, senLoc, senCon):
    conn = connect("oldData.db")
    try:
        cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS \"{}_data\" (Subject STRING, \"Sensor location\" STRING, \"Sensor condition\" STRING);".format(tableName))
        conn.close()
    except Error as e:
        print(e)
    insertIntoAddTable(tableName, subject, senLoc, senCon)

def insertIntoAddTable(tableName, subject, senLoc, senCon):
    conn = connect("oldData.db")
    try:
        cur = conn.cursor()
        cur.execute("INSERT INTO \"{}_data\" VALUES (\"{}\", \"{}\", \"{}\");".format(tableName, subject, senLoc, senCon))
        conn.commit()
        conn.close()
    except Error as e:
        print(e)