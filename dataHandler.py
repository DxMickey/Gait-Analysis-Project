import pandas as pd
import os
import sys
from scipy.signal import find_peaks
from scipy.signal import savgol_filter
from matplotlib import pyplot as plt
import matplotlib
from calculations import addCols
from matplotlib.lines import Line2D
from matplotlib.figure import Figure
import numpy as np
from sqlalchemy import create_engine
from sqlite3 import connect

# Input: file path
# Output: pandas dataframe
def readFileIntoDF(tableName):
    cnx = create_engine('sqlite:///oldData.db').connect()
    df = pd.read_sql_table(tableName, cnx)
    df = addCols(df)
    return df


# Input: dataframe column
# Output: filtered data as 1d array
def getFilteredData(array, filterValue):
    return savgol_filter(array, filterValue, 3)


# Input: dataframe column
# Output: 1d array containg indices of the peaks
def getPeaks(array,y):
    peaks, _ = find_peaks(array, height=y)
    return peaks
        
        
class Plotter:
    def __init__(self,data,peaks) -> None:
        self.ctrlPressed = False
        self.peakState = [peaks] #for undo redo
        self.peaks = peaks
        self.data = data
        
        #Make plot
        fig,ax = plt.subplots()
        ax.plot(data)
        ax.plot(self.data[self.peaks],".",markersize=20,picker=True)
        fig.canvas.mpl_connect('pick_event',self.on_pick)
        plt.show()
        plt.draw()
        
                
        #attach event listeners
        # self.figure.canvas.mpl_connect('key_press_event',self.on_press)
        # self.figure.canvas.mpl_connect('key_release_event',self.on_release)
    
        
    def on_press(self,event):
        self.ctrlPressed = True
    def on_release(self,event):
        self.ctrlPressed = False
    def on_pick(self,event):
        if isinstance(event.artist, Line2D):
            ind = event.ind
            self.peaks = np.delete(self.peaks,ind[0])
            self.update()
    def update(self):
        plt.clf()
        plt.plot(self.data)
        plt.plot(self.data[self.peaks],".",markersize=20,picker=True)
        plt.draw()
    def destroyFigure(self):
        plt.clf()
                
                
# Input: dataframe column (x-axis is time)
# Output: plot
# def plot(data, peaks):
    


# main()

