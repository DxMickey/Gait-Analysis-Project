import matplotlib.patches as mpatches

def plotAccelerationWithPeaks(axes, acceleration, peaks):
    axes.clear()
    axes.plot(acceleration)
    axes.plot(acceleration[peaks].to_frame(),
            ".", markersize=20, picker=True)

    axes.grid(True, 'both')
    axes.set_xlabel("time [cs]")
    axes.set_ylabel("Acceleration [ms^2]")


def plotGaitCycles(axes,gaitCycles,color):
    for cycle in gaitCycles:
        axes.plot(cycle.time, cycle.filtered_acc, color)
        axes.grid(True, 'both')
        axes.set_xlabel("time [cs]")
        axes.set_ylabel("Acceleration [ms^2]")
def plotGaitCycleLabels(axes,selectedItems,colorList,count):
    # where some data has already been plotted to ax
    handles, labels = axes.get_legend_handles_labels()

    for i in range(0, count):
        legendText = mpatches.Patch(
                color=colorList[i], label=selectedItems[i])
        handles.append(legendText)

        axes.legend(handles=handles)    
        