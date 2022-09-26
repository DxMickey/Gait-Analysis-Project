from posixpath import split
import tkinter as tk
from tkinter import filedialog
from turtle import position
import AndriiMSc_Number_of_Peaks as peaks
import os

from database import database

# Table name that the user chose to save into database
chosen_File_Name = "test"

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
        
        database(chosen_File_Name)

    peaks.main(options.get(), filesList)


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