from dataHandler import getFilteredData, getPeaks
import numpy as np
from scipy.signal import find_peaks, savgol_filter
import pandas as pd
import matplotlib.pyplot as plt


def automaticPeakFinder(
    dataframe, selectedItem, selectedFilterValue, sensorLocationValue
):
    """
    Performs automatic peak finding on the filtered acceleration data.

    Args:
        dataframe (pandas.DataFrame): Input data frame.
        selectedItem: Selected item.
        selectedFilterValue: Selected filter value.
        sensorLocationValue: Sensor location value.

    Returns:
        tuple: A tuple containing the filtered peak indices, filtered acceleration data, and the best filter value.
    """
    df = dataframe
    filterValue = selectedFilterValue
    sensorLocation = sensorLocationValue

    filterValue = findBestFilterValue(df)
    filtered_acc = getFilteredData(df, filterValue)

    # This adds the time parameter
    df.insert(len(df.columns), "filtered_acc", filtered_acc)
    filtered_acc = df.filtered_acc

    peaks, _ = find_peaks(filtered_acc, height=16, distance=15, prominence=9)
    # peaks = getPeaks(selectedItem, filtered_acc, sensorLocation)

    # peaks = removePeaksUnderAverageValue(peaks, filtered_acc)
    # peaks = removeDuplicatePeaks(peaks, filtered_acc)
    peaks = removePeaksBeforeAndAfterGaitCycles(peaks, filtered_acc)
    peaks = removeInvalidPeaks(peaks, filtered_acc)

    return peaks, filtered_acc, filterValue


def findAverageValue(peaks, filtered_acc):
    """
    Calculates the average value of the peaks in the filtered acceleration data.

    Args:
        peaks (list): List of peak indices.
        filtered_acc (pandas.Series): Filtered acceleration data.

    Returns:
        float: Average value of the peaks.
    """
    if not len(peaks):
        return 0

    averageValue = 0
    for i in range(0, len(peaks)):
        averageValue += filtered_acc[peaks[i]]
    averageValue = averageValue / len(peaks)

    return averageValue


def removeInvalidPeaks(peaks, filtered_acc):
    """
    Removes invalid peaks based on the average distance between peaks.

    Args:
        peaks (list): List of peak indices.
        filtered_acc (pandas.Series): Filtered acceleration data.

    Returns:
        list: List of filtered peak indices.
    """
    filteredPeaks = set()
    for i in range(1, len(peaks) - 1):
        minPeaksDifference = findAverageDistance(peaks, filtered_acc) * 0.3
        if (
            filtered_acc[peaks[i - 1]] - filtered_acc[peaks[i]] > minPeaksDifference
            and filtered_acc[peaks[i + 1]] - filtered_acc[peaks[i]] > minPeaksDifference
        ):
            filteredPeaks.update((peaks[i], peaks[i - 1], peaks[i + 1]))
    return list(filteredPeaks)


def removePeaksUnderAverageValue(peaks, filtered_acc):
    """
    Removes peaks that are below a certain threshold (80% of the average value).

    Args:
        peaks (list): List of peak indices.
        filtered_acc (pandas.Series): Filtered acceleration data.

    Returns:
        list: List of filtered peak indices.
    """
    averageValue = findAverageValue(peaks, filtered_acc) * 0.80
    filtered_peaks = []
    for item in peaks:
        if filtered_acc[item] > averageValue:
            filtered_peaks.append(item)
    return filtered_peaks


def removeDuplicatePeaks(peaks, filtered_acc):
    """
    Removes duplicate peaks that are too close to each other.

    Args:
        peaks (list): List of peak indices.
        filtered_acc (pandas.Series): Filtered acceleration data.

    Returns:
        list: List of filtered peak indices.
    """
    previous_peak = None
    filtered_peaks = []
    for i, peak in enumerate(peaks):
        if previous_peak is None:
            previous_peak = peak
        else:
            if (
                abs(peak - previous_peak) < 15
                and filtered_acc[peak] > filtered_acc[previous_peak]
            ):
                previous_peak = peak
            else:
                filtered_peaks.append(previous_peak)
                previous_peak = peak
        if i == len(peaks) - 1 and peak != previous_peak:
            filtered_peaks.append(previous_peak)
    else:
        if previous_peak is not None and previous_peak not in filtered_peaks:
            filtered_peaks.append(previous_peak)
    return filtered_peaks


def findAverageDistance(peaks, filtered_acc):
    """
    Calculates the average distance between peaks in the filtered acceleration data.

    Args:
        peaks (list): List of peak indices.
        filtered_acc (pandas.Series): Filtered acceleration data.

    Returns:
        float: Average distance between peaks.
    """
    if not len(peaks):
        return 0

    # Calculate the average distance between the peaks
    distances = [
        abs(filtered_acc[i] - filtered_acc[j]) for i, j in zip(peaks, peaks[1:])
    ]
    if len(distances) == 0:
        return 0
    average_distance = sum(distances) / len(distances)

    return average_distance


def removePeaksBeforeAndAfterGaitCycles(peaks, filtered_acc):
    """
    Removes peaks that occur before or after gait cycles.

    Args:
        peaks (list): List of peak indices.
        filtered_acc (pandas.Series): Filtered acceleration data.

    Returns:
        list: List of filtered peak indices.
    """
    averageValue = findAverageValue(peaks, filtered_acc)

    gait_cycle_reached = False
    filtered_peaks = []
    length = len(peaks)

    for i, item in enumerate(peaks):
        if filtered_acc[item] > averageValue * 0.95 and not gait_cycle_reached:
            gait_cycle_reached = True
            filtered_peaks = []
        if i < length - 1:
            if filtered_acc[item] < averageValue * 0.77 and gait_cycle_reached:
                break
        filtered_peaks.append(item)
    return filtered_peaks


def findBestFilterValue(dataframe):
    """
    Finds the best filter value by comparing the number of peaks detected for different filter values.

    Args:
        dataframe (pandas.DataFrame): Input data frame.

    Returns:
        int: Best filter value.
    """
    df = dataframe.copy()
    bestFilter = 0
    highestPeaksAmount = 0
    filter_value_dict = {}

    # Go through the filter values
    for x in range(39, 49):
        temp_df = df.copy()
        filtered_acceleration = getFilteredData(temp_df, x)
        temp_df.insert(len(temp_df.columns), "filtered_acc", filtered_acceleration)
        filtered_acceleration = temp_df.filtered_acc

        # peaks = getPeaks(selectedItem, filtered_acceleration, sensorLocation)
        peaks, _ = find_peaks(
            filtered_acceleration, height=16, distance=15, prominence=9
        )

        # peaks = removePeaksUnderAverageValue(peaks, filtered_acceleration)
        # peaks = removeDuplicatePeaks(peaks, filtered_acceleration)
        # peaks = removeDuplicatePeaks(peaks, filtered_acceleration)
        peaks = removePeaksBeforeAndAfterGaitCycles(peaks, filtered_acceleration)
        peaks = removeInvalidPeaks(peaks, filtered_acceleration)

        averageDistance = findAverageDistance(peaks, filtered_acceleration)

        if len(peaks) > highestPeaksAmount:
            filter_value_dict.clear()
            filter_value_dict[x] = averageDistance
            highestPeaksAmount = len(peaks)
        elif len(peaks) == highestPeaksAmount:
            filter_value_dict[x] = averageDistance

    bestFilter = max(filter_value_dict, key=filter_value_dict.get)

    return bestFilter


def generate_perfect_sinusoid():
    time = np.arange(0, 5, 0.0005)

    amplitude = 1
    frequency = 1
    phase = 0
    perfect_sinusoid = amplitude * np.sin(2 * np.pi * frequency * time + phase)
    perfect_sinusoid = perfect_sinusoid + 1

    noise_gaussian = np.random.normal(0, 0.01, len(time))

    perfect_sinusoid = perfect_sinusoid + noise_gaussian

    filtered_acc = pd.Series(perfect_sinusoid, name="filtered_acc")
    filtered_acc = savgol_filter(filtered_acc, 39, 3)
    filtered_acc = pd.Series(filtered_acc, name="filtered_acc")

    top_peaks, _ = find_peaks(filtered_acc)
    bottom_peaks, _ = find_peaks(-filtered_acc)

    peaks = []

    peaks.extend(top_peaks)
    peaks.extend(bottom_peaks)

    return filtered_acc, peaks


def plot_rmse():
    time = np.arange(0, 5, 0.0005)
    stdev = []
    rmse = []
    peaks_count = []

    for i in range(1, 101):

        amplitude = 1
        frequency = 1
        phase = 0
        perfect_sinusoid = amplitude * np.sin(2 * np.pi * frequency * time + phase)
        perfect_sinusoid = perfect_sinusoid + 1

        noise_gaussian = np.random.normal(0, i / 100, len(time))

        perfect_sinusoid = perfect_sinusoid + noise_gaussian

        filtered_acc = pd.Series(perfect_sinusoid, name="filtered_acc")
        filtered_acc = savgol_filter(filtered_acc, 39, 3)
        filtered_acc = pd.Series(filtered_acc, name="filtered_acc")

        # 1st algorithm version
        # peaks = getPeaks("none", filtered_acc, 0)

        # 2nd algorithm version
        top_peaks, _ = find_peaks(filtered_acc)
        bottom_peaks, _ = find_peaks(-filtered_acc)

        peaks = []

        peaks.extend(top_peaks)
        peaks.extend(bottom_peaks)

        peaks_count.append(len(peaks))

        # peaks = removePeaksUnderAverageValue(peaks, filtered_acc)
        # peaks = removeDuplicatePeaks(peaks, filtered_acc)
        # peaks = removePeaksBeforeAndAfterGaitCycles(peaks, filtered_acc)
        # peaks = removeInvalidPeaks(peaks, filtered_acc)
        # peaks = removePeaksUnderAverageValue(peaks, filtered_acc)

        difference = len(peaks) - 9
        squared_difference = np.square(difference)
        mean_squared_difference = np.mean(squared_difference)
        rmse.append(np.sqrt(mean_squared_difference))
        stdev.append(i / 100)

    for val1, val2 in zip(stdev, peaks_count):
        print(val1, val2)

    # Create the plot
    plt.plot(stdev, rmse, marker="o")

    # Set labels and title
    plt.xlabel("Standard deviation")
    plt.ylabel("RMSE value")

    # Show the plot
    plt.show()


def plot_rmse_plus_phase():
    time = np.arange(0, 5, 0.0005)
    stdev = []
    rmse = []
    peaks_count = []

    for i in range(1, 101):

        amplitude = 1
        frequency = 1
        phase = i
        perfect_sinusoid = amplitude * np.sin(2 * np.pi * frequency * time + phase)
        perfect_sinusoid = perfect_sinusoid + 1

        noise_gaussian = np.random.normal(0, i / 100, len(time))

        perfect_sinusoid = perfect_sinusoid + noise_gaussian

        filtered_acc = pd.Series(perfect_sinusoid, name="filtered_acc")
        filtered_acc = savgol_filter(filtered_acc, 39, 3)
        filtered_acc = pd.Series(filtered_acc, name="filtered_acc")

        # 1st algorithm version
        # peaks = getPeaks("none", filtered_acc, 0)

        # 2nd algorithm version
        top_peaks, _ = find_peaks(filtered_acc, distance=15, prominence=0.1)
        bottom_peaks, _ = find_peaks(-filtered_acc, distance=15, prominence=0.1)

        peaks = []

        peaks.extend(top_peaks)
        peaks.extend(bottom_peaks)

        peaks_count.append(len(peaks))

        # peaks = removePeaksUnderAverageValue(peaks, filtered_acc)
        # peaks = removeDuplicatePeaks(peaks, filtered_acc)
        peaks = removeInvalidPeaks(peaks, filtered_acc)
        # peaks = removePeaksBeforeAndAfterGaitCycles(peaks, filtered_acc)

        difference = len(peaks) - 9
        squared_difference = np.square(difference)
        mean_squared_difference = np.mean(squared_difference)
        rmse.append(np.sqrt(mean_squared_difference))
        stdev.append(i / 100)

    for val1, val2 in zip(stdev, rmse):
        print(val1, val2)

    # Create the plot
    plt.plot(stdev, rmse, marker="o")

    # Set labels and title
    plt.xlabel("Standard deviation and phase shift * 100")
    plt.ylabel("RMSE value")

    # Show the plot
    plt.show()
