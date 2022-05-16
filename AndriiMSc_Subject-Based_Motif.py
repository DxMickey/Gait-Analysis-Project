import numpy as np
import pandas as pd
from scipy.signal import find_peaks
import stumpy
import os

from scipy.signal import savgol_filter
from matplotlib import pyplot as plt


plt.rcParams["figure.figsize"] = [30,15]
plt.rcParams['xtick.direction'] = 'out'
plt.rcParams["font.size"] = '20'

#upload the data
Ref_path = r''
Ref_files = os.listdir(Ref_path)

i = 0
Ref_acceleration = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
acceleration = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
NumOfPeaks = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
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

Ref_Location = 'Ankle'
location = Ref_Location
name = "Subject 1"

#SavGol funciton to define reference matrix
def Ref_SavGol_39 (i):
    #applying the Sav_Gol filter
    ACC_filtered = savgol_filter(Ref_df.averagea, 39, 3)
    #the filtered signal is stored into an array
    Ref_Acceleration_39[i] = ACC_filtered
    return Ref_Acceleration_39[i]

#upload the data into Python environment
for Ref_file in Ref_files:
    if Ref_file.endswith(".xlsx") and Ref_file.startswith(Ref_Location):
        Ref_df = pd.read_excel(os.path.join(Ref_path, Ref_file))
        Ref_df.columns = ['time','stamp','battery', 'pressure','temperature','ax','ay','az','gx','gy','gz','mx','my','mz','averagea']
        Ref_acceleration[i] = Ref_df.averagea
        time[i] = Ref_df.time
        Ref_Acceleration_39[i] = Ref_SavGol_39(i)
        i += 1

#set the threshold based on the location of the sensor
if Ref_Location == 'Ankle':
    y = 13
elif Ref_Location == 'Shank':
    y = 12
elif Ref_Location == 'Foot':
    y = 13

#find peaks in filtered data
peaks,_ = find_peaks(Ref_Acceleration_39[0], height=y)
peaks_array_filtered[11]=peaks

#a funciton to find boundaries for the motif
def Ref_Peaks(i):
    print('Threshold value: ' + str(y))
    print ("Peaks time stamps in raw data: ", peaks_array_filtered[11])
    plt.plot(Ref_Acceleration_39[i], linewidth = '3', label = 'Filtered data')
    plt.axhline(y, linewidth = '3', color = 'r',label = 'Threshold')
    #plt.suptitle(name + ' ' + Ref_Location + ' '+ str(i), fontsize='30')
    plt.legend(fontsize = 30)
    plt.xlabel('Time Stamp, [cs]', fontsize=30)
    plt.ylabel('Acceleration, [m/s^2]', fontsize = 30)
    plt.grid(True, 'both')
    plt.show()

#---------------------------------------------------------Reference Matrix Definiton---------------------------------------------------#

#Cut out the Motif
Ref_Peaks(0)
print ("Start: ",end='')
start = int(input()) #specify first gait event
start = start - 20
print ("End: ",end='')
end = int(input()) #specify last gait event
end = end + 20

gaitCyclePattern = Ref_Acceleration_39[0][start:end] #define the reference matrix
print ('Start: ' + str(start), 'End: ' + str(end))

#---------------------------------------------------------Matrix Profiling-------------------------------------------------------------#

def SavGol_39 (i):
    #applying the Sav_Gol filter
    ACC_filtered = savgol_filter(df.averagea, 39, 3)
    #the filtered signal is stored into an array
    acceleration_39[i] = ACC_filtered
    return acceleration_39[i]
def PlotMatch(i):
    plt.plot(acceleration[i], label = 'Filtered data: ' + str(i+1))
    plt.plot(range(indx_array[i],indx_array[i] + len (gaitCyclePattern)), acceleration[i][indx_array[i]:indx_array[i]+len(gaitCyclePattern)], label = 'Motif', linewidth = 4)
    plt.suptitle('Match in ' + name + "'s dataset number: " + str(i+1), fontsize='30')
    plt.grid(True, 'both')
    plt.legend()
    plt.show()

path = Ref_path
files = os.listdir(path)
name = path.split('\\')
name = name[-1]
#Upload the data and apply Sav_Gol filter upon it
i = 0
for file in files:
    if file.endswith(".xlsx") and file.startswith(location):
        df = pd.read_excel(os.path.join(path, file))
        df.columns = ['time','stamp','battery', 'pressure','temperature','ax','ay','az','gx','gy','gz','mx','my','mz','averagea']
        acceleration[i] = SavGol_39(i)
        i += 1

#Run the matrix profiling through all datasets        
i = 0
for i in range (0,10):
    distance_profile = stumpy.mass(gaitCyclePattern, acceleration[i])
    distance_profile_array[i] = distance_profile
    indx = np.argmin(distance_profile)
    indx_array[i] = indx
    i += 1

#Chop out the Motif
i = 0
for i in range(0,10):
    profile_match = acceleration[i][indx_array[i]:indx_array[i]+len(gaitCyclePattern)]
    profile_match_array[i] = profile_match
    i+=1

#find peaks in the chopped Motif
i = 0
for i in range (0,10):
    peaks,_ = find_peaks(profile_match_array[i], height=y)
    peaks_array_filtered[i]=peaks
    NumOfPeaks[i] = len(peaks)
    i+=1
#plot every dataset with peaks array
i = 0
for i in range (0,10):
    PlotMatch(i)
    print('Peaks: ', peaks_array_filtered[i])
    print('Number of Peaks in Profile Match: ', NumOfPeaks[i])
    i += 1
