# Searches for a usb stick https://mail.python.org/pipermail/python-win32/2006-December/005406.html
from numpy import empty


def locate_usb():
    import win32file
    drive_list = []
    drivebits=win32file.GetLogicalDrives()
    for d in range(1,26):
        mask=1 << d
        if drivebits & mask:
            drname='%c:\\' % chr(ord('A')+d)
            t=win32file.GetDriveType(drname)
            if t == win32file.DRIVE_REMOVABLE:
                drive_list.append(drname)
    test = drive_list
    return test
    
def getUSBDrive(sensorIdFileName):
            USBdrive = locate_usb()
            for i in range(len(USBdrive)):
                try:
                    sensorID = open(USBdrive[i] + sensorIdFileName, "r").read()
                    return sensorID
                except:
                    print ("No such file on this USB/Sensor")