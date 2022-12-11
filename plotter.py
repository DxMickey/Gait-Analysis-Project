import matplotlib.patches as mpatches


def plotAccelerationWithPeaks(axes, acceleration, peaks,title):
    axes.clear()
    axes.plot(acceleration)
    axes.plot(acceleration[peaks].to_frame(),
              ".", markersize=20, picker=True)
    axes.set_title(title)
    axes.grid(True, 'both')
    axes.set_xlabel("time [cs]")
    axes.set_ylabel("Acceleration [ms^2]")


def plotGaitCycles(axes, gaitCycles, color, lightcolor, error, deviationMode):
    print(gaitCycles)
    for cycle in gaitCycles:
        axes.plot(cycle.time, cycle.filtered_acc, color)
        if deviationMode == "yes":
            yerr0 = cycle.filtered_acc - error
            yerr1 = cycle.filtered_acc + error
            axes.fill_between(cycle.time, yerr0, yerr1, color=lightcolor, alpha=0.5)
        axes.grid(True, 'both')
        axes.set_xlabel("Gait cycle")
        axes.set_ylabel("Acceleration [ms^2]")

def plotJoinedGaitCycles(axes, gaitCycles, color, lightcolor, error, deviationMode):
    time = []
    for i in range(len(gaitCycles)):
        time.append(1/(len(gaitCycles)-1)*(i))
    axes.plot(time, gaitCycles, color)
    

    if deviationMode == "yes":
        count = 0
        yerr0 = []
        yerr1 = []
        for cycle in gaitCycles:
            
            yerr0.append(cycle-error[count])
            yerr1.append(cycle+error[count])
            count += 1
        
        axes.fill_between(time, yerr0, yerr1, color=lightcolor, alpha=0.5)




    axes.grid(True, 'both')
    axes.set_xlabel("Gait cycle")
    axes.set_ylabel("Acceleration [ms^2]")
    


def plotGaitCycleLabels(axes, selectedItems, colorList, count):
    # where some data has already been plotted to ax
    handles, labels = axes.get_legend_handles_labels()

    for i in range(0, count):
        legendText = mpatches.Patch(
            color=colorList[i], label=selectedItems[i])
        handles.append(legendText)

        axes.legend(handles=handles)


def plotRawData(axes, df):
    axes.clear()
    axes.plot(df.averagea,color="blue")
    axes.plot(df.filtered_acc,color="red")
    axes.grid(True, 'both')
    axes.set_xlabel("time [cs]")
    axes.set_ylabel("Acceleration [ms^2]")
def highlightPeak(axes, acceleration,peaks,index):
    for i in range(len(peaks)):
        color = None
        if(i == index):
            color = "red"
        axes.plot(acceleration[peaks[i]].to_frame(),
              ".", markersize=20, picker=True, color=color)
