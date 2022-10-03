import numpy as np
import pandas as pd
from AndriiMSc_Number_of_Peaks import NR_OF_FILES
from calculations import addCols
from scipy.signal import find_peaks
import stumpy
import os
import sys

from scipy.signal import savgol_filter
from matplotlib import pyplot as plt

plt.rcParams["figure.figsize"] = [30,15]
plt.rcParams['xtick.direction'] = 'out'
plt.rcParams["font.size"] = '20'

#upload the data
Ref_path = r'./data'
Ref_files = [sys.argv[1]]
NR_OF_FILES = 1
i = 0
Ref_acceleration = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
NumOfPeaks = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
acceleration = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
time = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
peaks_array_higher = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
peaks_array_lower = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
peaks_array_filtered = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
indx_array = [1,1,1,1,1,1,1,1,1,1]
profile_match_array = [1,1,1,1,1,1,1,1,1,1]
Ref_Acceleration_39 = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
acceleration_39 = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
Resam_Acc = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
Chopped_Acc = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
distance_profile_array = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]


Ref_Location = 'Foot'

def Ref_SavGol_39 (i):
    #applying the Sav_Gol filter
    ACC_filtered = savgol_filter(Ref_df.averagea, 39, 3)
    #the filtered signal is stored into an array
    Ref_Acceleration_39[i] = ACC_filtered
    return Ref_Acceleration_39[i]


for Ref_file in Ref_files:
    if Ref_file.endswith(".txt") : #and Ref_file.startswith(Ref_Location)
        Ref_df = pd.read_csv(Ref_file)
        Ref_df = addCols(Ref_df)
        Ref_df.columns = ['time','stamp','battery', 'pressure','temperature','ax','ay','az','gx','gy','gz','mx','my','mz','averagea']
        Ref_acceleration[i] = Ref_df.averagea
        time[i] = Ref_df.time
        Ref_Acceleration_39[i] = Ref_SavGol_39(i)
        i += 1

#---------------------------------------------------------Motif Definiton---------------------------------------------------#

#ANKLE
#gaitCyclePattern = Ref_Acceleration_39[0][564:942] #single dataset
#SHANK
#gaitCyclePattern = Ref_Acceleration_39[0][556:921] #single dataset
#FOOT
gaitCyclePattern = Ref_Acceleration_39[0][680:820] #single dataset

#---------------------------------------------------------Matrix Profiling-------------------------------------------------------------#

def SavGol_39 (i):
    #applying the Sav_Gol filter
    ACC_filtered = savgol_filter(df.averagea, 39, 3)
    #the filtered signal is stored into an array
    acceleration_39[i] = ACC_filtered
    #time[i] = df.time
    return acceleration_39[i]
def PlotMatch(i):
    plt.plot(acceleration[i], label = 'Filtered data: ' + str(i))
    plt.plot(range(indx_array[i],indx_array[i] + len (gaitCyclePattern)), acceleration[i][indx_array[i]:indx_array[i]+len(gaitCyclePattern)], label = 'Motif', linewidth = 2)
    plt.suptitle('Match in ' + name + "'s dataset number: " + str(i+1), fontsize='30')
    plt.grid(True, 'both')
    plt.legend()
    plt.show()

path = r'./data'
files = [sys.argv[1]]

location = 'S(6'
name = path.split('\\')
name = name[-1]
#Upload the data and apply Sav_Gol filter upon it
i = 0
for file in files:
    if file.endswith(".txt"):
        df = pd.read_csv(file)
        df = addCols(df)
        df.columns = ['time','stamp','battery', 'pressure','temperature','ax','ay','az','gx','gy','gz','mx','my','mz','averagea']
        acceleration[i] = SavGol_39(i)
        i += 1

#Set the threshold based on the location of the sensor
if Ref_Location == 'Ankle':
    y = 13
elif Ref_Location == 'Shank':
    y = 12
elif Ref_Location == 'Foot':
    y = 13

#Run the matrix profiling through all datasets        
i = 0
for i in range (0,NR_OF_FILES):
    distance_profile = stumpy.mass(gaitCyclePattern, acceleration[i])
    distance_profile_array[i] = distance_profile
    indx = np.argmin(distance_profile)
    indx_array[i] = indx
    i += 1

#Chop out the identified Motif similar dataset
i = 0
for i in range(0,NR_OF_FILES):
    profile_match = acceleration[i][indx_array[i]:indx_array[i]+len(gaitCyclePattern)]
    profile_match_array[i] = profile_match
    i += 1

#Find peaks in the identified motif
i = 0
for i in range (0,NR_OF_FILES):
    peaks,_ = find_peaks(profile_match_array[i], height=y)
    peaks_array_filtered[i]=peaks
    NumOfPeaks[i] = len(peaks)
    i+=1
#Plot Motif over Raw data and print Peaks    
i = 0
for i in range (0,NR_OF_FILES):
    PlotMatch(i)
    print('Peaks: ', peaks_array_filtered[i])
    print('Number of Peaks in Profile Match: ', NumOfPeaks[i])
    i += 1

PlotMatch(0)