import numpy as np
import pandas as pd
from scipy.signal import savgol_filter
from scipy.signal import find_peaks
import os
from matplotlib import pyplot as plt

plt.rcParams["figure.figsize"] = [30,15]
plt.rcParams['xtick.direction'] = 'out'
plt.rcParams["font.size"] = '15'

acceleration = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
acceleration_9 = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
acceleration_19 = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
acceleration_29 = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
acceleration_39 = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
acceleration_49 = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
acceleration_59 = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
acceleration_69 = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
time = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
time_9 = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
time_19 = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
time_29 = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
time_39 = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
time_49 = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
time_59 = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
time_69 = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]

peaks_array = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
_array = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
ankle_resample_array = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
#CV_Results = [1,1,1,1,1]
indx_array = [1,1,1,1,1,1,1,1,1,1]
profile_match_array = [1,1,1,1,1,1,1,1,1,1]
peak_results = [1,1,1,1,1,1,1,1]
path = r''
files = os.listdir(path)

#function that applies SavitzkyGolay filter and returns an array with filtered acceleration
def SavGol_9 (x):
    #applying the Sav_Gol filter
    ACC_filtered = savgol_filter(df.averagea, 9, 3)
    #the filtered signal is stored into an array
    acceleration_9[i] = ACC_filtered
    time[i] = df.time
    return acceleration_9[i]

def SavGol_19 (x):
    #applying the Sav_Gol filter
    ACC_filtered = savgol_filter(df.averagea, 19, 3)
    #the filtered signal is stored into an array
    acceleration_19[i] = ACC_filtered
    time[i] = df.time
    return acceleration_19[i]

def SavGol_29 (x):
    #applying the Sav_Gol filter
    ACC_filtered = savgol_filter(df.averagea, 29, 3)
    #the filtered signal is stored into an array
    acceleration_29[i] = ACC_filtered
    time[i] = df.time
    return acceleration_29[i]

def SavGol_39 (x):
    #applying the Sav_Gol filter
    ACC_filtered = savgol_filter(df.averagea,39, 3)
    #the filtered signal is stored into an array
    acceleration_39[i] = ACC_filtered
    time[i] = df.time
    return acceleration_39[i]

def SavGol_49 (x):
    #applying the Sav_Gol filter
    ACC_filtered = savgol_filter(df.averagea, 49, 3)
    #the filtered signal is stored into an array
    acceleration_49[i] = ACC_filtered
    time[i] = df.time
    return acceleration_49[i]

def SavGol_59 (x):
    #applying the Sav_Gol filter
    ACC_filtered = savgol_filter(df.averagea, 59, 3)
    #the filtered signal is stored into an array
    acceleration_59[i] = ACC_filtered
    time[i] = df.time
    return acceleration_59[i]

def SavGol_69 (x):
    #applying the Sav_Gol filter
    ACC_filtered = savgol_filter(df.averagea, 69, 3)
    #the filtered signal is stored into an array
    acceleration_69[i] = ACC_filtered
    time[i] = df.time
    return acceleration_69[i]

i = 0
print(i)
SubjectName = 'Subject 1'
y = 'Shank'
#uploading the files and storing them to arrays
for file in files:
    if file.startswith(y) and file.endswith(".xlsx"):
        df = pd.read_excel(os.path.join(path, file))
        df.columns = ['time','stamp','battery', 'pressure','temperature','ax','ay','az','gx','gy','gz','mx','my','mz','averagea']
        acceleration_9[i] = SavGol_9(df.averagea)
        time_9[i] = df.time
        acceleration[i] = df.averagea   
    if file.endswith(".xlsx") and file.startswith(y):
        df = pd.read_excel(os.path.join(path, file))
        df.columns = ['time','stamp','battery', 'pressure','temperature','ax','ay','az','gx','gy','gz','mx','my','mz','averagea']
        acceleration_19[i] = SavGol_19(df.averagea)
        time_19[i] = df.time
        
    if file.endswith(".xlsx") and file.startswith(y):
        df = pd.read_excel(os.path.join(path, file))
        df.columns = ['time','stamp','battery', 'pressure','temperature','ax','ay','az','gx','gy','gz','mx','my','mz','averagea']
        acceleration_29[i] = SavGol_29(df.averagea)
        time_29[i] = df.time

    if file.endswith(".xlsx") and file.startswith(y):
        df = pd.read_excel(os.path.join(path, file))
        df.columns = ['time','stamp','battery', 'pressure','temperature','ax','ay','az','gx','gy','gz','mx','my','mz','averagea']
        acceleration_39[i] = SavGol_39(df.averagea)
        time_39[i] = df.time
                  
    if file.endswith(".xlsx") and file.startswith(y):
        df = pd.read_excel(os.path.join(path, file))
        df.columns = ['time','stamp','battery', 'pressure','temperature','ax','ay','az','gx','gy','gz','mx','my','mz','averagea']
        acceleration_49[i] = SavGol_49(df.averagea)
        time_49[i] = df.time
        
    if file.endswith(".xlsx") and file.startswith(y):
        df = pd.read_excel(os.path.join(path, file))
        df.columns = ['time','stamp','battery', 'pressure','temperature','ax','ay','az','gx','gy','gz','mx','my','mz','averagea']
        acceleration_59[i] = SavGol_59(df.averagea)
        time_59[i] = df.time
        
    if file.endswith(".xlsx") and file.startswith(y):
        df = pd.read_excel(os.path.join(path, file))
        df.columns = ['time','stamp','battery', 'pressure','temperature','ax','ay','az','gx','gy','gz','mx','my','mz','averagea']
        acceleration_69[i] = SavGol_69(df.averagea)
        time_69[i] = df.time
        i += 1
    
 
i = 0

for i in range (0, 5):
    plt.plot(time[i], acceleration[i], label = 'raw')
    plt.plot(time[i],acceleration_9[i], label = '9')
    plt.plot(time[i],acceleration_19[i], label = '19')
    plt.plot(time[i],acceleration_29[i], label = '29')
    plt.plot(time[i],acceleration_39[i], label = '39')
    plt.plot(time[i],acceleration_49[i], label = '49')
    plt.plot(time[i],acceleration_59[i], label = '59')
    plt.plot(time[i],acceleration_69[i], label = '69')
    plt.grid(True, 'both')
    plt.suptitle(str(y) + '_' + str(SubjectName) + " " + str(i), fontsize='30')
    plt.legend()
    plt.show()

#function that finds peaks in data with various window lengths
def Peaks(i, start, end):
    peaks_raw = find_peaks(acceleration[i][start:end], height=11)
    peak_occurences = peaks_raw[0] #occurence of the peak in time frame
    peak_values = peaks_raw[1]["peak_heights"] #numerical value of the peak
    peak_index = np.where(peak_values == max(peak_values)) #index of the occurence of the highest peak in time frame array
    result = int(peak_occurences[peak_index]) #getting the actual value of the highest peak occurence
    
    peaks_9 = find_peaks(acceleration_9[i][start:end], height=11)
    peak_occurences_9 = peaks_9[0] #occurence of the peak in time frame
    peak_values_9 = peaks_9[1]["peak_heights"] #numerical value of the peak
    peak_index_9 = np.where(peak_values_9== max(peak_values_9)) ##index of the occurence of the highest peak in time frame array
    result_9 = int(peak_occurences_9[peak_index_9]) #getting the actual value of the highest peak occurence
    
    peaks_19 = find_peaks(acceleration_19[i][start:end], height=11)
    peak_occurences_19 = peaks_19[0] #occurence of the peak in time frame
    peak_values_19 = peaks_19[1]["peak_heights"] #numerical value of the peak
    peak_index_19 = np.where(peak_values_19 == max(peak_values_19)) ##index of the occurence of the highest peak in time frame array
    result_19 = int(peak_occurences_19[peak_index_19]) #getting the actual value of the highest peak occurence
    
    peaks_29 = find_peaks(acceleration_29[i][start:end], height=11)
    peak_occurences_29 = peaks_29[0] #occurence of the peak in time frame
    peak_values_29 = peaks_29[1]["peak_heights"] #numerical value of the peak
    peak_index_29 = np.where(peak_values_29 == max(peak_values_29)) ##index of the occurence of the highest peak in time frame array
    result_29 = int(peak_occurences_29[peak_index_29]) #getting the actual value of the highest peak occurence
    
    peaks_39 = find_peaks(acceleration_39[i][start:end], height=11)
    peak_occurences_39 = peaks_39[0] #occurence of the peak in time frame
    peak_values_39 = peaks_39[1]["peak_heights"] #numerical value of the peak
    peak_index_39 = np.where(peak_values_39 == max(peak_values_39)) ##index of the occurence of the highest peak in time frame array
    result_39 = int(peak_occurences_39[peak_index_39]) #getting the actual value of the highest peak occurence
    
    peaks_49 = find_peaks(acceleration_49[i][start:end], height=11)
    peak_occurences_49 = peaks_49[0] #occurence of the peak in time frame
    peak_values_49 = peaks_49[1]["peak_heights"] #numerical value of the peak
    peak_index_49 = np.where(peak_values_49 == max(peak_values_49)) ##index of the occurence of the highest peak in time frame array
    result_49 = int(peak_occurences_49[peak_index_49]) #getting the actual value of the highest peak occurence
    
    peaks_59 = find_peaks(acceleration_59[i][start:end], height=11)
    peak_occurences_59 = peaks_59[0] #occurence of the peak in time frame
    peak_values_59 = peaks_59[1]["peak_heights"] #numerical value of the peak
    peak_index_59 = np.where(peak_values_59 == max(peak_values_59)) ##index of the occurence of the highest peak in time frame array
    result_59 = int(peak_occurences_59[peak_index_59]) #getting the actual value of the highest peak occurence
    
    peaks_69 = find_peaks(acceleration_69[i][start:end], height=11)
    peak_occurences_69 = peaks_69[0] #occurence of the peak in time frame
    peak_values_69 = peaks_69[1]["peak_heights"] #numerical value of the peak
    peak_index_69 = np.where(peak_values_69 == max(peak_values_69)) ##index of the occurence of the highest peak in time frame array
    result_69 = int(peak_occurences_69[peak_index_69]) #getting the actual value of the highest peak occurence 
    #finding the difference of the peak occurences between filtered and raw data
    all_results = [result-result_9, result-result_19,result-result_29, result-result_39, result-result_49, result-result_59, result-result_69]
    return all_results

i = 0
#plotting the certain part of the dataset, limit is defined by the end1 variable
def ShiftCheck (i,end1):
    plt.plot(acceleration[i][:end1], label = 'raw')
    plt.plot(acceleration_9[i][:end1], label = '9')
    plt.plot(acceleration_19[i][:end1], label = '19')
    plt.plot(acceleration_29[i][:end1], label = '29')
    plt.plot(acceleration_39[i][:end1], label = '39')
    plt.plot(acceleration_49[i][:end1], label = '49')
    plt.plot(acceleration_59[i][:end1], label = '59')
    plt.plot(acceleration_69[i][:end1], label = '69')
    plt.legend()
    plt.grid(True, 'both')
    return plt.show()

#plottring a single dataset with raw data and all the window lengths
def SingleGraph (i):
    plt.plot(time[i], acceleration[i], label = 'raw', lw = 3)
    plt.plot(time[i],acceleration_9[i], label = '9')
    plt.plot(time[i],acceleration_19[i], label = '19')
    plt.plot(time[i],acceleration_29[i], label = '29')
    plt.plot(time[i],acceleration_39[i], label = '39')
    plt.plot(time[i],acceleration_49[i], label = '49')
    plt.plot(time[i],acceleration_59[i], label = '59')
    plt.plot(time[i],acceleration_69[i], label = '69')
    plt.grid(True, 'both')
    plt.suptitle(str(y) + '_' + str(SubjectName) + " " + str(i), fontsize='30')
    plt.legend()
    return plt.show()

