import matplotlib
import os
from matplotlib.patches import Rectangle
import matplotlib.pyplot as plt
from plotter import *
from matplotlib.backend_bases import key_press_handler
from dataHandler import *
from database import connect, additionalDataTable, editAdditionalDataTable, deleteAllSelectedData, createPeaks, returnPeaks,  insertPeaks, getTables, deletePeaks
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime
import tkinter as tk
import tkinter.messagebox as messageBox
from tkinter import W, filedialog, Button, ttk, Menu, WORD, messagebox
import customtkinter
import sqlite3
import math
from USB import getUSBDrive
from tktooltip import ToolTip
from PIL import ImageTk, Image  
import statsmodels.api as stats
from pandas import DataFrame
from errors import *
from tree import *
from peakSelect import *
import stumpy
from automation import *
from matrixprofile import *


matplotlib.use("TkAgg")

# Automatically gets sensor name if it is connected by USB
# Put the name of the file where the sensor ID is here if it changes
sensorIdFileName = "sensorname.txt"

colorList = ["blue", "red", "green", "chocolate", "black", "beige", "indigo", "gold"]
lightColorList = ["lightblue", "salmon", "lightgreen", "brown", "grey", "ivory", "purple", "yellow"]
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
        self.state("zoomed")
        
        self.peakSelector = peakSelect()
        self.currentGraphTitle = ""
        global lastButton
        global selectedItems
        global joinItems1
        global joinItems2
        global deviationMode
        global filesToSave
        deviationMode = "yes"
        
        #remove toolbar from matplotlib graphs
        matplotlib.rcParams['toolbar'] = 'None'


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

        self.bind('<Delete>',lambda event:deleteSaves())
        
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

            global filesToSave

            tk.messagebox.showinfo("Gait analysis",  "Choose file/files to save")
            filesToSave = filedialog.askopenfilenames()
            print(filesToSave)       
           
            if len(filesToSave) > 0:
                additionalData(0)

        def deleteSaves():

            if tk.messagebox.askyesno("Confirmation", "Are you sure that you want to delete currently selected files?"):
            
                for item in selectedItems:
                    deleteAllSelectedData(item)
                                            
                refreshTree()

            


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
            conn = connect("oldData.db")
            cur = conn.cursor()
            try:
                cur.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name=\"{}\";".format(tableName))
                res = cur.fetchall()
                if (1 in res[0]):
                    lblNameError = tk.Label(dataBox, text="That Save name is already used", fg="indian red", bg="lightgray")
                    lblNameError.place(x=125, y=45)
                else:
                    df.to_sql(name=tableName, con=conn, if_exists='fail', index=False)
                    
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
                                [  saveFiles(txtSensorID.get("1.0", "end-1c"), txtTableName.get("1.0", "end-1c"), txtSubjectName.get(
                                          "1.0", "end-1c"), sensorLoc.get(), txtSensorCon.get("1.0", "end-1c"))

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

        def saveFiles(sensorID, tableName, subjectName, sensorLoc, sensorCon):
            global dFrame, fileDate, filesToSave
            
            count = 1
            
            for file in filesToSave:
                print("saving")
                print(count)
                df = pd.read_csv(file)
                df.columns = ['stamp', 'battery', 'pressure', 'temperature',
                            'ax', 'ay', 'az', 'gx', 'gy', 'gz', 'mx', 'my', 'mz']

                dFrame = df
                fileDate = dateAndTime(file)

                if (count == 1):
                    table = tableName
                else:
                    table = tableName + str(count)

                additionalDataTable(sensorID, table, subjectName, sensorLoc, sensorCon, fileDate),
                toSQL(dFrame, table)

                detectGaitCycles(table)

                count += 1
            dataBox.destroy()
            refreshTree()

        def getLocation(table):
            """
            Method for getting saved sensor location from database

            :return: Integer depending on the location, 14, 13 or 16

            """

            conn = connect("oldData.db")
            tableName = str(table) + "_data"
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
            """
            Method returns all data from sqlite database,

            :return: list of data

            """
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

                    if len(saveText) > 3:
                        if count < 3:
                            itemNames += str(i)
                            itemNames += ' & '
                        if count == 3:
                            itemNames += str(i)
                            itemNames += '... '
                    if len(saveText) < 4:
                        itemNames += str(i)
                        if count < len(saveText):
                            itemNames += ' & '

                        
                    count += 1
            else:
                itemNames = saveText
            selectedItems = saveText

            lbl_selected.config(text=itemNames)

        def joinSave1(a):
            """ 
            Get name of selected items in tree1 widget

            """
            global joinItems1

            saveID = tree1.selection()
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
            joinItems1 = saveText



        def joinSave2(a):
            """ 
            Get name of selected items in tree2 widget 

            """
            global joinItems2

            saveID = tree2.selection()
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
            joinItems2 = saveText

        def detectGaitCycles(tableName):
            
            df = readFileIntoDF(tableName)
            
            filterValue = int(lbl_filter_value['text'])
            sensorLocation = getLocation(tableName)

            peaks, filtered_acc, filterValue = automaticPeakFinder(df, filterValue, tableName, sensorLocation)

            self.df = df

            peaks.sort()

            createPeaks(tableName)
            for peak in peaks:
                insertPeaks(tableName, peak)

           

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

        def filterPeaks():

            """
            Method for removing peaks

            """

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

        def matrixPeaks():

            """
            Method for finding peaks and cycles using matrix profiling
            """

            global lastButton, selectedItems
            axes.clear()
            df = readFileIntoDF(selectedItems[0])
            self.df = df

            sensorLocation = int(lbl_filter_value['text'])
            filtered_acc = getFilteredData(df, sensorLocation)

            # This adds the time parameter
            df.insert(len(df.columns), "filtered_acc", filtered_acc)
            filtered_acc = df.filtered_acc
            filtered_acc = np.array(filtered_acc)


            # Define the motif length
            m = 100

           # Compute the matrix profile
            matrix_profile = stumpy.stump(filtered_acc, m)

            # Find the motifs above a certain threshold
            threshold = 1.5
            motif_indices = np.where(matrix_profile[:, 0] < threshold)[0]

            # Compute the maximum value within each motif
            max_values = [np.max(filtered_acc[motif_indices[i]:motif_indices[i] + m]) for i in range(len(motif_indices))]
            max_threshold = 20 # Adjust the threshold as per your data

            # Retain only the motifs whose maximum values exceed the threshold
            filtered_indices = [i for i in range(len(motif_indices)) if max_values[i] > max_threshold]
            filtered_motif_indices = [motif_indices[i] for i in filtered_indices]



            # Plot the time series data
            plt.figure(figsize=(10, 6))
            plt.plot(filtered_acc, color=colorList[0])

            # Highlight the detected motifs
            for index in filtered_motif_indices:
                plt.axvspan(index, index + m, color='lightcoral', alpha=0.3)
            
            plt.xlabel("Time [cs]")
            plt.ylabel("Acceleration [ms^2]")
            plt.title('Detected motifs')

            plt.grid(True, 'both')
            plt.legend()
            plt.show()


            

        def compareGaits():
            """
            Method for comparing different data files

            """
            

            global filtered_acc, lastButton, deviationMode
            axes.clear()
            axes.set_title(lbl_selected['text'])
            noPeaks = []
                
                
            count = 0

            for item in selectedItems:
                peaksList = returnPeaks(item)
                if len(peaksList) == 0:
                    noPeaks.append(item)
            if len(noPeaks) == 0:
                for item in selectedItems:
                    self.df = generateData(item, int(lbl_filter_value['text']))
                    peaksList = returnPeaks(item)

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

            if len(noPeaks) > 0:
                messagebox.showerror("Error", "No peaks saved yet for file/files: {}".format(noPeaks))

            lastButton = "compareGaits"
            btn_resetPeaks.place_forget()
            btn_savePeaks.place_forget()
            btn_help.place_forget()
            lbl_modifyPeaks.place_forget()
            slider_filter.place_forget()
            lbl_filter_value.place_forget()
            lbl_filter.place_forget()
        
        def getAltman():
            """
            Method for showing Bland-Altman plot

            """
            
            if len(selectedItems) == 2:
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
                ax.set_title("{} - {}".format(selectedItems[0], selectedItems[1]))

                stats.graphics.mean_diff_plot(arrayLine1, arrayLine2, ax = ax)

                plt.show()
            else:
                messagebox.showerror("Bland-Altman Error", "Incorrect amount of files selected, make sure to select only 2 files")

        def changeDeviation():
            """
            Method for changing color of btn_EnableDeviation

            """
            global deviationMode, lastButton
            if deviationMode == "yes":
                deviationMode = "no"
                btn_enableDeviation.configure(fg_color= "salmon", hover_color= "salmon", text_color="white")
                
            else:
                deviationMode = "yes"
                btn_enableDeviation.configure(fg_color= "lightgreen", hover_color= "lightgreen", text_color="black")

            if lastButton == "compareGaits":
                compareGaits()
            if lastButton == "getJoined":
                getJoined()

            

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
            refreshTree()
            filterPeaks()

        def joinGaits():
            popup = tk.Toplevel()
            popup.wm_title("Join gaits")
            popup.geometry("1300x450+300+250")
            popup.config(bg="white")
            popup.resizable(False, False)

            global tree1, tree2
            
            tree1 = getTreeWidget(popup,joinSave1,additionalData)
            # Scrollbar
            scrollbar1 = ttk.Scrollbar(popup, orient=tk.VERTICAL, command=tree1.yview)
            tree1.configure(yscroll=scrollbar1.set)

            tree2 = getTreeWidget(popup,joinSave2,additionalData)
            # Scrollbar
            scrollbar2 = ttk.Scrollbar(popup, orient=tk.VERTICAL, command=tree2.yview)
            tree2.configure(yscroll=scrollbar2.set)

            itemsList = getData()
            tablesList = getTables()
            for i in range(0,len(itemsList),6):
                isSaved = "No"
                if (itemsList[i] + "_peaks") in tablesList:
                    isSaved = "Yes"

                tree1.insert('', 'end', values=(itemsList[i], itemsList[i+1], isSaved, itemsList[i+2], itemsList[i+3], itemsList[i+4], itemsList[i+5]))
                tree2.insert('', 'end', values=(itemsList[i], itemsList[i+1], isSaved, itemsList[i+2], itemsList[i+3], itemsList[i+4], itemsList[i+5]))

            lbl_info = tk.Label(
            popup,
            text="Select the gaits you wish to merge and compare",
            bg="white",
            font=("Arial", 14)
        )

            lbl_data1 = tk.Label(
            popup,
            text="Select first set of gaits",
            bg="white",
            font=("Arial", 14)
        )

            lbl_data2 = tk.Label(
            popup,
            text="Select second set of gaits",
            bg="white",
            font=("Arial", 14)
        )

            btn_join = customtkinter.CTkButton(
            popup,
            text="Join gaits",
            command=getJoined

        )
                

            tree1.place(x=60, y=100)
            tree2.place(x=670, y=100)
            btn_join.place(x=580, y=370)
            lbl_info.place(x=56, y=20)
            lbl_data1.place(x=56, y=70)
            lbl_data2.place(x=666, y=70)
            scrollbar1.place(x=620, y=100, height=227)
            scrollbar2.place(x=1230, y=100, height=227)

        def autoPeaks():
            global lastButton, selectedItems
            axes.clear()
            
            df = readFileIntoDF(selectedItems[0])
            

            filterValue = int(lbl_filter_value['text'])
            sensorLocation = getLocation(selectedItems[0])

            peaks, filtered_acc, filterValue = automaticPeakFinder(df, selectedItems[0], filterValue, sensorLocation)
            

            self.df = df

            self.peakSelector.queue = []
            self.peakSelector.current = 0
            self.peakSelector.setPeaks(peaks)
            self.infoStr = self.peakSelector.info

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
     
            

        def getJoined():

            global lastButton, deviationMode, joinItems1, joinItems2
            
            

            axes.clear()

            firstLine = []
            secondLine = []
            noPeaks = []
            
            count = 0
            if len(joinItems1) > 1 and len(joinItems2) > 1:

                for item in joinItems1:
                    peaksList = returnPeaks(item)
                    if len(peaksList) == 0:
                        noPeaks.append(item)
                for item in joinItems2:
                    peaksList = returnPeaks(item)
                    if len(peaksList) == 0:
                        noPeaks.append(item)

                if len(noPeaks) == 0:
                    for item in joinItems1:
                        self.df = generateData(item, int(lbl_filter_value['text']))
                        peaksList = returnPeaks(item)
                        firstTemp = firstLine
                        firstLine = []

                        tempLine = getLineData(peaksList, self.df)
                        if count > 1:
                            firstLine = [t + (word,) for t, word in zip(firstTemp, tempLine)]
                        if count == 1:
                            firstLine = list(zip(firstTemp, tempLine))
                        if count == 0:
                            firstLine = tempLine
                        count += 1

                    firstLine, error1 = averageJoinLine(firstLine)

                    for item in joinItems2:
                        self.df = generateData(item, int(lbl_filter_value['text']))
                        peaksList = returnPeaks(item)

                        tempLine = getLineData(peaksList, self.df)
                        if len(secondLine) > 0:
                            secondLine = list(zip(firstLine, tempLine))
                        else:
                            secondLine = tempLine

                    secondLine, error2 = averageJoinLine(secondLine)

                    plotJoinedGaitCycles(axes,firstLine,colorList[0], lightColorList[0], error1, deviationMode)
                    figure_canvas.draw()
                    
                    plotJoinedGaitCycles(axes,secondLine,colorList[1], lightColorList[1], error2, deviationMode)

                    plotGaitCycleLabels(axes, ["First set of gaits", "Second set of gaits"], colorList, 2)
                    figure_canvas.draw()
                else:
                    messagebox.showerror("Error", "No peaks saved yet for file/files: {}".format(noPeaks))
                
                lastButton = "getJoined"
                
            else:
                messagebox.showerror("Error", "Not enough data selected, select atleast 2 both from both columns")
            

           
            
            
        
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
            self,
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
            text="None(Hold ctrl to select multiple files)",
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

        btn_filterPeaks = customtkinter.CTkButton(
            text="Show filtered peaks",
            command=filterPeaks

        )

        btn_compareGait = customtkinter.CTkButton(
            text="Compare gaits",
            command=compareGaits

        )

        btn_enableDeviation = customtkinter.CTkButton(
            text="Standard deviaton",
            command=changeDeviation,
            fg_color= "lightgreen",
            hover_color= "lightgreen",
            text_color="black"

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

        btn_joinGaits = customtkinter.CTkButton(
            text="Join gaits",
            command=joinGaits

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
                    filterPeaks()
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

        btn_filterPeaks.place(x=230, y=280, width=130, height=40)
        btn_compareGait.place(x=160, y=340, width=130, height=40)
        btn_enableDeviation.place(x=300, y=340, width=130, height=40)
        btn_altman.place(x=230, y=400, width=130, height=40)
        btn_joinGaits.place(x=230, y=600, width=130, height=40)





        ToolTip(btn_insertData, msg="Choose and save a data file to database", delay=0.5)
        ToolTip(btn_Peaks, msg="Show raw data of selected file", delay=0.5)
        ToolTip(btn_filterPeaks, msg="Show and modify saved peaks of data files", delay=0.5)
        ToolTip(btn_compareGait, msg="Compare gait cycles of selected data files", delay=0.5)
        ToolTip(btn_savePeaks, msg="Save selected peaks to database", delay=0.5)
        ToolTip(btn_resetPeaks, msg="Delete peaks of current data file from database and reset to unmodified peaks", delay=0.5)
        ToolTip(slider_filter, msg="Change value of window_length used in Savitzky-Golay filter", delay=0.5)
        ToolTip(tree, msg="Double click to edit file info", delay=0.5)
        ToolTip(btn_altman, msg="Show Bland-Altman plot for selected 2 files", delay=0.5)
        ToolTip(btn_enableDeviation, msg="Turn standard deviation on or off", delay=0.5)
        ToolTip(btn_joinGaits, msg="Join and compare multiple datasets", delay=0.5)
        




if __name__ == '__main__':
    GUI = UI()
    GUI.mainloop()
