from math import sqrt
#Converts the time stamp into seconds
#Inputs: timeStap
def timeStampToSeconds(timeStamp,firstTimeStamp):
    #TODO: Figure out what the excel formula does exactly and replicate in python
    return (timeStamp/1000) - (firstTimeStamp/1000)
    
#Calculates the magnitude of a 3-d vector
#Inputs: x,y,z direction of the vector
def calculateMagnitude(x,y,z):
    return sqrt(x**2 + y**2 + z**2)