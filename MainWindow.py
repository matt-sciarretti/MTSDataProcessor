import sys
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import QProcess
from ui_main import Ui_MainWindow
import os
from scipy.interpolate import make_interp_spline
import matplotlib.pyplot as plt
from shapely.geometry import LineString
import pandas as pd
import astmD638
import time

class mainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ProcessedDataList = []
        self.buildID = ""
        machinetype = ['Instron', 'MTS Flex Test']
        standards = ['ASTM D638', 'ISO 527', 'ASTM E8']
        self.html_colors = [
        'red', 'green', 'blue', 'yellow', 'cyan', 'magenta', 'purple', 'orange',
        'lime', 'pink', 'teal', 'brown', 'maroon', 'indigo', 'skyblue', 'navy', 'olive',
        'coral', 'turquoise', 'salmon', 'gold', 'violet','orchid', 
        'tan', 'aquamarine', 'khaki', 'tomato', 'peru', 'slategray'
        ]
        self.ui.ProgressBar = QtWidgets.QProgressBar(self)
        
        
        self.ui.forwardSTL.clicked.connect(lambda: self.navPlots(True))
        self.ui.backwardSTL.clicked.connect(lambda: self.navPlots(False))
        self.ax = self.ui.plot_view.canvas.ax
        self.ui.standardCombo.addItems(standards)
        self.ui.RawTypeBox.addItems(machinetype)
        self.ui.loadUtilites.clicked.connect(lambda: self.branch())
        self.ui.plot_view.canvas.ax
        self.ui.activeSTL.currentIndexChanged.connect(lambda: self.ChangeIndex())
        self.ui.saveAll.clicked.connect(lambda: self.saveFigures())
        self.ui.COadjustmentF.clicked.connect(lambda: self.COadjustment(True))
        self.ui.COadjustmentB.clicked.connect(lambda: self.COadjustment(False))
        self.ui.MMAforward.clicked.connect(lambda: self.MMadjustment(True))
        self.ui.MMAback.clicked.connect(lambda: self.MMadjustment(False))

        
        

    def branch(self):
        if self.ui.standardCombo.currentText() == "ASTM D638" and self.ui.RawTypeBox.currentText() == 'Instron':
            try:
                self.buildID, done1 = QtWidgets.QInputDialog.getText(self, 'Input Dialog', 'Enter the Build Id [XXXX (XXXX)]:')
                dataList, ids = astmD638.open_folder(0)
                self.ProcessedDataList = astmD638.processData_start(dataList, ids)
            except Exception as e:
                print(e)
                return
        elif self.ui.standardCombo.currentText() == "ASTM D638" and self.ui.RawTypeBox.currentText() == 'MTS Flex Test':
            try:
                self.buildID, done1 = QtWidgets.QInputDialog.getText(self, 'Input Dialog', 'Enter the Build Id [XXXX (XXXX)]:')
                dataList, ids = astmD638.open_folder(1)
                self.ProcessedDataList = astmD638.processData_startMPT(dataList, ids)
            except Exception as e:
                print(e)
                return    

        self.fillIDbox(self.ProcessedDataList)


    
    def fillIDbox(self, ProcessedDataList):
        self.sortList()
        self.ui.activeSTL.clear()
        index = 0
        while index <= len(ProcessedDataList)-1:
            specimine = ProcessedDataList[index]
            self.ui.activeSTL.addItem(specimine.id)
            index = index +1
        self.processDataPlot(self.ui.activeSTL.currentIndex())
    


    def navPlots(self, direction):
        if direction and self.ui.activeSTL.currentIndex() == len(self.ProcessedDataList) - 1:
            self.processDataPlot(0)
            self.ui.activeSTL.setCurrentIndex(0)
        elif direction and self.ui.activeSTL.currentIndex() != len(self.ProcessedDataList) - 1:
            self.processDataPlot(self.ui.activeSTL.currentIndex() + 1)
            self.ui.activeSTL.setCurrentIndex(self.ui.activeSTL.currentIndex() + 1)
        elif not direction and self.ui.activeSTL.currentIndex() == 0:
            self.processDataPlot(len(self.ProcessedDataList) - 1)
            self.ui.activeSTL.setCurrentIndex(len(self.ProcessedDataList) - 1)
        elif not direction and self.ui.activeSTL.currentIndex() != 0:
            self.processDataPlot(self.ui.activeSTL.currentIndex() - 1)
            self.ui.activeSTL.setCurrentIndex(self.ui.activeSTL.currentIndex() - 1)
            


    def ChangeIndex(self):
        print("entered change index")
        try:
            self.ax.clear()
            i = self.ui.activeSTL.currentIndex()
            self.ui.activeSTL.setCurrentIndex(i)
            self.processDataPlot(i)  # Pass the index to the processDataPlot method
        except Exception as e:
            print(e)




    def processDataPlot(self, index):
        df = self.ProcessedDataList[index]
        cap = 0
        try:
            self.ax.clear()
            self.ax.plot(df.strain, df.stress)
            self.ax.plot(df.mstrain, df.mstress, label="Modulus = " + str(df.modulus)[0:8])
            self.ax.plot((df.percentYeild/100), df.maxStress, 'o', label = "Yeild = ("+ str(df.percentYeild)[0:5] + ", "+ str(df.maxStress)[0:7] + ")")
            self.ax.plot((df.percentatBreak/100), df.breakStress, 'x', label = "Break = ("+ str(df.percentatBreak)[0:5] + ", "+ str(df.breakStress)[0:7] + ")")
            self.ax.plot((df.mstrain[len(df.mstrain)-1]), df.mstress[len(df.mstress)-1], 'x', label = "Mod End = " + str(df.mstrain[len(df.mstrain) - 1])[0:5])
            self.ax.plot(df.mstrain[0], df.mstress[0], 'x', label = "Mod Start = " + str(df.mstrain[0])[0:5])
            self.ax.set_xlabel("Engineering Strain (in/in)")
            self.ax.set_ylabel("Engineering Stress (ksi)")
            self.ax.legend(loc = 'lower right')
            self.ui.plot_view.canvas.draw()
            print("Plotted: " + str(index))
        except Exception as e:
            print(e)

    
    def saveFigures(self):
        if len(self.ProcessedDataList) == 0:
            return
        try:
            saveFolder = QFileDialog.getExistingDirectory(caption='Open Machine Folder')
            astmD638.createTensileRecord(self.ProcessedDataList, saveFolder)
        except Exception as e:
            print(e)
            return
        for item in self.ProcessedDataList:
            plt.subplots(figsize=(8, 7))
            plt.plot(item.strain, item.stress)
            plt.plot(item.mstrain, item.mstress, label="Modulus = " + str(item.modulus)[0:8])
            plt.plot((item.percentYeild/100), item.maxStress, 'o', label = "Yeild = ("+ str(item.percentYeild)[0:5] + ", "+ str(item.maxStress)[0:7] + ")")
            plt.plot((item.percentatBreak/100), item.breakStress, 'x', label = "Break = ("+ str(item.percentatBreak)[0:5] + ", "+ str(item.breakStress)[0:7] + ")")
            plt.xlabel("Engineering Strain (in/in)")
            plt.ylabel("Engineering Stress (ksi)")
            plt.title(self.buildID + "\n" + item.id + "\n" + "Stress vs Strain")
            plt.grid(True)
            plt.legend(loc = 'lower right')
            plt.savefig(os.path.join(saveFolder, item.id + ".png"))
            plt.close()
        
        orrientations = astmD638.sumplotSplit(self.ProcessedDataList)

        for orrientation in orrientations:
            i = 0
            plt.subplots(figsize=(8, 8))
            plt.xlabel("Engineering Strain (in/in)")
            plt.ylabel("Engineering Stress (ksi)")
            plt.title(self.buildID + "\n" + "Ultem Qual\n" + orrientation + " Summary\n" + "Stress vs Strain")
            for item in self.ProcessedDataList:
                if item.orrient == orrientation:
                    plt.plot(item.strain, item.stress, label = item.id, color = self.html_colors[i])
                    i = i+1
            plt.legend(loc = 'lower right')
            plt.grid(True)
            plt.savefig(os.path.join(saveFolder, orrientation + ".png"))
            plt.close()
        return


    
    def COadjustment(self, direction):
        i = self.ui.activeSTL.currentIndex()
        df = self.ProcessedDataList[i]
        if direction:
            try:
                index = len(df.strain) - 1
                df.strain.append(df.fullStrain[index + 1])
                df.stress.append(df.fullStress[index + 1])
            except Exception as e:
                print(e)
                return
        else:
            try:
                index = len(df.strain) - 1
                df.strain = df.strain[0: index -1]
                df.stress = df.stress[0: index -1]
            except Exception as e:
                print(e)
                return
        df.breakStress = df.stress[len(df.stress) - 1]
        df.percentatBreak = df.strain[len(df.strain) - 1] *100
        self.ProcessedDataList[i] = df
        self.processDataPlot(i)
    
    def MMadjustment(self, direction):
        i = self.ui.activeSTL.currentIndex()
        df = self.ProcessedDataList[i]
        if direction:
            try:
                index = len(df.mstrain) - 1
                df.mstrain.append(df.fullStrain[index + 1])
                df.mstress.append(df.fullStress[index + 1])
            except Exception as e:
                print(e)
                return
        else:
            try:
                index = len(df.mstrain) -1
                df.mstrain = df.mstrain[0:index -1]
                df.mstress = df.mstress[0:index -1]
            except Exception as e:
                print(e)
                return
        df.modulus = astmD638.find_modulus(df.mstrain, df.mstress)
        self.ProcessedDataList[i] = df
        self.processDataPlot(i)

    def sortList(self):
        print("enter sort")
        hold = 0
        self.ProcessedDataList = sorted(self.ProcessedDataList, key=lambda x: x.number)
        for item in self.ProcessedDataList:
            print(str(item.number) + " ")

    def update_progress(total_items):

        self.ui.ProgressBar.setMinimum(0)
        self.ui.ProgressBar.setMaximum(total_items)
        self.ui.ProgressBar.setValue(self.ui.ProgressBar.value() + 1)  # Increment the progress bar value


if __name__=='__main__':
    app = QtWidgets.QApplication(sys.argv)
    application = mainWindow()
    application.show()
   
    sys.exit(app.exec())