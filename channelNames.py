from wario.GlobalWidgets import GlobalWindowWidget
from PyQt5 import QtWidgets
import numpy as np
import os
import mne

class GlobalChannelNames(GlobalWindowWidget):
    def __init__(self):
        super(GlobalChannelNames, self).__init__()
        
        self.fileBox = QtWidgets.QLineEdit()
        
        self.saveButton = QtWidgets.QPushButton("Load")
        width = self.saveButton.fontMetrics().boundingRect("Load").width() + 15
        self.saveButton.setMaximumWidth(width)
        self.saveButton.clicked.connect(self.getFile)
        
        self.layout.addWidget(self.fileBox)
        self.layout.addWidget(self.saveButton)
        
        self.channelNames = []
        
        self.cls = "GlobalChannelNames"
        self.file = "channelNames.py"
        self.toolkit = "EEG"
        
    def getFile(self):
        dialog = QtWidgets.QFileDialog.getOpenFileName(self, "Select File")
        if (dialog[0] != ''):
            self.fileBox.setText(dialog[0])
            
        self.updateChannelNames()
            
    def getData(self):
        return(self.channelNames)
        
    def setData(self, gb):
        self.channelNames = gb["value"]
        if "text" in gb["properties"]:
            self.fileBox.setText(gb["properties"]["text"])
        
    def getProperties(self):
        return {"text" : self.fileBox.text()}
        
    def updateChannelNames(self):
        file = self.fileBox.text()
        ext = file.split(".")[-1]
        
        # Text format
        if ext == "txt":
            f = open(file, "r")
            self.channelNames = f.readlines()
            f.close()
            return
        
        # EEG format
        elif ext == "edf":
            data = mne.io.read_raw_edf(file)
        elif ext == "bdf":
            data = mne.io.read_raw_bdf(file)
        elif ext == "gdf":
            data = mne.io.read_raw_gdf(file)
            
        # Montage file
        elif ext == "sfp":
            filename = os.path.basename(file).split(".")[0]
            filePath = os.path.dirname(file)

            data = mne.channels.read_montage(kind = filename, path = filePath)
            
        else:
            error_dialog = QtWidgets.QErrorMessage()
            error_dialog.showMessage('Invalid file selected')
            return
            
        self.channelNames = data.ch_names
        