from dataHandler import getFilteredData, getPeaks


def automaticPeakFinder(dataframe, selectedFilterValue, selectedItem, sensorLocationValue, filterSetting):
    df = dataframe
    filterValue = selectedFilterValue
    sensorLocation = sensorLocationValue

    # Only find the best filter value if it's selected in UI
    if filterSetting == 1:
        filterValue = findBestFilterValue(df, filterValue, sensorLocation)
        print(filterValue)

    filtered_acc = getFilteredData(df, filterValue)

    # This adds the time parameter
    df.insert(len(df.columns), "filtered_acc", filtered_acc)
    filtered_acc = df.filtered_acc

    peaks = getPeaks(
        selectedItem, filtered_acc, sensorLocation)

    peaks = removePeaksUnderAverageValue(peaks, filtered_acc)
    peaks = removeDuplicatePeaks(peaks, filtered_acc)
    peaks = removePeaksBeforeAndAfterGaitCycles(peaks, filtered_acc)
    peaks = removeInvalidPeaks(peaks, filtered_acc)
    
    return peaks, filtered_acc, filterValue

def findAverageValue(peaks, filtered_acc):
    if not len(peaks):
        return 0

    averageValue = 0
    for i in range(0, len(peaks)):
        averageValue += filtered_acc[peaks[i]]
    averageValue = (averageValue / len(peaks))

    return averageValue

def removeInvalidPeaks(peaks, filtered_acc):
    filteredPeaks = set()
    for i in range(1, len(peaks) - 1):
        minPeaksDifference = findAverageDistance(peaks, filtered_acc) * 0.3
        if filtered_acc[peaks[i - 1]] - filtered_acc[peaks[i]] > minPeaksDifference and \
                filtered_acc[peaks[i + 1]] - filtered_acc[peaks[i]] > minPeaksDifference:
            filteredPeaks.update((peaks[i], peaks[i - 1], peaks[i + 1]))
    return list(filteredPeaks)

def removePeaksUnderAverageValue(peaks, filtered_acc):
    averageValue = findAverageValue(peaks, filtered_acc) * 0.80
    filtered_peaks = []
    for item in peaks:
         if filtered_acc[item] > averageValue:
             filtered_peaks.append(item)
    return filtered_peaks

def removeDuplicatePeaks(peaks, filtered_acc):
    previous_peak = None
    filtered_peaks = []
    for i, peak in enumerate(peaks):
        if previous_peak is None:
            previous_peak = peak
        else:
            if abs(peak - previous_peak) < 15 and filtered_acc[peak] > filtered_acc[previous_peak]:
                previous_peak = peak
            else:
                filtered_peaks.append(previous_peak)
                previous_peak = peak
        if i == len(peaks)-1 and peak != previous_peak:
            filtered_peaks.append(previous_peak)
    else:
        if previous_peak is not None and previous_peak not in filtered_peaks:
            filtered_peaks.append(previous_peak)
    return filtered_peaks

def findAverageDistance(peaks, filtered_acc):
    if not len(peaks):
        return 0

    # Calculate the average distance between the peaks
    distances = [abs(filtered_acc[i] - filtered_acc[j]) for i, j in zip(peaks, peaks[1:])]
    average_distance = sum(distances) / len(distances)

    return average_distance

def removePeaksBeforeAndAfterGaitCycles(peaks, filtered_acc):
    averageValue = findAverageValue(peaks, filtered_acc)
    print(averageValue)
    gait_cycle_reached = False
    gait_cycle_end_reached = False
    filtered_peaks = []
    for item in peaks:
        if filtered_acc[item] > averageValue * 0.95 and not gait_cycle_reached:
             gait_cycle_reached = True
             filtered_peaks = []
             print("start reached")
        if filtered_acc[item] < averageValue * 0.77 and gait_cycle_reached and not gait_cycle_end_reached:
            print(averageValue * 0.77)
            print("end reached")
            break
        filtered_peaks.append(item)
    return filtered_peaks





def findBestFilterValue(dataframe, selectedItem, sensorLocation):
    df = dataframe.copy()
    bestFilter = 0
    highestPeaksAmount = 0

    # Go through the filter values
    for x in range(39, 49):
        temp_df = df.copy()
        filtered_acceleration = getFilteredData(temp_df, x)
        temp_df.insert(len(temp_df.columns), "filtered_acc", filtered_acceleration)
        filtered_acceleration = temp_df.filtered_acc

        peaks = getPeaks(
        selectedItem, filtered_acceleration, sensorLocation)
        filtered_acceleration = temp_df.filtered_acc
        
        
        peaks = removePeaksUnderAverageValue(peaks, filtered_acceleration)
        peaks = removeDuplicatePeaks(peaks, filtered_acceleration)
        peaks = removeDuplicatePeaks(peaks, filtered_acceleration)
        peaks = removeInvalidPeaks(peaks, filtered_acceleration)
        peaks = removePeaksBeforeAndAfterGaitCycles(peaks, filtered_acceleration)
 

        if len(peaks) > highestPeaksAmount:
            bestFilter = x
            highestPeaksAmount = len(peaks)

    return bestFilter





