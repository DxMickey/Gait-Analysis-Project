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
from database import returnPeaks

# Input: file path
# Output: pandas dataframe


def readFileIntoDF(tableName):
    cnx = create_engine('sqlite:///oldData.db').connect()
    df = pd.read_sql_table(tableName, cnx)
    df = addCols(df)
    return df


# Input: dataframe
# Output: filtered data as 1d array
def getFilteredData(df, filterValue):
    return savgol_filter(df.averagea, filterValue, 3)


# Input: dataframe column
# Output: dataframe rows concerning relevant gait cycles
def getPeaks(item,array, y):
    #Try to get the peaks from DB
    peaks = returnPeaks(item)
    if(len(peaks) > 0):
        return peaks
    
    #If no peaks in DB, calculate them
    peaks, _ = find_peaks(array, height=y)
    return peaks


def getGaitCycles(peaks, df):
    arr = []
    for i in range(0, len(peaks), 2):
        if(i + 2 > len(peaks)-1):
            break
        start = peaks[i]
        end = peaks[i+2]
        gaitCycle = df[start:end]
        arr.append(gaitCycle)
    #add timeStamps to gaitCycles dataframe
    arr = normalizeGaitCycles(arr)
    return arr
    
def normalize(df):
    result = df.copy()
    feature_name = "time"
    max_value = df[feature_name].max()
    min_value = df[feature_name].min()
    result[feature_name] = (df[feature_name] - min_value) / (max_value - min_value)
    return result

def normalizeGaitCycles(gaitCycles):
    normalized = []
    for cycleDf in gaitCycles:
        normalized.append(normalize(cycleDf))
    return normalized
