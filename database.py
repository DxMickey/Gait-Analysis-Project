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
    except Error() as e:
        print(e)
    return connection

# Creates a new table in the database with raw data from file
def createTable(conn, name):
    try:
        cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS {} (time DECIMAL, stamp DECIMAL, battery DECIMAL, pressure DECIMAL, temperature DECIMAL, ax DECIMAL, ay DECIMAL, az DECIMAL, gx DECIMAL, gy DECIMAL, gz DECIMAL, mx DECIMAL, my DECIMAL, mz DECIMAL, averagea DECIMAL);".format(name))
        conn.close()
    except Error() as e:
        print(e)

# Creates a new table in the database that has all the additional data like subject name and sensor location
def additionalDataTable(sensorId, tableName, subject, senLoc, senCon, date):
    conn = connect("oldData.db")
    try:
        cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS \"{}_data\" (\"Sensor ID\" STRING, Subject STRING, \"Sensor location\" STRING, \"Sensor condition\" STRING, \"Data created\" DATE);".format(tableName))
        conn.close()
    except Error() as e:
        print(e)
    insertIntoAddedTable(sensorId, tableName, subject, senLoc, senCon, date)

def insertIntoAddedTable(sensorId, tableName, subject, senLoc, senCon, date):
    conn = connect("oldData.db")
    try:
        cur = conn.cursor()
        cur.execute("INSERT INTO \"{}_data\" VALUES (\"{}\", \"{}\", \"{}\", \"{}\", \"{}\");".format(tableName, sensorId, subject, senLoc, senCon, date))
        conn.commit()
        conn.close()
    except Error() as e:
        print(e)

# Modifies the data inside an already existing additional data table
def editAdditionalDataTable(sensorId, tableName, subject, senLoc, senCon, originalName):
    conn = connect("oldData.db")

    cur = conn.cursor()
    cur.execute("ALTER TABLE \"{}_data\" RENAME TO \"{}_data\";".format(originalName, tableName))
    conn.commit()
    cur.execute("ALTER TABLE \"{}\" RENAME TO \"{}\";".format(originalName, tableName))
    conn.commit()
    cur.execute("UPDATE \"{}_data\" SET \"Sensor ID\"=\"{}\", Subject=\"{}\", \"Sensor location\"=\"{}\", \"Sensor condition\"=\"{}\";".format(tableName, sensorId, subject, senLoc, senCon))
    conn.commit()
    conn.close()

def deleteAllSelectedData(tableName):
    conn = connect("oldData.db")

    cur = conn.cursor()
    cur.execute("DROP TABLE \"{}_data\";".format(tableName))
    cur.execute("DROP TABLE \"{}\";".format(tableName))
    conn.commit()
    conn.close()
