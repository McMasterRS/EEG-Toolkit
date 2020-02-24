from wario import Node
import mne 
import numpy as np
import os, sys
import matplotlib.pyplot as plt

from wario.CustomSettings import CustomSettings
from wario.CustomWidgets import loadWidget, LinkedCheckbox

from PyQt5 import QtWidgets, QtCore, QtGui
from blinker import signal

class FileSelectWindow(QtWidgets.QWidget):
    def __init__(self, settings, type):
        super(FileSelectWindow, self).__init__()
        self.type = type
        self.layout = QtWidgets.QVBoxLayout()
        
        self.table = FileSelectTable(settings)
        
        self.btAdd = QtWidgets.QPushButton("Add Files")
        self.btAdd.clicked.connect(self.openFiles)
        self.btRemove = QtWidgets.QPushButton("Remove Files")
        self.btRemove.clicked.connect(self.removeFiles)
        
        btLayout = QtWidgets.QHBoxLayout()
        btLayout.setSpacing(5)
        btLayout.addWidget(self.btAdd)
        btLayout.addWidget(self.btRemove)
        
        self.layout.addWidget(self.table)
        self.layout.addItem(btLayout)
        self.setLayout(self.layout)
        
    def openFiles(self):
        fileList = QtWidgets.QFileDialog.getOpenFileNames(filter = self.type)[0]
        for file in fileList:
            i = self.table.rowCount()
            self.table.insertRow(i)
            self.table.setItem(i, 0, QtWidgets.QTableWidgetItem(file))
        
    def removeFiles(self):
        self.table.removeRow(self.table.currentRow())
        
    def genSettings(self, settings, vars):
    
        data = []
        for i in range(self.table.rowCount()):
            data.append(self.table.item(i, 0).text())
        
        settings["files"] = data
        vars["files"] = data
        
class FileSelectTable(QtWidgets.QTableWidget):
    def __init__(self, settings):
        super(FileSelectTable, self).__init__()
        
        self.setColumnCount(1)
        self.setHorizontalHeaderLabels(["Filename"])
        header = self.horizontalHeader()       
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)

        if "files" in settings.keys():
            for i, file in enumerate(settings["files"]):
                self.insertRow(self.rowCount())
                self.setItem(i, 0, QtWidgets.QTableWidgetItem(file))

class BdfImport(QtWidgets.QWidget):
    def __init__(self, settings):
        super(BdfImport, self).__init__()
        
        self.layout = QtWidgets.QVBoxLayout()
        self.fileSelect = FileSelectWindow(settings, "BDF Files (*.bdf)")    
        
        formLayout = QtWidgets.QFormLayout()
        formLayout.setSpacing(5)
        
        lb = QtWidgets.QLabel("Montage File")
        self.montageLoad = loadWidget(self)
        self.montageLoad.loadSettings(settings)
        formLayout.insertRow(-1, lb, self.montageLoad)
        
        self.maskSpinbox = QtWidgets.QSpinBox()
        self.maskSpinbox.setMaximum(2**24)
        self.maskSpinbox.setValue(255)
        self.maskEnable = LinkedCheckbox("Event mask", self.maskSpinbox)
        self.maskEnable.buildLinkedCheckbox("mask", settings)
        formLayout.insertRow(-1, self.maskEnable, self.maskSpinbox)
        
        self.layout.addWidget(self.fileSelect)
        self.layout.addItem(formLayout)
        
        self.setLayout(self.layout)
        
    def genSettings(self, settings, vars):
        
        self.fileSelect.genSettings(settings, vars)
        
        settings["filename"] = self.montageLoad.textbox.text()
        vars["montageFile"] = self.montageLoad.textbox.text()
        
        self.maskEnable.getSettings("mask", vars, settings)
        
class NumpyImport(QtWidgets.QWidget):
    def __init__(self, settings):
        super(NumpyImport, self).__init__() 
        
        self.layout = QtWidgets.QVBoxLayout()
        self.fileSelectWindow = FileSelectWindow(settings, "Numpy File (*.npz)")
        
        formLayout = QtWidgets.QFormLayout()
        formLayout.setSpacing(5)
        
        lb = QtWidgets.QLabel("Montage File")
        self.montageLoad = loadWidget(self)
        if "montage" in settings.keys():
            self.montageLoad.textbox.setText(settings["montage"])
        self.montageLoad.loadSettings(settings)
        formLayout.insertRow(-1, lb, self.montageLoad)
        
        lb = QtWidgets.QLabel("Channel Types")
        self.chanTypesLoad = loadWidget(self)
        if "chanTypes" in settings.keys():
            self.chanTypesLoad.textbox.setText(settings["chanTypes"])
        formLayout.insertRow(-1, lb, self.chanTypesLoad)
        
        lb = QtWidgets.QLabel("Sample Freq     ")
        self.sbFreq = QtWidgets.QSpinBox()
        self.sbFreq.setMaximum(10**5)
        if "sfreq" in settings.keys():
            self.sbFreq.setValue(settings["sfreq"])
        else:
            self.sbFreq.setValue(256)
        formLayout.insertRow(-1, lb, self.sbFreq)
        
        self.layout.addWidget(self.fileSelectWindow)
        self.layout.addItem(formLayout)
        
        self.setLayout(self.layout)
        
    def genSettings(self, settings, vars):
        
        self.fileSelectWindow.genSettings(settings, vars)
        
        settings["montage"] = self.montageLoad.textbox.text()
        settings["chanTypes"] = self.chanTypesLoad.textbox.text()
        settings["sfreq"] = self.sbFreq.value()
        
        vars["montageFile"] = self.montageLoad.textbox.text()
        vars["channelTypes"] = self.chanTypesLoad.textbox.text()
        vars["sfreq"] = self.sbFreq.value()
        
class ImportDataSettings(CustomSettings):
    def __init__(self, parent, settings):
        super(ImportDataSettings, self).__init__(parent, settings)
        
        
    def buildUI(self, settings):
        self.layout = QtWidgets.QVBoxLayout()
        
        typeLayout = QtWidgets.QHBoxLayout()
        lb = QtWidgets.QLabel("Data Type: ")
        
        self.cbType = QtWidgets.QComboBox()
        self.cbType.addItems(["BDF Files", "Numpy Files"])
        self.cbType.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed))
        
        self.widgetStack = QtWidgets.QStackedWidget(self)

        typeLayout.addWidget(lb)
        typeLayout.addWidget(self.cbType)
        
        if "currentTab" in settings.keys():
        
            if settings["currentTab"] == 0:
                self.BDF = BdfImport(settings)
            else:
                self.BDF = BdfImport({})
                
            if settings["currentTab"] == 1:
                self.numpy = NumpyImport(settings)
            else:
                self.numpy = NumpyImport({})
                
        else:
            self.BDF = BdfImport({})
            self.numpy = NumpyImport({})
            
        self.widgetStack.addWidget(self.BDF)
        self.widgetStack.addWidget(self.numpy)
        self.cbType.currentIndexChanged.connect(self.swapTab)
        
        if "currentTab" in settings.keys():
            self.cbType.setCurrentIndex(settings["currentTab"])
            self.widgetStack.setCurrentIndex(settings["currentTab"])
            
        self.cbFolders = QtWidgets.QCheckBox("Create folder for each input file")
        if "makeFolders" in settings.keys():
            self.cbFolders.setChecked(settings["makeFolders"])
        else:
            self.cbFolders.setChecked(True)
        
        self.layout.addItem(typeLayout)
        self.layout.addWidget(self.widgetStack)
        self.layout.addWidget(self.cbFolders)
        self.setLayout(self.layout)
        
    def swapTab(self, i):
        self.widgetStack.setCurrentIndex(i)
        
    def genSettings(self):
        settings = {}
        vars = {}
        
        settings["settingsFile"] = self.settings["settingsFile"]
        settings["settingsClass"] = self.settings["settingsClass"]
        
        settings["currentTab"] = self.cbType.currentIndex()
        vars["dataType"] = self.cbType.currentText()
        
        if vars["dataType"] == "BDF Files":
            self.BDF.genSettings(settings, vars)
        if vars["dataType"] == "Numpy Files":
            self.numpy.genSettings(settings, vars)
        
        settings["makeFolders"] = self.cbFolders.isChecked()
        vars["makeFolders"] = self.cbFolders.isChecked()
        
        self.parent.settings = settings
        self.parent.variables = vars
        
class importEEGData(Node):

    def __init__(self, name, params = None):
        super(importEEGData, self).__init__(name, params)
        
        assert(self.parameters["files"] is not ""), "ERROR: Import Data node has no input files set. Please update the node's settings and re-run"
        assert(self.parameters["montageFile"] is not ""), "ERROR: Import Data node has no montage file set. Please update the node's settings and re-run"
        
        if self.parameters["dataType"] == "Numpy Files":
            assert(self.parameters["channelTypes"] is not ""), "ERROR: Import Data node has no channel type file set. Please update the node's settings and re-run"
            
        dataCount = signal('eegNodeCount').send('node', count=len(self.parameters["files"]))
            
    def process(self):

        currentFile = self.parameters["files"][0]
        
        # BDF File import
        if self.parameters["dataType"] == "BDF Files":
            data = mne.io.read_raw_bdf(currentFile, stim_channel = -1)
            data.load_data()
            data.drop_channels(["EXG1", "EXG2", "EXG3", "EXG4", "EXG5", "EXG6", "EXG7", "EXG8"]) # FIXME
            
            # Need to split up the path name for the montage file
            montageFile = self.parameters["montageFile"]
            # Extract extensionless filename
            filename = os.path.basename(montageFile).split(".")[0]
            # Extract path
            filePath = os.path.dirname(montageFile)
            montage = mne.channels.read_montage(kind = filename, path = filePath)
            montage.ch_names = data.ch_names[:64] # FIXME - Temp hack while we wait for correct montage file
            data.set_montage(montage)
            
            events = mne.find_events(data, mask = self.parameters["mask"]) 
            
        # Numpy file import
        if self.parameters["dataType"] == "Numpy Files":
            data = np.load(currentFile)
            sfreq = self.parameters["sfreq"]
        
            trigTimes = data["SampleTime"][data["TriggerTime"] != 0.][:13] ## FIXME
            trigData = data["TriggerValues"]
            
            # Need to split up the path name for the montage file
            montageFile = self.parameters["montageFile"]
            filename = os.path.basename(montageFile).split(".")[0]
            filePath = os.path.dirname(montageFile)

            montage = mne.channels.read_montage(kind = filename, path = filePath)
            ch_names = montage.ch_names
            
            ch_types = open(self.parameters["channelTypes"], 'r').read().split(",")

            info = mne.create_info(ch_names = ch_names[-16:], sfreq = sfreq, ch_types = ch_types)
            raw = mne.io.RawArray(data["EEG"], info, first_samp = 0)
            
            raw.set_montage(montage, set_dig=True) 
            raw.pick_types(eeg=True,exclude='bads')
            raw.set_eeg_reference('average',projection=False)   
            
                    # MNE needs trigger data in a certain format
            events = np.concatenate((np.expand_dims(trigTimes*sfreq,axis=1),
                                           np.zeros((trigTimes.shape[0],1)),
                                           np.expand_dims(trigData,axis=1)),axis=1).astype(int)
                                           
            data = raw
                                           
        # Update the global filename variable with each new file
        # Useful for batch jobs where you want each dataset to output results with matching names     
        self.global_vars["Output Filename"] = os.path.splitext(os.path.split(currentFile)[1])[0]
            
        # Save output from each data file in its own folder
        if self.parameters["makeFolders"] == True:
            dir = os.path.join(self.global_vars["Output Folder"].getVal(), self.global_vars["Output Filename"])
            self.global_vars["Output Filename"] = os.path.join(self.global_vars["Output Filename"], self.global_vars["Output Filename"])
            if not os.path.isdir(dir):
                os.mkdir(dir)
                
            os.mkdir(os.path.join("wariotmp", self.global_vars["Output Filename"].split("\\")[0]))
                
        self.parameters["files"].pop(0)
        self.done = not len(self.parameters["files"]) > 0
                
        return{"Raw" : data, "Events" : events}