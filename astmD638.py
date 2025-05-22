import pandas as pd
from PyQt5.QtWidgets import QFileDialog
import os
import MainWindow as MW
import xlrd
from DataFormat import ProcessedData
import xlsxwriter
import numpy as np





def open_folder(mach):
    #print("Open_folder_enter")
    try:
        rawFolder = QFileDialog.getExistingDirectory(caption='Open Machine Folder')
        if rawFolder:  # Check if a folder is selected
            dataList, ids = extractData(rawFolder, mach)
            return dataList, ids
    except Exception as e:
        print(e)


def extractData(rawFolder, mach):
    dataList = []
    ids = []
    if mach == 0:
        for file in os.listdir(rawFolder):
            file_path = os.path.join(rawFolder, file)
            df = pd.read_csv(file_path, skiprows = 4)
            dataList.append(df)
            ids.append(file)
        return dataList, ids
    elif mach == 1:
        for file in os.listdir(rawFolder):
            file_path = os.path.join(rawFolder, file)
            df_opinfo = pd.read_csv(file_path, skiprows = 2, delim_whitespace= True , nrows = 7)
            print(df_opinfo)
            df_data = pd.read_csv(file_path, skiprows = 14, sep= '\t', on_bad_lines= "skip")
            infoarray = [df_data,df_opinfo]
            dataList.append(infoarray)

            ids.append(str(infoarray[1].iloc[2,1]))
            
        return dataList, ids


#Process Data Functions (Instron)

#####################################

def find_modulus(x, y):
    #print("enter find_modulus")
    x = np.array(x)
    y = np.array(y)
    
    modulus = np.sum((x - np.mean(x)) * (y - np.mean(y))) / np.sum((x - np.mean(x)) ** 2)
    
    return modulus



def getmstrain_mstress_modulus(df):
    targetRow = 0
    mstrain = []
    mstress = []
    while df.iloc[targetRow, 4] < .003 and targetRow < (len(df) - 100):
        mstrain.append(df.iloc[targetRow, 4])
        mstress.append(df.iloc[targetRow, 5])
        targetRow += 1
    mstrain.append(df.iloc[targetRow + 1, 4])
    mstress.append(df.iloc[targetRow + 1, 5])
    modulus = find_modulus(mstrain, mstress)
    return mstrain, mstress, modulus
    


def getStrain_Stress(df):
    stress = []
    strain = []
    fullStrain = []
    fullStress = []
    maxstress = -9999999999
    maxindex = 0
    
    
    leng = len(df) - 1
    while df.iloc[leng, 5] < 0:  
        if leng >= 0 and abs(df.iloc[leng, 5] - df.iloc[leng-1, 5]) < 0.1:
            leng -= 1
            break
        leng -= 1 
    cur = 0
    while cur < leng and cur < len(df):
        stress.append(df.iloc[cur, 5])
        if df.iloc[cur, 5] > maxstress:
            maxstress = df.iloc[cur, 5]
            maxindex = cur
        strain.append(df.iloc[cur, 4])
        cur += 1  # Increment cur
    i = 0
    while i < len(df):
        fullStrain.append(df.iloc[i,4])
        fullStress.append(df.iloc[i,5])
        i+=1
    return strain, stress, maxstress, (df.iloc[maxindex, 4] * 100), df.iloc[leng-1, 5], (df.iloc[leng-1, 4]*100), fullStrain, fullStress


def splitId(id):
    print("enter splitID")
    print(id)
    x = id.split(sep='.')
    id = x[0]
    y = id.split(sep = "-")
    number = int(y[1])
    orrient = y[0]
    print("exit splitID")
    return id, number, orrient


def processData_start(dataList, ids):
    ProcessedDataList = []
    count = 0
    for df in dataList:
        id, number, orrient = splitId(ids[count])
        strain, stress, maxStress, percentYeild, breakStress, percentatBreak, fullStrain, fullStress = getStrain_Stress(df)
        mstrain, mstress, modulus = getmstrain_mstress_modulus(df)
        
        ProcessedDataList.append(ProcessedData(id, stress, strain, mstress, mstrain, modulus, maxStress, percentYeild, breakStress, percentatBreak, fullStrain, fullStress, number, orrient))
        count  +=1
    
    
    i = 0
    j = 1
    while i < len(ProcessedDataList) -2:
        while j < len(ProcessedDataList) -1:
            if ProcessedDataList[i].number > ProcessedDataList[j].number:
                ProcessedDataList[i], ProcessedDataList[j] = ProcessedDataList[j], ProcessedDataList[i]
            j += 1
        i+=1

    return ProcessedDataList

def createTensileRecord(ProcessedDataList, path):
    count = 0
        
    
    title = "Tensile Record.xlsx"
    headers = ["Id", "Tensile Strength Yield(ksi)", "Elongation at Yield (%)", "Stress at Break (ksi)", "Elongation at break (%)", "Modulus"]
    workbook = xlsxwriter.Workbook(os.path.join(path,title))
    worksheet = workbook.add_worksheet(name = "Record")
        
        

    col = 2
    for header in headers:
        worksheet.write(0, col, header)
        col += 1
    
    column = 2
    row = 1
    index = 0
    while index < len(ProcessedDataList):
        worksheet.write(row, column, ProcessedDataList[index].id)
        worksheet.write(row,column+1, float(ProcessedDataList[index].maxStress))
        worksheet.write(row,column+2, float(ProcessedDataList[index].percentYeild))
        worksheet.write(row,column+3, float(ProcessedDataList[index].breakStress))
        worksheet.write(row,column+4, float(ProcessedDataList[index].percentatBreak))
        worksheet.write(row,column+5, float(ProcessedDataList[index].modulus))
        row += 1
        index += 1
    recordPath = os.path.join(path,title)
    workbook.close()
    



def sumplotSplit(ProcessedDataList):
    orrientations = []
    holder = ""
    for item in ProcessedDataList:
        if item.orrient != holder:
            orrientations.append(item.orrient)
    
    return orrientations
        
    
#Process Data Functions (MTP Flex Test)
#######################################


def getInfo(testinfo):
    print("enter getInfo")
    gageLength, width, thick, orrient = float(testinfo.iloc[6,3]), float(testinfo.iloc[4,1]), float(testinfo.iloc[5,1]), testinfo.iloc[3, 2]
    print("GageLength: "+ str(gageLength))
    print("width: "+ str(width) + " Thickness: "+ str(thick))
    area = width * thick
    print("exit getInfo")
    return area, gageLength, orrient

def splitId(id):
    print("enter splitID")
    print(id)
    y = id.split(sep = "-")
    number = int(y[1])
    orrient = y[0]
    print("exit splitID")
    return id, number

def getData(testData):
    print("enter getData")
    displacement = []
    force = []
    extenso = []
    dflength = len(testData) - 1
    i = 1
    while i < dflength:
        displacement.append(float(testData.iloc[i,1]))
        force.append(float(testData.iloc[i,2]))
        extenso.append(float(testData.iloc[i,3]))
        i += 1
    print("exit getData")
    return displacement, force, extenso

def stress_strain_calc(displacement, force, extenso, area, gageLength):
    print("enter stress_strain_calc")
    maxindex = 0
    maxstress = -9999999
    stress, strain = [], []
    index = 0
    for x,z in zip(force,extenso):
        y = (x/float(area))/1000
        w = z/gageLength
        if y > 0:
            stress.append(float(y))
            strain.append(float(w))
        index += 1
    
    fullStrain = strain
    fullStress = stress
    i = 0
    j = 0
    while i < len(strain)-2:
        if stress[i] - stress[i+1] > 1:
            break
        elif stress[i] < 0:
            j = j+1
        i = i+1
    
    
        
    print("Values Cut: " + str(i))
    stress = fullStress[j:i]
    strain = fullStrain[j:i]

    max_Value = max(stress)
    while stress[maxindex] != max_Value and maxindex < len(stress):
        maxindex += 1
    

    #print("Stress: " + str(stress) + "\n")
    #print("Strain: " + str(strain) + "\n")
    #print("exit stress_strain_calc")
    
    return stress, strain, stress[maxindex], fullStress, fullStrain, maxindex
    
    
def modulusMPT(strain):
    print("enter modulusMPT")
    index = 0
    while strain[index] < .003 and index < len(strain) -1:
        index = index +1
    modindex = index + 1
    print("exit modulusMPT")
    return modindex
    

def processData_startMPT(dataList, ids):
    print("enter processData_startMPT")
    modindex = 0
    ProcessedDataList = []
    count = 0
    for data in dataList:
        print("Specimine: " + str(count + 1))
        ident = ids[count]
        testData = data[0]
        testinfo = data[1]
        area, gageLength, orrient = getInfo(testinfo)
        id, number = splitId(ident)
        print("run getData")
        displacement, force, extenso = getData(testData)
        stress, strain, maxStress, fullStress, fullStrain, maxindex = stress_strain_calc(displacement, force, extenso, area, gageLength)
        modindex = modulusMPT(strain)
        mstress, mstrain = stress[0:modindex], strain[0:modindex]
        modulus = find_modulus(mstrain, mstress)
        percentYeild = strain[maxindex]*100
        breakStress = stress[len(stress)-1]
        percentatBreak = strain[len(strain)-1]*100

        ProcessedDataList.append(ProcessedData(id, stress, strain, mstress, mstrain, modulus, maxStress, percentYeild, breakStress, percentatBreak, fullStrain, fullStress, number, orrient))
        count = count+1
    i = 0
    j = 1
    while i < len(ProcessedDataList) -2:
        while j < len(ProcessedDataList) -1:
            if ProcessedDataList[i].number > ProcessedDataList[j].number:
                ProcessedDataList[i], ProcessedDataList[j] = ProcessedDataList[j], ProcessedDataList[i]
            j += 1
        i+=1
    return ProcessedDataList