import tkinter

import numpy as np
import pandas as pd
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2Tk)
from matplotlib.figure import Figure
from calculations import addCols
from sidebyside import getFilteredData, readFileIntoDF,getPeaks


#GET DATA
DATA_FILE = "Katsed\Katsed\Ground\Ankle\Ankle_asphalt_1.txt"
df = readFileIntoDF(DATA_FILE)


root = tkinter.Tk()
root.wm_title("Embedding in Tk")

fig = Figure(figsize=(8, 4), dpi=100)
ax = fig.add_subplot()
    # Filter with SavGol filter
unfiltered_acc = df.averagea
filtered_acc = getFilteredData(df.averagea)

# This adds the time parameter
df.insert(len(df.columns), "filtered_acc", filtered_acc)
filtered_acc = df.filtered_acc

# Get peaks in filtered data
peaks = getPeaks(filtered_acc)
filtered_acc = df.filtered_acc
a = filtered_acc[peaks]

line, = ax.plot(filtered_acc)
dots, = ax.plot(filtered_acc[peaks].to_frame(),".",markersize=20,picker=True)

ax.set_xlabel("time [cs]")
ax.set_ylabel("Acceleration")

canvas = FigureCanvasTkAgg(fig, master=root)  # A tk.DrawingArea.
canvas.draw()


def handlePick(event):
    global peaks
    global filtered_acc
    ind = event.ind
    #event index might be an array if 2 peaks are overlapping
    for i in ind:
        peaks[i] = 0
   
    dots.set_xdata(peaks)
    print(peaks)
    canvas.draw()       
canvas.mpl_connect("pick_event",handlePick)

button_quit = tkinter.Button(master=root, text="Quit", command=root.destroy)
peaksArr_label = tkinter.Label(master=root,text=peaks)




# slider_update = tkinter.Scale(root, from_=1, to=5, orient=tkinter.HORIZONTAL,
#                               command=update_frequency, label="Frequency [Hz]")

# Packing order is important. Widgets are processed sequentially and if there
# is no space left, because the window is too small, they are not displayed.
# The canvas is rather flexible in its size, so we pack it last which makes
# sure the UI controls are displayed as long as possible.
button_quit.pack(side=tkinter.BOTTOM)

# slider_update.pack(side=tkinter.BOTTOM)
canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True)

tkinter.mainloop()
