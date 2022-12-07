from math import sqrt

#Converts the time stamp into seconds
#Inputs: timeStamp
def timeStampToSeconds(timeStamp,firstTimeStamp):
    return (timeStamp/1000) - (firstTimeStamp/1000)
    
#Calculates the magnitude of a 3-d vector
#Inputs: x,y,z direction of the vector
def calculateMagnitude(x,y,z):
    return sqrt(x**2 + y**2 + z**2)
#Adds the required columns to the dataframe and returns the appended df
def addCols(df):
    df.columns = ['stamp','battery', 'pressure','temperature','ax','ay','az','gx','gy','gz','mx','my','mz']
        
    #Calculate magnitudes
    magnitudes = []
    for idx,x in enumerate( df['ax']):
        y = df['ay'][idx]
        z = df['az'][idx]
        magnitudes.append(calculateMagnitude(x,y,z))
    #Add averagea column with the calculated data
    df.insert(len(df.columns),"averagea" ,magnitudes)
    
    #Calculate timestamps
    beginTime = df['stamp'][0]
    timestamps = []
    for idx,stamp in enumerate(df['stamp']):
        timestamps.append(timeStampToSeconds(stamp,beginTime))
    #Insert the calculated times
    df.insert(0,'time',timestamps)
    return df
    