from tkinter import W,ttk

def getTreeWidget(parent,selectedSave,additionalData):
    tree = ttk.Treeview(parent, columns=("tableName", "sensorId", "peaksSaved", "patientName",
     "sensor_location", "situation", "date"))

    tree.heading('tableName', text="Saved name", anchor=W)
    tree.heading('sensorId', text="Sensor ID", anchor=W)
    tree.heading('peaksSaved', text="Peaks saved", anchor=W)
    tree.heading('patientName', text="Patient", anchor=W)
    tree.heading('sensor_location', text="Sensor location", anchor=W)
    tree.heading('situation', text="Situation", anchor=W)
    tree.heading('date', text="Date", anchor=W)

    tree.column('#0', width=0)
    tree.column('#1', width=85)
    tree.column('#2', width=60)
    tree.column('#3', width=75)
    tree.column('#4', width=100)
    tree.column('#5', width=90)
    tree.column('#6', width=60)
    tree.column('#7', width=90)

    #tree.bind('<Motion>', 'break')
    tree.bind('<ButtonRelease-1>', selectedSave)
    tree.bind('<Double-Button-1>', additionalData)
    
    return tree