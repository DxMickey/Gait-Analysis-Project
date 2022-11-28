from plotter import *
from matplotlib.patches import Patch
import matplotlib.patches as mpatches
import numpy as np
from matplotlib.backend_bases import key_press_handler
from calculations import addCols
from baselineFinder import getBaseline
from dataHandler import *
from database import connect, additionalDataTable, editAdditionalDataTable, deleteAllSelectedData, createPeaks, returnPeaks,  insertPeaks, getTables, deletePeaks
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime
from msilib.schema import File
from posixpath import split
from sqlite3 import DatabaseError
import tkinter as tk
import tkinter.messagebox as messageBox
import sqlite3
from tkinter import CENTER, W, filedialog, Button, ttk, Label, Menu, WORD
from turtle import position
from numpy import pad
import time
import math
import win32file
from USB import getUSBDrive
import customtkinter
from tktooltip import ToolTip
from PIL import ImageTk, Image  
import statsmodels.api as stats


from pandas import DataFrame
from pyparsing import col
# import AndriiMSc_Number_of_Peaks as peaks
import os
import pandas as pd

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from errors import *

from tree import *
from peakSelect import *
matplotlib.use("TkAgg")


# Put the name of the sensor ID file here if it changes
sensorIdFileName = "sensorname.txt"
colorList = ["blue", "red", "green", "chocolate", "black"]
lightColorList = ["lightblue", "salmon", "lightgreen", "brown", "grey"]
customtkinter.set_appearance_mode("dark")  # Modes: system (default), light, dark
customtkinter.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green


class UI(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Gait Analysis")
        self.geometry("1920x1080+-7+0")
        self.config(bg="white")
        self.df = None  # the dataframe currently loaded into the window
        # Set the resizable property False
        self.resizable(False, False)
        self.ctrlPressed = False
        self.infoStr = ""
        
        self.peakSelector = peakSelect()
        self.currentGraphTitle = ""
        global lastButton
        global selectedItems
        global peaks
        global deviationMode
        deviationMode = "no"


        # EVENT LISTENERS
        # https://stackoverflow.com/questions/32289175/list-of-all-tkinter-events

        def onKeyPress(e):
            if e.keycode == 17:
                self.ctrlPressed = True
        def onKeyRelease(e):
            if e.keycode == 17:
                self.ctrlPressed = False
           
        def onZ(e):
            if(not self.ctrlPressed):
                return
            self.peakSelector.undo()
            plotAccelerationWithPeaks(axes,self.df.filtered_acc,self.peakSelector.getPeaks(),self.currentGraphTitle)
            figure_canvas.draw()
        def onY(e):
            self.peakSelector.redo()
            plotAccelerationWithPeaks(axes,self.df.filtered_acc,self.peakSelector.getPeaks(),self.currentGraphTitle)
            figure_canvas.draw()
        def handleSetFirstGE():
            self.peakSelector.setGaitEvent(self.lastPeak,"first")
            plotAccelerationWithPeaks(axes,self.df.filtered_acc,self.peakSelector.getPeaks(),self.currentGraphTitle)
            figure_canvas.draw()
            
        def handleSetLastGE():
            self.peakSelector.setGaitEvent(self.lastPeak,"last")
            plotAccelerationWithPeaks(axes,self.df.filtered_acc,self.peakSelector.getPeaks(),self.currentGraphTitle)
            figure_canvas.draw()
            
        def handleDeletePeak():
            self.peakSelector.deletePeak(self.lastPeak)
            plotAccelerationWithPeaks(axes,self.df.filtered_acc,self.peakSelector.getPeaks(),self.currentGraphTitle)
            figure_canvas.draw()
        def handleUndo():
            self.peakSelector.undo()
            plotAccelerationWithPeaks(axes,self.df.filtered_acc,self.peakSelector.getPeaks(),self.currentGraphTitle)
            figure_canvas.draw()
        def handleRedo():
            self.peakSelector.redo()
            plotAccelerationWithPeaks(axes,self.df.filtered_acc,self.peakSelector.getPeaks(),self.currentGraphTitle)
            figure_canvas.draw()
            
        self.bind("<Key>", onKeyPress)
        self.bind("<KeyRelease>", onKeyRelease)
        self.bind("<z>",onZ)
        self.bind("<y>",onY)
        
        self.lastPeak = -1
        
        m = Menu(self, tearoff = 0)
        m.add_command(label ="Set first gait event",command=handleSetFirstGE)
        m.add_command(label ="Set last gait event",command=handleSetLastGE)
        m.add_command(label ="Remove peak",command=handleDeletePeak)
        m.add_separator()
        m.add_command(label ="Undo (CTRL + Z)", command=handleUndo)
        m.add_command(label ="Redo (CTRL + Y)",command=handleRedo)
        
        def do_popup(event):
            try:
                m.tk_popup(event.x_root, event.y_root)
            finally:
                m.grab_release()
        
        # self.bind("<Button-3>", do_popup)
        
        # /EVENT LISTENERS

        def insertData(event):
            """ 
            User chooses which file to save data from

            """

            tk.messagebox.showinfo("Gait analysis",  "Choose file to save")
            global dFrame, fileDate
            file = filedialog.askopenfilename()
            df = pd.read_csv(file)
            df.columns = ['stamp', 'battery', 'pressure', 'temperature',
                          'ax', 'ay', 'az', 'gx', 'gy', 'gz', 'mx', 'my', 'mz']

            dFrame = df
            fileDate = dateAndTime(file)
            additionalData(0)
            self.df = df


        def getDataTables():
            """
            Method returns all table names from sqlite database, that have _data in their name

            :return: list of table names

            """

            tablesList = []
            tablesFiltered = []
            conn = connect("oldData.db")
            try:
                res = conn.execute("SELECT name FROM sqlite_master WHERE type='table';")
                for name in res.fetchall():
                    tablesList.append(name[0])
                conn.close()
            except sqlite3.Error as e:
                messageBox.showerror("getDataTables", e)
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
            try:
                df.to_sql(name=fName, con=conn, if_exists='replace', index=False)
                conn.close()
            except sqlite3.Error as e:
                messageBox.showerror("toSQL", e)
            refreshTree()

        def refreshTree():
            """ 
            Refreshes items in tree widget by deleting everything and loading new items from database

            """

            tree.delete(*tree.get_children())
            itemsList = getData()
            tablesList = getTables()
            for i in range(0,len(itemsList),6):
                isSaved = "No"
                if (itemsList[i] + "_peaks") in tablesList:
                    isSaved = "Yes"

                tree.insert('', 'end', values=(itemsList[i], itemsList[i+1], isSaved, itemsList[i+2], itemsList[i+3], itemsList[i+4], itemsList[i+5]))

        def additionalData(event):
            global dataBox
            save = 0
            if (event == 0):
                save = 1
                dictionary = ["", "", "", "", "", ""]
            else:
                saveID = tree.focus()
                saveDict = tree.item(saveID)
                dictionary = [] * 6
                for i in range(0, len(saveDict['values'])):
                    if i != 2:
                        dictionary.append(saveDict['values'][i])
                originalName = dictionary[0]

            dataBox = tk.Tk()
            dataBox.title("Additional data")
            dataBox.geometry("300x425+800+400")
            dataBox.config(bg="lightgray")

            lblTableName = tk.Label(dataBox, text="Save name:")
            lblTableName.grid(row=1, column=1, padx=25, pady=25)
            txtTableName = tk.Text(dataBox, height=1, width=20)
            txtTableName.insert(1.0, dictionary[0])
            txtTableName.grid(row=1, column=2)

            lblSensorID = tk.Label(dataBox, text="Sensor ID:")
            lblSensorID.grid(row=2, column=1)
            txtSensorID = tk.Text(dataBox, height=1, width=20)
            if (save == 1):
                sensorId = getSensorId()
            else:
                sensorId = dictionary[1]
            txtSensorID.insert(1.0, sensorId)
            txtSensorID.grid(row=2, column=2)

            lblSubjectName = tk.Label(dataBox, text="Subject name:")
            lblSubjectName.grid(row=3, column=1, padx=25, pady=25)
            txtSubjectName = tk.Text(dataBox, height=1, width=20)
            txtSubjectName.insert(1.0, dictionary[2])
            txtSubjectName.grid(row=3, column=2)

            lblSensorLoc = tk.Label(dataBox, text="Sensor location:")
            lblSensorLoc.grid(row=4, column=1)

            sensorLoc = tk.StringVar(dataBox, "")
            rdSL1 = tk.Radiobutton(
                dataBox, text="Ankle", variable=sensorLoc, value="Ankle", tristatevalue="x")
            rdSL1.grid(row=4, column=2)
            rdSL2 = tk.Radiobutton(
                dataBox, text="Foot", variable=sensorLoc, value="Foot", tristatevalue="x")
            rdSL2.grid(row=5, column=2, pady=25)
            rdSL3 = tk.Radiobutton(
                dataBox, text="Shank", variable=sensorLoc, value="Shank", tristatevalue="x")
            rdSL3.grid(row=6, column=2)
            sensorLoc.set(dictionary[3])

            lblSensorCon = tk.Label(dataBox, text="Sensor condition:")
            lblSensorCon.grid(row=7, column=1, pady=25)
            txtSensorCon = tk.Text(dataBox, height=1, width=20)
            txtSensorCon.grid(row=7, column=2)
            txtSensorCon.insert(1.0, dictionary[4])

            if(save == 1):
                btn_save = Button(dataBox, text="SAVE", command=lambda:
                                  [
                                      additionalDataTable(txtSensorID.get("1.0", "end-1c"), txtTableName.get("1.0", "end-1c"), txtSubjectName.get(
                                          "1.0", "end-1c"), sensorLoc.get(), txtSensorCon.get("1.0", "end-1c"), fileDate),
                                      toSQL(dFrame, txtTableName.get(
                                          "1.0", "end-1c"))
                                  ])
                btn_save.grid(row=8, column=2, pady=25)
            else:
                btn_edit = Button(dataBox, text="EDIT", command=lambda:
                                  [
                                      editAdditionalDataTable(txtSensorID.get("1.0", "end-1c"), txtTableName.get("1.0", "end-1c"), txtSubjectName.get(
                                          "1.0", "end-1c"), sensorLoc.get(), txtSensorCon.get("1.0", "end-1c"), originalName),
                                      refreshTree(),
                                      dataBox.destroy()
                                  ])
                btn_delete = Button(dataBox, text="DELETE DATA", fg="red", command=lambda:
                                    [
                                        deleteAllSelectedData(originalName),
                                        refreshTree(),
                                        dataBox.destroy()
                                    ])
                btn_delete.grid(row=8, column=2, pady=25)
                btn_edit.grid(row=8, column=1, pady=25)

        def getLocation(table):
            """
            Method for getting saved sensor location from database

            :return: Integer depending on the location, 14, 13 or 16

            """

            conn = connect("oldData.db")
            tableName = table + "_data"
            try:
                res = conn.execute("SELECT \"Sensor location\" FROM \"{}\";".format(tableName))
                location = res.fetchone()
                conn.close()
            except sqlite3.Error as e:
                messageBox.showerror("getLocation", e)
          
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
            try:
                for table in tableList:
                    res = conn.execute("SELECT * FROM \"{}\";".format(table))
                    for data in res.fetchall():
                        dataList.append(table.replace('_data', ''))
                        dataList.append(data[0])
                        dataList.append(data[1])
                        dataList.append(data[2])
                        dataList.append(data[3])
                        dataList.append(data[4])
                conn.close()
            except sqlite3.Error as e:
                messageBox.showerror("getData", e)
            return dataList

        def selectedSave(a):
            """ 
            Get name of selected item in tree widget and change lbl_selected text into the name

            """
            global selectedItems

            saveID = tree.selection()
            saveText = []
            itemNames = ''
            for i in saveID:
                saveText.append(tree.item(i)['values'][0])

            if len(saveText) > 1:
                count = 1
                for i in saveText:
                    itemNames += str(i)
                    if count < len(saveText):
                        itemNames += ' & '
                    count += 1
            else:
                itemNames = saveText
            selectedItems = saveText

            lbl_selected.config(text=itemNames)

        def findPeaks():
            """
            Method for plotting out the graph with analysed data from peaks.main function

            """
            global lastButton
            
            df = readFileIntoDF(lbl_selected['text'])
            self.df = df
            if DFIsEmpty(self.df):
                return
            
            
            unfiltered_acc = df.averagea
            filtered_acc = getFilteredData(df, int(lbl_filter_value['text']))

            # This adds the time parameter
            df.insert(len(df.columns), "filtered_acc", filtered_acc)
            filtered_acc = df.filtered_acc

            # Get peaks in filtered data
            # peaks = getPeaks(filtered_acc, getLocation(lbl_selected['text']))
            # filtered_acc = df.filtered_acc

            
            plotRawData(axes,df)
            axes.set_title(lbl_selected['text'])
            
            figure_canvas.draw()
            lastButton = "findPeaks"
            btn_resetPeaks.place_forget()
            btn_savePeaks.place_forget()
            btn_help.place_forget()
            lbl_modifyPeaks.place_forget()
            slider_filter.place_forget()
            lbl_filter_value.place_forget()
            lbl_filter.place_forget()

        def compareData():

            global lastButton, selectedItems
            axes.clear()
            df = readFileIntoDF(selectedItems[0])
           
            self.df = df
           
            sensorLocation = int(lbl_filter_value['text'])
            filtered_acc = getFilteredData(df, sensorLocation)

            # This adds the time parameter
            df.insert(len(df.columns), "filtered_acc", filtered_acc)
            filtered_acc = df.filtered_acc

            peaks = getPeaks(
                selectedItems[0], filtered_acc, getLocation(selectedItems[0]))
            self.peakSelector.queue = []
            self.peakSelector.current = 0
            self.peakSelector.setPeaks(peaks)
            self.infoStr = self.peakSelector.info

            filtered_acc = df.filtered_acc
            self.currentGraphTitle = lbl_selected['text']
            plotAccelerationWithPeaks(axes, filtered_acc, peaks,self.currentGraphTitle)
            
            figure_canvas.draw()
            lastButton = "compareData"
            btn_savePeaks.place(x=140, y=540, width=90, height=40)
            btn_resetPeaks.place(x=250, y=540, width=90, height=40)
            btn_help.place(x=360, y=540, width=90, height=40)
            lbl_modifyPeaks.place(x=134, y=505)
            slider_filter.place(x=200, y=475, width=200, height=25)
            lbl_filter.place(x=245, y=450)
            lbl_filter_value.place(x=329, y=450)
            

        def compareGaits():

            global filtered_acc, lastButton, deviationMode
            axes.clear()
            axes.set_title(lbl_selected['text'])
                
                
            count = 0

            for item in selectedItems:
                self.df = generateData(item, int(lbl_filter_value['text']))
                peaksList = returnPeaks(item)

                print("DEBUG DEBUG DEBUG")
                print(deviationMode)

                gaitCycles = getGaitCycles(peaksList, self.df)
                if deviationMode == "yes":
                    error = getGaitCycleDeviation(peaksList, self.df)
                else:
                    error = None
                plotGaitCycles(axes,gaitCycles,colorList[count], lightColorList[count], error, deviationMode)

                
                figure_canvas.draw()
                count += 1

            plotGaitCycleLabels(axes,selectedItems,colorList,count)
            figure_canvas.draw()

            lastButton = "compareGaits"
            btn_resetPeaks.place_forget()
            btn_savePeaks.place_forget()
            btn_help.place_forget()
            lbl_modifyPeaks.place_forget()
            slider_filter.place_forget()
            lbl_filter_value.place_forget()
            lbl_filter.place_forget()
        
        def getAltman():
       
            self.df = generateData(selectedItems[0], int(lbl_filter_value['text']))
            peaksList = returnPeaks(selectedItems[0])

            line1 = getLineData(peaksList, self.df)

            self.df = generateData(selectedItems[1], int(lbl_filter_value['text']))
            peaksList = returnPeaks(selectedItems[1])

            line2 = getLineData(peaksList, self.df)

            if len(line1) > len(line2):
                size = len(line2)
            else:
                size = len(line1)

            filteredLine1 = []
            filteredLine2 = []

            for i in range (0, size):
                filteredLine1.append(line1[i])
                filteredLine2.append(line2[i])

            arrayLine1 = np.array(filteredLine1)
            arrayLine2 = np.array(filteredLine2)

            f, ax = plt.subplots(1, figsize = (8,5))

            stats.graphics.mean_diff_plot(arrayLine1, arrayLine2, ax = ax)

            plt.show()

        def changeDeviation():
            global deviationMode
            if deviationMode == "yes":
                deviationMode = "no"
                btn_enableDeviation.configure(fg_color= "salmon", hover_color= "salmon", text_color="white")
                
            else:
                deviationMode = "yes"
                btn_enableDeviation.configure(fg_color= "lightgreen", hover_color= "lightgreen", text_color="black")

            
            compareGaits()

            

        def handlePick(event):
            self.lastPeak = event.ind[0]
            cmd = do_popup(event.guiEvent)
            filtered_acc = self.df.filtered_acc
            peaks = self.peakSelector.getPeaks()
            plotAccelerationWithPeaks(axes,filtered_acc,peaks)

            figure_canvas.draw()
           

        def getSensorId():
            tester = getUSBDrive(sensorIdFileName)
            if (tester != None):
                sensorId = tester
            else:
                sensorId = "Unknown"
            return sensorId

        def savePeaks():
            global selectedItems
            createPeaks(selectedItems[0])
            peaks = self.peakSelector.peaks
            for peak in peaks:
                insertPeaks(selectedItems[0], peak)
            refreshTree()

        def resetPeaks():
            global selectedItems
            deletePeaks(selectedItems[0])
            print(selectedItems[0])
            refreshTree()
            compareData()
        
        def help():
            
            popup = tk.Toplevel()
            popup.wm_title("Help window")
            popup.geometry("800x900+600+100")
            popup.config(bg="white")
            popup.resizable(False, False)

            path = ".\helpImage.png"
            image1 = Image.open(path)
            image1 = image1.resize((780, 530))
            image1 = ImageTk.PhotoImage(image1)
    
            lbl_panel = tk.Label(
                popup, 
                image = image1)
            
            lbl_header = tk.Label(
            popup,
            text="Steps:",
            bg="white",
            font=("Arial", 14)
        )

            lbl_example = tk.Label(
            popup,
            text="N.B. Remember that a gait cycle is defined from a Heel-strike to the following\nHeel-strike. Be sure to select a finite number of cycles as shown in figure:",
            bg="white",
            font=("Arial", 14)
        )
            

            textbox = customtkinter.CTkTextbox(popup, fg_color="white", text_color="black", wrap=WORD, width=700, height=180)
            textbox.insert("0.0", "1) Select the first gait event by clicking on the correct peak marker and choose \"Set first gait event\"\n\n"
            "2) Select the last gait event by clicking on the correct peak marker and choose \"Set last gait event\"\n\n"
            "3) All the peaks from before first and after last gait event will automatically be removed, if there are any peaks that you want to remove manually, select the wanted peak and choose \"Remove peak\"\n\n"
            "4) You are also able to undo and redo actions by pressing CTRL+Z or CTRL+Y\n\n"
            "5) Once selecting peaks is done, click on \"Save peaks\" button to save selected peaks to database or click on \"Reset peaks\" if you want the unmodified peaks back")
            
            lbl_header.place(x=20, y=10)
            textbox.place(x=20, y=40)
            lbl_example.place(x=10, y=235)
            lbl_panel.place(x=10, y=290)



            popup.mainloop()

        btn_insertData = customtkinter.CTkButton(
            text="Save new data",

            command=lambda: insertData(0)

        )

        btn_Peaks = customtkinter.CTkButton(
            text="Show raw data",
            command=findPeaks

        )

        lbl_selection = tk.Label(
            text="Selected:",
            bg="white",
            font=("Arial", 15)
        )

        lbl_selected = tk.Label(
            text="None",
            bg="white",
            font=("Arial", 15),
            anchor=W
        )

        lbl_modifyPeaks = tk.Label(
            text="Available options for modifying peaks",
            bg="white",
            font=("Arial", 14),
            anchor=W
        )

        btn_compareData = customtkinter.CTkButton(
            text="Show filtered peaks",
            command=compareData

        )

        btn_compareGait = customtkinter.CTkButton(
            text="Compare gaits",
            command=compareGaits

        )

        btn_enableDeviation = customtkinter.CTkButton(
            text="Standard Deviaton",
            command=changeDeviation,
            fg_color= "salmon",
            hover_color= "salmon",
            text_color="white"

        )

        btn_altman = customtkinter.CTkButton(
            text="Show Bland-Altman",
            command=getAltman

        )

        lbl_filter = tk.Label(
            text="Filter value:",
            bg="white",
            font=("Arial", 13)
        )

        lbl_filter_value = tk.Label(
            text="39",
            bg="white",
            font=("Arial", 14)
        )
        btn_savePeaks = customtkinter.CTkButton(
            text="Save peaks",
            command=savePeaks

        )

        btn_resetPeaks = customtkinter.CTkButton(
            text="Reset peaks",
            command=resetPeaks

        )

        btn_help = customtkinter.CTkButton(
            text="Help",
            command=help

        )

        def slider_changed(val):
            """ 
            Check if any button was pressed before and update lbl_filter to new slider value

            """

            global lastButton
            lbl_filter_value.config(text=(math.floor(slider_filter.get())))

            if(lastButton == "compareGaits"):
                return
            match lastButton:
                case 'findPeaks':
                    findPeaks()
                case 'compareData':
                    compareData()
                case 'compareGaits':
                    compareGaits()

        current_value = tk.IntVar()

        slider_filter = customtkinter.CTkSlider(
            from_=0,
            to=100,
            orient='horizontal',
            command=slider_changed,
            variable=current_value
        )

        slider_filter.set(39)

        frame = tk.Frame(self)
        

        # create a figure
        figure = plt.Figure(figsize=(16, 11), dpi=100)

        # create axes
        axes = figure.add_subplot()

        # create FigureCanvasTkAgg object
        figure_canvas = FigureCanvasTkAgg(figure, master=frame)

        figure_canvas.draw()
        figure_canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        figure_canvas.mpl_connect("pick_event", handlePick)
        figure_canvas.mpl_connect("key_press_event", key_press_handler)

        

        tree = getTreeWidget(self,selectedSave,additionalData)
        # Scrollbar
        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)

        itemsList = getData()
        tablesList = getTables()
        for i in range(0,len(itemsList),6):
            isSaved = "No"
            if (itemsList[i] + "_peaks") in tablesList:
                isSaved = "Yes"

            tree.insert('', 'end', values=(itemsList[i], itemsList[i+1], isSaved, itemsList[i+2], itemsList[i+3], itemsList[i+4], itemsList[i+5]))

        # Placing the elements
        btn_insertData.place(x=230, y=130, width=130, height=40)
        frame.place(x=450, y=0)
        btn_Peaks.place(x=230, y=220, width=130, height=40)
        scrollbar.place(x=580, y=800, height=230)
        tree.place(x=10, y=800, width= 570, height= 230)

        lbl_selection.place(x=5, y=770)
        lbl_selected.place(x=93, y=770)

        btn_compareData.place(x=230, y=280, width=130, height=40)
        btn_compareGait.place(x=170, y=340, width=130, height=40)
        btn_enableDeviation.place(x=310, y=340, width=130, height=40)
        btn_altman.place(x=230, y=400, width=130, height=40)




        ToolTip(btn_insertData, msg="Choose and save a data file to database", delay=0.5)
        ToolTip(btn_Peaks, msg="Show raw data of selected files", delay=0.5)
        ToolTip(btn_compareData, msg="Show and modify saved peaks of data files", delay=0.5)
        ToolTip(btn_compareGait, msg="Compare gait cycles of selected data files", delay=0.5)
        ToolTip(btn_savePeaks, msg="Save selected peaks to database", delay=0.5)
        ToolTip(btn_resetPeaks, msg="Delete peaks of current data file from database and reset to unmodified peaks", delay=0.5)
        ToolTip(slider_filter, msg="Change value of window_length used in Savitzky-Golay filter", delay=0.5)
        




if __name__ == '__main__':
    GUI = UI()
    GUI.mainloop()
