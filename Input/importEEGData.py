from pipeline.Node import Node
import mne 
import numpy as np
import os, sys
import matplotlib.pyplot as plt

from extensions.customSettings import CustomSettings
from extensions.customWidgets import loadWidget, LinkedCheckbox

from PyQt5 import QtWidgets, QtCore, QtGui

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
        
        self.fileSelect.genSettings(settings, vars)
        
        settings["montage"] = self.montageLoad.textbox.text()
        settings["chanTypes"] = self.chanTypesLoad.textbox.text()
        settings["sfreq"] = self.sbFreq.currentValue()
        
        vars["montageFile"] = self.montageLoad.textbox.text()
        vars["channelTypes"] = self.chanTypesLoad.textbox.text()
        vars["sfreq"] = self.sbFreq.currentValue()
        
class ImportDataSettings(CustomSettings):
    def __init__(self, parent, settings):
        super(ImportDataSettings, self).__init__(parent, settings)
        
        
    def buildUI(self, settings):
        self.layout = QtWidgets.QVBoxLayout()
        
        self.tabWindow = QtWidgets.QTabWidget()
        self.BDF = BdfImport(settings)
        self.numpy = NumpyImport(settings)
        self.tabWindow.addTab(self.BDF, "BDF Files")
        self.tabWindow.addTab(self.numpy, "Numpy Files")
            
        self.cbFolders = QtWidgets.QCheckBox("Create folder for each input file")
        if "makeFolders" in settings.keys():
            self.cbFolders.setChecked(settings["makeFolders"])
        else:
            self.cbFolders.setChecked(True)
        
        self.layout.addWidget(self.tabWindow)
        self.layout.addWidget(self.cbFolders)
        self.setLayout(self.layout)
        
    def genSettings(self):
        settings = {}
        vars = {}
        
        settings["settingsFile"] = self.settings["settingsFile"]
        settings["settingsClass"] = self.settings["settingsClass"]
        
        settings["currentTab"] = self.tabWindow.currentIndex()
        vars["dataType"] = self.tabWindow.tabText(self.tabWindow.currentIndex())
        
        self.BDF.genSettings(settings, vars)
        
        settings["makeFolders"] = self.cbFolders.isChecked()
        vars["makeFolders"] = self.cbFolders.isChecked()
        
        self.parent.settings = settings
        self.parent.variables = vars
        
class importEEGData(Node):

    def __init__(self, name, params = None):
        super(importEEGData, self).__init__(name, params)
        
        assert(self.parameters["file"] is not ""), "ERROR: Import Data node has no input files set. Please update the node's settings and re-run"
        assert(self.parameters["montageFile"] is not ""), "ERROR: Import Data node has no montage file set. Please update the node's settings and re-run"
        
        if self.parameters["dataType"] == "Numpy Files":
            assert(self.parameters["channelTypes"] is not ""), "ERROR: Import Data node has no channel type file set. Please update the node's settings and re-run"
            
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
            sfreq = self.parameters["sfreq"]
        
            trigTimes = data["SampleTime"][data["TriggerTime"] != 0.][:13] ## FIXME
            trigData = [data["TriggerValues"], trigTimes]
            
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
            events = np.concatenate((np.expand_dims(T*sfreq,axis=1),
                                           np.zeros((T.shape[0],1)),
                                           np.expand_dims(Y,axis=1)),axis=1).astype(int)
                                           
        # Update the global filename variable with each new file
        # Useful for batch jobs where you want each dataset to output results with matching names     
        self.global_vars["Output Filename"] = os.path.splitext(os.path.split(currentFile)[1])[0]
            
        # Save output from each data file in its own folder
        if self.parameters["makeFolders"] == True:
            dir = os.path.join(self.global_vars["Output Folder"].getVal(), self.global_vars["Output Filename"])
            self.global_vars["Output Filename"] = os.path.join(self.global_vars["Output Filename"], self.global_vars["Output Filename"])
            if not os.path.isdir(dir):
                os.mkdir(dir)
                
        self.parameters["files"].pop(0)
        self.done = not len(self.parameters["files"]) > 0
                
        return{"Raw" : data, "Events" : events}