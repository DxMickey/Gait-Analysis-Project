
import sqlite3
import tkinter.messagebox as messageBox

def database(name):
    conn = connect("oldData.db")
    createTable(conn, name)

# Connect to database file
def connect(dbFile):
    try:
        connection = sqlite3.connect(dbFile)
    except sqlite3.Error as e:
        messageBox.showerror("connect", e)
    return connection

# Creates a new table in the database with raw data from file
def createTable(conn, name):
    try:
        cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS {} (time DECIMAL, stamp DECIMAL, battery DECIMAL, pressure DECIMAL, temperature DECIMAL, ax DECIMAL, ay DECIMAL, az DECIMAL, gx DECIMAL, gy DECIMAL, gz DECIMAL, mx DECIMAL, my DECIMAL, mz DECIMAL, averagea DECIMAL);".format(name))
        conn.close()
    except sqlite3.Error as e:
        messageBox.showerror("createTable", e)

# Creates a new table in the database that has all the additional data like subject name and sensor location
def additionalDataTable(sensorId, tableName, subject, senLoc, senCon, date):
    conn = connect("oldData.db")
    try:
        cur = conn.cursor()
        cur.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name=\"{}_data\";".format(tableName))
        res = cur.fetchall()
        if(0 in res[0]):
            cur.execute("CREATE TABLE IF NOT EXISTS \"{}_data\" (\"Sensor ID\" STRING, Subject STRING, \"Sensor location\" STRING, \"Sensor condition\" STRING, \"Data created\" DATE);".format(tableName))
            conn.close()
            insertIntoAddedTable(sensorId, tableName, subject, senLoc, senCon, date)
        else:
            conn.close()
    except sqlite3.Error as e:
        messageBox.showerror("Error", e)

def insertIntoAddedTable(sensorId, tableName, subject, senLoc, senCon, date):
    conn = connect("oldData.db")
    try:
        cur = conn.cursor()
        cur.execute("INSERT INTO \"{}_data\" VALUES (\"{}\", \"{}\", \"{}\", \"{}\", \"{}\");".format(tableName, sensorId, subject, senLoc, senCon, date))
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        messageBox.showerror("additionalDataTable", e)

# Modifies the data inside an already existing additional data table
def editAdditionalDataTable(sensorId, tableName, subject, senLoc, senCon, originalName):
    conn = connect("oldData.db")
    try:
        cur = conn.cursor()
        if(originalName != tableName):
            cur.execute("ALTER TABLE \"{}_data\" RENAME TO \"{}_data\";".format(originalName, tableName))
            conn.commit()
            cur.execute("ALTER TABLE \"{}\" RENAME TO \"{}\";".format(originalName, tableName))
            conn.commit()
            cur.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name=\"{}_peaks\";".format(originalName))
            res = cur.fetchall()
            if(1 in res[0]): # "alter table if exists" doesn't work in SQLite
                cur.execute("ALTER TABLE \"{}_peaks\" RENAME TO \"{}_peaks\";".format(originalName, tableName))
                conn.commit()
        cur.execute("UPDATE \"{}_data\" SET \"Sensor ID\"=\"{}\", Subject=\"{}\", \"Sensor location\"=\"{}\", \"Sensor condition\"=\"{}\";".format(tableName, sensorId, subject, senLoc, senCon))
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        messageBox.showerror("editAdditionalDataTable", e)

def deleteAllSelectedData(tableName):
    conn = connect("oldData.db")
    try:
        cur = conn.cursor()
        cur.execute("DROP TABLE \"{}_data\";".format(tableName))
        cur.execute("DROP TABLE \"{}\";".format(tableName))
        cur.execute("DROP TABLE IF EXISTS \"{}_peaks\";".format(tableName))
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        messageBox.showerror("deleteAllSelectedData", e)

def createPeaks(name):
    try:
        conn = connect("oldData.db")
        tableName = name + "_peaks"
        cur = conn.cursor()
        cur.execute("DROP TABLE IF EXISTS {};".format(tableName))
        cur.execute("CREATE TABLE IF NOT EXISTS {} (peak DECIMAL);".format(tableName))
        conn.close()
    except sqlite3.Error as e:
        messageBox.showerror("createPeaks", e)

def deletePeaks(name):
    conn = connect("oldData.db")
    tableName = name + "_peaks"
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS \"{}\";".format(tableName))
    conn.commit()
    conn.close()




def insertPeaks(tableName, peak):
    conn = connect("oldData.db")
    try:
        cur = conn.cursor()
        cur.execute("INSERT INTO \"{}_peaks\" VALUES (\"{}\");".format(tableName, peak))
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        messageBox.showerror("insertPeaks", e)

def returnPeaks(item):
    conn = connect("oldData.db")
    try:
        conn.row_factory = lambda cursor, row: row[0]
        tableName = str(item) + "_peaks"
        res = conn.execute("SELECT peak FROM \"{}\";".format(tableName))
        
        peaksList = res.fetchall()
        conn.close()
        return peaksList
    except:
        return []

def getTables():
    """
    Method returns all table names from sqlite database
    :return: list of table names
    """

    tablesList = []
    conn = connect("oldData.db")
    res = conn.execute(
        "SELECT name FROM sqlite_master WHERE type = \"table\"")
    for name in res.fetchall():
        tablesList.append(name[0])
    conn.close()

    return tablesList