from pipeline.Node import Node
import mne 
import numpy as np
import os, sys
import matplotlib.pyplot as plt

from extensions.customSettings import CustomSettings

from PyQt5 import QtWidgets, QtCore, QtGui

class ImportDataSettings(CustomSettings):
    def __init__(self, parent, settings):
        super(ImportDataSettings, self).__init__(parent, settings)
        
        
class importEEGData(Node):

    def __init__(self, name, params = None):
        super(importEEGData, self).__init__(name, params)
        assert(self.parameters["file"] is not ""), "ERROR: Import Data node has no input file set. Please update the node's settings and re-run"
        
        self.parameters["updateGlobal"] = True
        self.parameters["makeFolders"] = True
        self.parameters["files"] = []
        
        path = "C://Users/mudwayt/Documents/CANARIE/EEG/testData/" 
        for dirpath, dnames, fnames in os.walk(path):   
            for fname in fnames:
                self.parameters["files"].append(dirpath + fname)
                
            break
        

    def process(self):
        np.set_printoptions(suppress=True)
        currentFile = self.parameters["files"][0]
        data = mne.io.read_raw_bdf(currentFile, stim_channel = -1)
        print(data.get_data(-1)[0])
        #plt.plot(np.right_shift(data.get_data(-1)[0].astype("uint"), 8))
        #plt.show()
        #print(np.unique(np.int16(data.get_data(-1)), return_counts = True))
        events = mne.find_events(data, uint_cast = True, mask = 2**8 - 1, min_duration = 0.1)
        print(events)
        epochs = mne.Epochs(data, events)
        print(epochs)
        epochs.plot()   
        # Update the global filename variable with each new file
        # Useful for batch jobs where you want each dataset to output results with matching names
        if self.parameters["updateGlobal"] == True:
            self.global_vars["Output Filename"] = os.path.splitext(os.path.split(currentFile)[1])[0]
            
        # Save output from each data file in its own folder
        if self.parameters["makeFolders"] == True:
            dir = os.path.join(self.global_vars["Output Folder"].getVal(), self.global_vars["Output Filename"])
            self.global_vars["Output Filename"] = os.path.join(self.global_vars["Output Filename"], self.global_vars["Output Filename"])
            if not os.path.isdir(dir):
                os.mkdir(dir)
                
        return{"Raw" : data, "Triggers" : events}