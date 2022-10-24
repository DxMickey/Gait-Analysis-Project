from datetime import datetime
from msilib.schema import File
from posixpath import split
from sqlite3 import DatabaseError
import tkinter as tk
from tkinter import CENTER, W, filedialog, Button, ttk
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
import compareGaitCycles as compGaits

from database import connect, additionalDataTable
from dataHandler import getFilteredData, readFileIntoDF, getPeaks
from baselineFinder import getBaseline
from calculations import addCols
from matplotlib.backend_bases import key_press_handler


class UI(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Gait Analysis")
        self.geometry("1800x950")
        self.config(bg="white")

        #Set the resizable property False
        self.resizable(False, False)


        def insertData():
            """ 
            User chooses which file to save data from
           
            """

            tk.messagebox.showinfo("Gait analysis",  "Choose file to save")
            file = filedialog.askopenfilename()
            df = pd.read_csv(file)
            df.columns = ['stamp','battery', 'pressure','temperature','ax','ay','az','gx','gy','gz','mx','my','mz']
            
            additionalData(df, file)
            

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

       
       
        def getDataTables():
            """
            Method returns all table names from sqlite database, that have _data in their name

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
                if "_data" in table:
                    tablesFiltered.append(table)


            return tablesFiltered


        def dateAndTime(file):
            date = os.path.getctime(file)
            date2 = datetime.fromtimestamp(date)
            return date2
        
        # Inserts raw and calculated data from sensor into database
        # Ideally this function would be in 'database.py', but because of an error it is here for now
        def toSQL(df: DataFrame, tableName):
            dataBox.destroy()
            fName = tableName
            conn = connect("oldData.db")
            df.to_sql(name=fName, con=conn, if_exists='replace', index=False)
            conn.close()

            refreshTree()

        def refreshTree():
            tree.delete(*tree.get_children())
            itemsList = getData()
            
            for i in range(0,len(itemsList),5):
                tree.insert('', 'end', values=(itemsList[i], itemsList[i+1], itemsList[i+2], itemsList[i+3], itemsList[i+4]))
            




        def additionalData(df: DataFrame, file: File):
            global dataBox
            dataBox = tk.Tk()
            dataBox.title("Additional data")
            dataBox.geometry("300x375+800+400")
            dataBox.config(bg="lightgray")

            lblTableName = tk.Label(dataBox, text="Save name:")
            lblTableName.grid(row=1,column=1,padx=25,pady=25)
            txtTableName = tk.Text(dataBox, height=1, width=20)
            txtTableName.grid(row=1,column=2)

            lblSubjectName = tk.Label(dataBox, text="Subject name:")
            lblSubjectName.grid(row=2,column=1)
            txtSubjectName = tk.Text(dataBox, height=1, width=20)
            txtSubjectName.grid(row=2,column=2)

            lblSensorLoc = tk.Label(dataBox, text="Sensor location:")
            lblSensorLoc.grid(row=3,column=1,pady=25)

            sensorLoc = tk.StringVar(dataBox, "lamp")
            rdSL1 = tk.Radiobutton(dataBox, text="Ankle", variable=sensorLoc, value="Ankle", tristatevalue="x")
            rdSL1.grid(row=3,column=2)
            rdSL2 = tk.Radiobutton(dataBox, text="Foot", variable=sensorLoc, value="Foot", tristatevalue="x")
            rdSL2.grid(row=4,column=2)
            rdSL3 = tk.Radiobutton(dataBox, text="Shank", variable=sensorLoc, value="Shank", tristatevalue="x")
            rdSL3.grid(row=5,column=2, pady=25)

            lblSensorCon = tk.Label(dataBox, text="Sensor condition:")
            lblSensorCon.grid(row=6, column=1)
            txtSensorCon = tk.Text(dataBox, height=1, width=20)
            txtSensorCon.grid(row=6, column=2)

            btn_yes = Button(dataBox, text="SAVE", command=lambda: 
            [   
                additionalDataTable(txtTableName.get("1.0", "end-1c"), txtSubjectName.get("1.0", "end-1c"), sensorLoc.get(), txtSensorCon.get("1.0", "end-1c"), dateAndTime(file)),
                toSQL(df, txtTableName.get("1.0", "end-1c"))
            ])
            btn_yes.grid(row=7,column=2, pady=25)

        def getLocation():
            """
            Method for getting saved sensor location from database
            
            :return: Integer depending on the location, 14, 13 or 16
            
            """


            conn = connect("oldData.db")
            tableName = lbl_selected['text'] + "_data"
            res = conn.execute("SELECT \"Sensor location\" FROM \"{}\";".format(tableName))
            location = res.fetchone()
            conn.close()
            print(location)
            if "Ankle" in location:
                return 14
            elif "Shank" in location: 
                return 13
            else:
                return 16

        def getData():
            conn = connect("oldData.db")
            dataList = []
            tableList = getDataTables()
            for table in tableList:
                res = conn.execute("SELECT * FROM \"{}\";".format(table))
                for data in res.fetchall():
                    dataList.append(table.replace('_data', ''))
                    dataList.append(data[0])
                    dataList.append(data[1])
                    dataList.append(data[2])
                    dataList.append(data[3])
            
        
            conn.close()
            return dataList

        def selectedSave(a):
            saveID = tree.focus()
            saveDict = tree.item(saveID)
            saveText = saveDict['values'][0]
            
            lbl_selected.config(text = saveText)

        def findPeaks():
            """
            Method for plotting out the graph with analysed data from peaks.main function
            
            """

            axes.clear()
            list1, list2 = peaks.main(lbl_selected['text'])
            axes.plot(list1[0])
            axes.plot(list2[0], linewidth = '2')
            axes.axhline(getLocation(), linewidth = '3', color = 'r')
            #figure.suptitle('Acceleration ' + str(0), fontsize='30')
            axes.grid(True, 'both')
            #axes.set_xlabel("time [cs]")
            #axes.set_ylabel("Acceleration [ms^2]")
            figure_canvas.draw()

        def compareData():
            global dots
            axes.clear()
            df = readFileIntoDF(lbl_selected['text'])
            #axes.set_title(lbl_selected['text'])

            unfiltered_acc = df.averagea
            filtered_acc = getFilteredData(df.averagea)

             # This adds the time parameter
            df.insert(len(df.columns), "filtered_acc", filtered_acc)
            filtered_acc = df.filtered_acc

             # Get peaks in filtered data
            peaks = getPeaks(filtered_acc,getLocation())
            filtered_acc = df.filtered_acc
            a = filtered_acc[peaks]

            line, = axes.plot(filtered_acc)
            dots, = axes.plot(filtered_acc[peaks].to_frame(),
                    ".", markersize=20, picker=True)

            axes.grid(True, 'both')
            axes.set_xlabel("time [cs]")
            axes.set_ylabel("Acceleration [ms^2]")

            figure_canvas.draw()

        
        def compareGait():
            global peaks, line, ax, filtered_acc
            peaks = peaks[peaks != 0]  # filter all the 0s aka stuff user just removed
            axes.clear()

            for i in range(0, len(peaks), 2):
                if(i + 2 > len(peaks)-1):
                    break
                start = peaks[i]
                end = peaks[i+2]
                gaitCycle = filtered_acc[start:end]
                # sets the index starting from 0
                axes.plot(gaitCycle.reset_index(drop=True))
            figure_canvas.draw()

        def handlePick(event):
            global peaks
            global filtered_acc
            ind = event.ind
            # event index might be an array if 2 peaks are overlapping
            for i in ind:
                peaks[i] = 0

            dots.set_xdata(peaks)
            figure_canvas.draw()




  
        
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

        lbl_selection = tk.Label(
            text= "Selected saved file is:",
            bg="white",
            font=("Arial", 13)
        )

        lbl_selected = tk.Label(
            text= "None",
            bg="white",
            font=("Arial", 13),
            anchor=W,
            wraplength=150
        )

        
        btn_compareData = tk.Button(
            text="CompareData",
            bg="blue",
            fg="yellow",
            command=compareData

        )

        btn_compareGait = tk.Button(
            text="CompareGait",
            bg="blue",
            fg="yellow",
            command=compareGait

        )



        frame = tk.Frame(self)

        # create a figure
        figure = plt.Figure(figsize=(14, 10), dpi=100)


        # create axes
        axes = figure.add_subplot()


        # create FigureCanvasTkAgg object
        figure_canvas = FigureCanvasTkAgg(figure, master=frame)

        figure_canvas.draw()
        figure_canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        figure_canvas.mpl_connect("pick_event", handlePick)
        figure_canvas.mpl_connect("key_press_event", key_press_handler)

        #tree
        tree = ttk.Treeview(self, columns=("tableName", "patientName", "sensor_location", "situation", "date"))
        
        tree.heading('tableName', text="Saved name", anchor=W)
        tree.heading('patientName', text="Patient", anchor=W)
        tree.heading('sensor_location', text="Sensor location", anchor=W)
        tree.heading('situation', text="Situation", anchor=W)
        tree.heading('date', text="Date", anchor=W)

        tree.column('#0', minwidth=0, width=0)
        tree.column('#1', minwidth=85, width=85)
        tree.column('#2', minwidth=130, width=130)
        tree.column('#3', minwidth=75, width=75)
        tree.column('#4', minwidth=80, width=80)
        tree.column('#5', minwidth=130, width=130)

        #tree.bind('<Motion>', 'break')
        tree.bind('<ButtonRelease-1>', selectedSave)

        #Scrollbar
        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        

        itemsList = getData()
        
        for i in range(0,len(itemsList),5):

            tree.insert('', 'end', values=(itemsList[i], itemsList[i+1], itemsList[i+2], itemsList[i+3], itemsList[i+4]))

        # Placing the elements
        btn_insertData.place(x=230,y=220,width=120,height=40)
        frame.place(x=450,y=0)
        btn_Peaks.place(x=230,y=400,width=120,height=40)
        scrollbar.place(x=532,y=650, height=227)
        tree.place(x=30,y=650)
        lbl_selection.place(x=130,y=450, width=300)
        lbl_selected.place(x=358,y=450)
        btn_compareData.place(x=230,y=500,width=120,height=40)
        btn_compareGait.place(x=230,y=550,width=120,height=40)




if __name__ == '__main__':
    GUI = UI()
    GUI.mainloop()