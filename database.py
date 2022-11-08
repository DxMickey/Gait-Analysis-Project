from datetime import datetime
from msilib.schema import Error
import sqlite3
import os
import datetime

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

def additionalDataTable(sensorId, tableName, subject, senLoc, senCon, date):
    conn = connect("oldData.db")
    try:
        cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS \"{}_data\" (\"Sensor ID\" STRING, Subject STRING, \"Sensor location\" STRING, \"Sensor condition\" STRING, \"Data created\" DATE);".format(tableName))
        conn.close()
    except Error as e:
        print(e)
    insertIntoAddedTable(sensorId, tableName, subject, senLoc, senCon, date)

def insertIntoAddedTable(sensorId, tableName, subject, senLoc, senCon, date):
    conn = connect("oldData.db")
    try:
        cur = conn.cursor()
        cur.execute("INSERT INTO \"{}_data\" VALUES (\"{}\", \"{}\", \"{}\", \"{}\", \"{}\");".format(tableName, sensorId, subject, senLoc, senCon, date))
        conn.commit()
        conn.close()
    except Error as e:
        print(e)

def createPeaks(name):
    try:
        conn = connect("oldData.db")
        tableName = name + "_peaks"
        cur = conn.cursor()
        cur.execute("DROP TABLE IF EXISTS {};".format(tableName))
        cur.execute("CREATE TABLE IF NOT EXISTS {} (peak DECIMAL);".format(tableName))
        conn.close()
    except Error as e:
        print(e)




def insertPeaks(tableName, peak):
    conn = connect("oldData.db")
    try:
        cur = conn.cursor()
        cur.execute("INSERT INTO \"{}_peaks\" VALUES (\"{}\");".format(tableName, peak))
        conn.commit()
        conn.close()
    except Error as e:
        print(e)