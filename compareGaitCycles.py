import tkinter
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.figure import Figure
from dataHandler import getFilteredData, readFileIntoDF, getPeaks


"""
TODO: take sensor location into account here
TODO: undo/redo for removing peaks
TODO: embed into main UI
TODO: add ability to highlight single gait
TODO: add legend
TODO: actually remove peak on click instead of moving it to 0
"""

def mainCompare(tableName):

    #flag = --foot, --ankle, --shank
    #SENSOR_LOCATION = getBaseline(sys.argv[2][2:]) or 14 #if not provided default to ankle
    SENSOR_LOCATION = 14

    df = readFileIntoDF(tableName)


    root = tkinter.Tk()
    root.wm_title("GaitCycles")

    fig = Figure(figsize=(8, 4), dpi=100)
    ax = fig.add_subplot()
    #ax.set_title(DATA_FILE.split("\\")[-1])
    # Filter with SavGol filter
    unfiltered_acc = df.averagea
    filtered_acc = getFilteredData(df.averagea)

    # This adds the time parameter
    df.insert(len(df.columns), "filtered_acc", filtered_acc)
    filtered_acc = df.filtered_acc

    # Get peaks in filtered data
    peaks = getPeaks(filtered_acc,SENSOR_LOCATION)
    filtered_acc = df.filtered_acc
    a = filtered_acc[peaks]

    line, = ax.plot(filtered_acc)
    dots, = ax.plot(filtered_acc[peaks].to_frame(),
                    ".", markersize=20, picker=True)

    ax.set_xlabel("time [cs]")
    ax.set_ylabel("Acceleration [ms^2]")

    canvas = FigureCanvasTkAgg(fig, master=root)  # A tk.DrawingArea.
    canvas.draw()


    def handlePick(event):
        global peaks
        global filtered_acc
        ind = event.ind
        # event index might be an array if 2 peaks are overlapping
        for i in ind:
            peaks[i] = 0

        dots.set_xdata(peaks)
        canvas.draw()


    canvas.mpl_connect("pick_event", handlePick)
    canvas.mpl_connect("key_press_event", key_press_handler)

    def compareGait():
        global peaks, line, ax, filtered_acc
        peaks = peaks[peaks != 0]  # filter all the 0s aka stuff user just removed
        fig.clear()
        ax = fig.add_subplot()

        for i in range(0, len(peaks), 2):
            if(i + 2 > len(peaks)-1):
                break
            start = peaks[i]
            end = peaks[i+2]
            gaitCycle = filtered_acc[start:end]
            # sets the index starting from 0
            ax.plot(gaitCycle.reset_index(drop=True))
        canvas.draw()


    button_quit = tkinter.Button(master=root, text="Quit", command=root.destroy)
    button_sidebyside = tkinter.Button(
        master=root, text="Compare gait cycles", command=compareGait)
    toolbar = NavigationToolbar2Tk(canvas, root, pack_toolbar=False)
    toolbar.update()


    button_quit.pack(side=tkinter.BOTTOM)
    button_sidebyside.pack(side=tkinter.BOTTOM)
    toolbar.pack(side=tkinter.BOTTOM, fill=tkinter.X)

    canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True)


if __name__ == '__main__':
    tkinter.mainloop()
    mainCompare()
