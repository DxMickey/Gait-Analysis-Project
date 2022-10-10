from posixpath import split
from sqlite3 import DatabaseError
import tkinter as tk
from tkinter import filedialog, Button
from turtle import position
from numpy import pad

from pandas import DataFrame
from pyparsing import col
import AndriiMSc_Number_of_Peaks as peaks
import os

from database import connect, additionalDataTable

root = tk.Tk()
root.title("Gait Analysis")
root.geometry("400x500")
root.config(bg="lightgray")


def runCode():
    i = 0
    filesList = []
    entryAmount = (int)(amount_entry.get())
    while i < entryAmount:
        tk.messagebox.showinfo("Gait analysis",  "Choose file number " + (str)(i + 1))
        filesList.append(filedialog.askopenfilename())
        i += 1
        #database(chosen_File_Name)

    peaks.main(options.get(), filesList)

# Inserts raw and calculated data from sensor into database
# Ideally this function would be in 'database.py', but because of an error it is here for now
def toSQL(df: DataFrame, tableName):
    dataBox.destroy()
    fName = tableName
    conn = connect("oldData.db")
    df.to_sql(name=fName, con=conn, if_exists='replace', index=False)
    conn.close()

# UI that asks the user whether they want to save the inserted data or not
def confirmSave(df: DataFrame):
    global msg
    msg = tk.Tk()
    msg.title("Save or not?")
    msg.geometry("375x115")
    msg.config(bg="lightgray")
    msg.attributes("-topmost", True)
    msg.update()
    label = tk.Label(msg, text="Save data to database?")
    label.config(bg="lightgray", font=("Arial", 16))
    label.grid(row=1,column=2, pady=25)
    btn_yes = Button(msg, text="Yes", command=lambda: additionalData(df))
    btn_yes.grid(row=2,column=1, padx=25)
    btn_no = Button(msg, text="No", command=lambda: msg.destroy())
    btn_no.grid(row=2,column=3)

def additionalData(df: DataFrame):
    msg.destroy()
    global dataBox
    dataBox = tk.Tk()
    dataBox.title("Additional data")
    dataBox.geometry("400x200")
    dataBox.config(bg="lightgray")

    lblTableName = tk.Label(dataBox, text="Table name:")
    lblTableName.grid(row=1,column=1,padx=25,pady=25)
    txtTableName = tk.Text(dataBox, height=1, width=20)
    txtTableName.grid(row=1,column=2)

    lblSubjectName = tk.Label(dataBox, text="Subject name:")
    lblSubjectName.grid(row=2,column=1)
    txtSubjectName = tk.Text(dataBox, height=1, width=20)
    txtSubjectName.grid(row=2,column=2)

    lblSensorLoc = tk.Label(dataBox, text="Sensor location:")
    lblSensorLoc.grid(row=3,column=1,pady=25)
    lblSensorLoc2 = tk.Label(dataBox, text=options.get())
    lblSensorLoc2.grid(row=3,column=2)

    btn_yes = Button(dataBox, text="SAVE", command=lambda: 
    [
        additionalDataTable(txtTableName.get("1.0", "end-1c")),
        toSQL(df, txtTableName.get("1.0", "end-1c"))
    ])
    btn_yes.grid(row=4,column=2)

btn_run = tk.Button(
    text="Analyse new data",
    bg="blue",
    fg="yellow",
    command=runCode

)


# datatype of menu text
options = tk.StringVar(root)
options.set("Ankle")

# Create Dropdown menu
location_drop = tk.OptionMenu(root, options, "Ankle", "Shank", "Foot")

amount_entry = tk.Entry(
    root, 
    width= 15)
amount_entry.insert(0, "1")

amount_label = tk.Label(
    text="How many files:"
)

location_label = tk.Label(
    text="Sensor location:"
)

amount_entry.focus_set()


# Placing the elements
btn_run.place(x=140,y=90,width=120,height=40)
amount_entry.place(x=230,y=150,width=32,height=25)
amount_label.place(x=140,y=150,width=89,height=25)
location_label.place(x=140,y=180,width=89,height=25)
location_drop.place(x=230,y=180,width=89,height=25)





root.mainloop()