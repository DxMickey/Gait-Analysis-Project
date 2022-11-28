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
from statistics import stdev

# Input: file path
# Output: pandas dataframe


def readFileIntoDF(tableName):
    cnx = create_engine('sqlite:///oldData.db').connect()
    df = pd.read_sql_table(str(tableName), cnx)
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
def getShortestGaitCycle(gaitCycles):
    shortest = gaitCycles[0]
    idx = 0
    for i in range(len(gaitCycles)):
        if(len(gaitCycles[i]) < len(shortest)):
            shortest = gaitCycles[i]
            idx = i
    return shortest, idx
def getOtherCycleValues(gaitCycles,ignoreIndex,idx):
    vals = []
    for i in range(len(gaitCycles)):
        if i != ignoreIndex:
            vals.append(gaitCycles[i].iloc[idx]["filtered_acc"])
    return vals
def averageGaitCycles(gaitCycles):
    if(len(gaitCycles) > 0):
        #average out the filtered_acc
        shortest,idx = getShortestGaitCycle(gaitCycles)
        averages = []
        for i in range(len(shortest)):
            vals = getOtherCycleValues(gaitCycles,idx,i)
            currentAcc = shortest.iloc[i]["filtered_acc"]
            for val in vals:
                currentAcc += val
            currentAcc = currentAcc / len(gaitCycles)
            averages.append(currentAcc)
            print(currentAcc)
        shortest["filtered_acc"] = averages
        # gaitCycles.append(shortest) #uncomment this to test alongide the uneaveraged gait cycles
        #return gaitCycles
        return [shortest ] #must return array as the plotting functions expect it
    return gaitCycles

def getGaitCycles(peaks, df):
    arr = []
    for i in range(0, len(peaks), 2):
        if(i + 2 > len(peaks)-1):
            break
        start = peaks[i]
        end = peaks[i+2]
        gaitCycle = df[start:end]
        arr.append(gaitCycle.reset_index())
    arr = normalizeGaitCycles(arr)
    arr = averageGaitCycles(arr)
    return arr


#Modified 2 base functions to get line data for bland-altman


def getLineData(peaks, df):
    arr = []
    for i in range(0, len(peaks), 2):
        if(i + 2 > len(peaks)-1):
            break
        start = peaks[i]
        end = peaks[i+2]
        gaitCycle = df[start:end]
        arr.append(gaitCycle.reset_index())
    arr = normalizeGaitCycles(arr)
    arr = averageGaitCyclesForLineData(arr)
    return arr

def averageGaitCyclesForLineData(gaitCycles):
    if(len(gaitCycles) > 0):
        #average out the filtered_acc
        shortest,idx = getShortestGaitCycle(gaitCycles)
        averages = []
        for i in range(len(shortest)):
            vals = getOtherCycleValues(gaitCycles,idx,i)
            currentAcc = shortest.iloc[i]["filtered_acc"]
            for val in vals:
                currentAcc += val
            currentAcc = currentAcc / len(gaitCycles)
            averages.append(currentAcc)
            print(currentAcc)

    return averages

#Modified base functions to get standard deviation

def getGaitCycleDeviation(peaks, df):
    arr = []
    for i in range(0, len(peaks), 2):
        if(i + 2 > len(peaks)-1):
            break
        start = peaks[i]
        end = peaks[i+2]
        gaitCycle = df[start:end]
        arr.append(gaitCycle.reset_index())
    arr = normalizeGaitCycles(arr)
    arr = getStandardDeviation(arr)
    return arr

def getStandardDeviation(gaitCycles):
    if(len(gaitCycles) > 0):
        deviation = []
        #average out the filtered_acc
        shortest,idx = getShortestGaitCycle(gaitCycles)
        averages = []
        for i in range(len(shortest)):
            vals = getOtherCycleValues(gaitCycles,idx,i)
            currentAcc = shortest.iloc[i]["filtered_acc"]
            values = []
            for val in vals:
                values.append(val)
            deviation.append(stdev(values))


    

    return deviation
    
    
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
def generateData(selectedItem,filterVal):
    df = readFileIntoDF(selectedItem)
    filtered_acc = getFilteredData(df, filterVal)

        # This adds the time parameter
    df.insert(len(df.columns), "filtered_acc", filtered_acc)
    filtered_acc = df.filtered_acc
    return df