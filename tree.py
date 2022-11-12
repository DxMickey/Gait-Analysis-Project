# tree
from tkinter import W,ttk
def getTreeWidget(parent,selectedSave,additionalData):
    tree = ttk.Treeview(parent, columns=("tableName", "sensorId", "patientName",
                        "sensor_location", "situation", "date"), selectmode="none")

    tree.heading('tableName', text="Saved name", anchor=W)
    tree.heading('sensorId', text="Sensor ID", anchor=W)
    tree.heading('patientName', text="Patient", anchor=W)
    tree.heading('sensor_location', text="Sensor location", anchor=W)
    tree.heading('situation', text="Situation", anchor=W)
    tree.heading('date', text="Date", anchor=W)

    tree.column('#0', minwidth=0, width=0)
    tree.column('#1', minwidth=85, width=85)
    tree.column('#2', minwidth=60, width=60)
    tree.column('#3', minwidth=130, width=130)
    tree.column('#4', minwidth=75, width=75)
    tree.column('#5', minwidth=80, width=80)
    tree.column('#6', minwidth=130, width=130)

    #tree.bind('<Motion>', 'break')
    tree.bind('<ButtonRelease-1>', selectedSave)
    tree.bind('<Double-Button-1>', additionalData)
    
    return tree