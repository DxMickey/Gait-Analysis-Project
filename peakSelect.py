import numpy as np
class peakSelect:
    def __init__(self) -> None:
        self.initialPeaks = []
        self.queue = []
        self.peaks = []
        self.firstGaitEvent = -1
        self.lastGaitEvent = -1
        self.info = "Set first gait event"
        self.currQueuePointer = 0
    def setPeaks(self,peaks):
        self.firstGaitEvent = -1
        self.lastGaitEvent = -1
        self.peaks = peaks
    def getPeaks(self):
        return self.peaks
    def setGaitEvent(self,index,cmd):
        if(cmd == "last"):
            self.lastGaitEvent = index
            self.peaks = self.peaks[0:index + 1]
        if(cmd == "first"):
            self.firstGaitEvent = 0
            self.peaks = self.peaks[index:]
        # if index <= 0:
        #     return
        # if self.firstGaitEvent >=0 and self.lastGaitEvent < 0:
        #     self.lastGaitEvent = index
        #     self.peaks = self.peaks[0:self.lastGaitEvent+1]
        # else:
        #     self.lastGaitEvent = -1
        #     self.firstGaitEvent = index
        #     self.peaks = self.peaks[index:]
    
    def deletePeak(self,indices):
        self.queue.append(self.peaks) #save current state
        self.peaks = np.delete(self.peaks, indices)
        self.info = "Peak deleted. Ctrl + Z to undo"
        self.currQueuePointer += 1
    def undo(self):
        queuePos = self.currQueuePointer - 1
        if queuePos <= 0:
            queuePos = 0
        self.peaks = self.queue[queuePos]
    def redo(self):
        queuePos = self.currQueuePointer + 1
        if queuePos >= len(queuePos):
            queuePos = len(queuePos) -1
        self.peaks = self.queue[queuePos]
    def cutPeaks(self):
        #cut the peaks
        return self.peaks[self.firstGaitEvent:self.lastGaitEvent]
        