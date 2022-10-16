from posixpath import split
from sqlite3 import DatabaseError
import tkinter as tk
from tkinter import filedialog, Button
from turtle import position
from numpy import pad
import time

from pandas import DataFrame
from pyparsing import col
import AndriiMSc_Number_of_Peaks as peaks
import os
import pandas as pd

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from database import connect, additionalDataTable

class UI(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Gait Analysis")
        self.geometry("1600x800")
        self.config(bg="lightgray")


        def insertData():
            """ 
            User chooses which file to save data from
           
            """

            tk.messagebox.showinfo("Gait analysis",  "Choose file to save")
            df = pd.read_csv(filedialog.askopenfilename())
            df.columns = ['stamp','battery', 'pressure','temperature','ax','ay','az','gx','gy','gz','mx','my','mz']
            

            additionalData(df)
            


        def getTables():
            """
            Method returns all table names from sqlite database, that dont have _data in their name

            :return: list of table names

            """

            tablesList = []
            tablesFiltered = []
            conn = connect("oldData.db")
            res = conn.execute("SELECT name FROM sqlite_master WHERE type='table';")
            for name in res.fetchall():
                tablesList.append(name[0])
            conn.close()
            for table in tablesList:
                if "_data" not in table:
                    tablesFiltered.append(table)


            return tablesFiltered


        
        # Inserts raw and calculated data from sensor into database
        # Ideally this function would be in 'database.py', but because of an error it is here for now
        def toSQL(df: DataFrame, tableName):
            dataBox.destroy()
            fName = tableName
            conn = connect("oldData.db")
            df.to_sql(name=fName, con=conn, if_exists='replace', index=False)
            conn.close()

            refreshList()




        def additionalData(df: DataFrame):
            global dataBox
            dataBox = tk.Tk()
            dataBox.title("Additional data")
            dataBox.geometry("400x275+800+400")
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

            lblSensorCon = tk.Label(dataBox, text="Sensor condition:")
            lblSensorCon.grid(row=4, column=1)
            txtSensorCon = tk.Text(dataBox, height=1, width=20)
            txtSensorCon.grid(row=4, column=2)

            btn_yes = Button(dataBox, text="SAVE", command=lambda: 
            [
                additionalDataTable(txtTableName.get("1.0", "end-1c"), txtSubjectName.get("1.0", "end-1c"), options.get(), txtSensorCon.get("1.0", "end-1c")),
                toSQL(df, txtTableName.get("1.0", "end-1c"))
            ])
            btn_yes.grid(row=5,column=2, pady=25)


        def findPeaks():
            """
            Method for plotting out the graph with analysed data from peaks.main function
            
            """

            axes.clear()
            list1, list2 = peaks.main(dataList.get())
            axes.plot(list1[0])
            axes.plot(list2[0], linewidth = '2')
            axes.axhline(getLocation(), linewidth = '3', color = 'r')
            figure.suptitle('Acceleration ' + str(0), fontsize='30')
            axes.grid(True, 'both')
            figure_canvas.draw()


        def refreshList():
            """
            Method for updating the names of tables in dropdown menu by deleting all the items and writing new ones.

            """

            
            dataList_drop['menu'].delete(0, 'end')
            for table in getTables():
                print(table)
                dataList_drop['menu'].add_command(label=table, command=tk._setit(dataList, table))

        def getLocation():
            """
            Method for getting saved sensor location from database
            
            :return: Integer depending on the location, 14, 13 or 16
            
            """


            conn = connect("oldData.db")
            tableName = dataList.get() + "_data"
            res = conn.execute("SELECT \"Sensor location\" FROM \"{}\";".format(tableName))
            location = res.fetchone()
            print(location)
            if "Ankle" in location:
                return 14
            elif "Shank" in location: 
                return 13
            else:
                return 16

 
        
        btn_insertData = tk.Button(
            text="Save new data",
            bg="blue",
            fg="yellow",
            command=insertData

        )

        btn_Peaks = tk.Button(
            text="Find peaks",
            bg="blue",
            fg="yellow",
            command=findPeaks

        )


        # datatype of menu text
        options = tk.StringVar(self)
        options.set("Ankle")

        dataList = tk.StringVar(self)

        
        dataList_drop = tk.OptionMenu(self, dataList, *getTables())

        # Create Dropdown menu
        location_drop = tk.OptionMenu(self, options, "Ankle", "Shank", "Foot")

        location_label = tk.Label(
            text="Sensor location:"
        )

   


        frame = tk.Frame(self)

        # create a figure
        figure = plt.Figure(figsize=(12, 8), dpi=100)


        # create axes
        axes = figure.add_subplot()


        # create FigureCanvasTkAgg object
        figure_canvas = FigureCanvasTkAgg(figure, master=frame)

        figure_canvas.draw()
        figure_canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)


        # Placing the elements
        btn_insertData.place(x=140,y=90,width=120,height=40)
        location_label.place(x=140,y=180,width=89,height=25)
        location_drop.place(x=230,y=180,width=89,height=25)
        frame.place(x=400,y=0)	
        btn_Peaks.place(x=140,y=300,width=120,height=40)
        dataList_drop.place(x=230,y=499,width=89,height=25)




if __name__ == '__main__':
    GUI = UI()
    GUI.mainloop()