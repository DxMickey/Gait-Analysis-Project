#Returns the y value for foot, shank, ankle
def getBaseline(str):
    str = str.lower()
    if str == "foot":
        return 16
    elif str == "shank":
        return 13
    elif str == "ankle":
        return 14
    else:
        return 14