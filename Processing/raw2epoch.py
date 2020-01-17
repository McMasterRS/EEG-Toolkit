from pipeline.Node import Node
from extensions.customSettings import CustomSettings
from extensions.customWidgets import LinkedCheckbox, ExpandingTable
import mne
import numpy as np

from PyQt5 import QtWidgets
from PyQt5 import QtCore

class Raw2EpochSettings(CustomSettings):
    
    def __init__(self, parent, settings):
        super(Raw2EpochSettings, self).__init__(parent, settings)

    # Build the settings UI
    def buildUI(self, settings):
        self.baseLayout = QtWidgets.QVBoxLayout()
        self.layout = QtWidgets.QFormLayout()
        
        # Minimum time
        self.tminWidget = QtWidgets.QSpinBox()
        self.tminWidget.setMinimum(-1000)
        self.tminWidget.setMaximum(0)
        if "tminValue" in settings.keys():
            self.tminWidget.setValue(settings["tminValue"])
        else:
            self.tminWidget.setValue(0.0)
        self.tminLabel = QtWidgets.QLabel("TMin")
        self.layout.insertRow(-1, self.tminLabel, self.tminWidget)
        
        # Maximum time
        self.tmaxWidget = QtWidgets.QSpinBox()
        self.tmaxWidget.setMinimum(1)
        self.tmaxWidget.setMaximum(1000)
        if "tmaxValue" in settings.keys():
            self.tmaxWidget.setValue(settings["tmaxValue"])
        self.tmaxLabel = QtWidgets.QLabel("TMax")
        self.layout.insertRow(-1, self.tmaxLabel, self.tmaxWidget)
        
        # Detrend type
        self.detrendWidget = QtWidgets.QComboBox()
        self.detrendWidget.addItems(["Constant", "Linear"])
        self.detrendLabel = LinkedCheckbox("Detrend Type", self.detrendWidget)
        self.detrendLabel.buildLinkedCheckbox("detrend", self.settings)
        self.layout.insertRow(-1, self.detrendLabel, self.detrendWidget)
        
        # Verbose type
        self.verboseWidget = QtWidgets.QComboBox()
        self.verboseWidget.addItems(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
        self.verboseLabel = LinkedCheckbox("Verbose Type", self.verboseWidget)
        self.verboseLabel.buildLinkedCheckbox("verbose", self.settings)
        self.layout.insertRow(-1, self.verboseLabel, self.verboseWidget)
        
        # Baseline
        self.baselineMin = QtWidgets.QDoubleSpinBox()
        self.baselineMin.setMinimum(-10000.0)
        self.baselineMin.setMaximum(10000.0)
        if "baselineMin" not in settings.keys():
            self.baselineMin.setValue(-0.2)
        else:
            self.baselineMin.setValue(settings["baselineMin"])
            
        self.baselineMinLabel = LinkedCheckbox("Baseline Min Time", self.baselineMin)
        self.baselineMinLabel.buildLinkedCheckbox("baselineMin", self.settings)
        self.layout.insertRow(-1, self.baselineMinLabel, self.baselineMin)
        
        self.baselineMax = QtWidgets.QDoubleSpinBox()
        self.baselineMax.setMinimum(-10000.0)
        self.baselineMax.setMaximum(10000.0)
        if "baselineMax" not in settings.keys():
            self.baselineMax.setValue(0)
        else:
            self.baselineMax.setValue(settings["baselineMax"])
            
        self.baselineMaxLabel = LinkedCheckbox("Baseline Max Time", self.baselineMax)
        self.baselineMaxLabel.buildLinkedCheckbox("baselineMax", self.settings)
        self.layout.insertRow(-1, self.baselineMaxLabel, self.baselineMax)
     
        self.baseLayout.addItem(self.layout)
        
        self.setLayout(self.baseLayout)
        
    # Return the values from each setting type
    def genSettings(self):
        settings = {}
        vars = {}
        settings["settingsFile"] = self.settings["settingsFile"]
        settings["settingsClass"] = self.settings["settingsClass"]
        
        settings["tminValue"] = self.tminWidget.value()
        settings["tmaxValue"] = self.tmaxWidget.value()
        vars["tmin"] = settings["tminValue"]
        vars["tmax"] = settings["tmaxValue"]
        
        settings["baselineMin"] = self.baselineMin.value()
        settings["baselineMax"] = self.baselineMax.value()
        self.baselineMinLabel.getSettings("baselineMin", vars, settings)
        self.baselineMaxLabel.getSettings("baselineMax", vars, settings)
        
        if self.baselineMinLabel.isChecked():
            vars["baselineMin"] = self.baselineMin.value()
        else:
            vars["baselineMin"] = None
            
        if self.baselineMaxLabel.isChecked():    
            vars["baselineMax"] = self.baselineMax.value()
        else:
            vars["baselineMax"] = None
            
        self.detrendLabel.getSettings("detrend", vars, settings)
        self.verboseLabel.getSettings("verbose", vars, settings)
              
        self.parent.settings = settings
        self.parent.variables = vars

class raw2epoch(Node):

    def __init__(self, name, params):
        super(raw2epoch, self).__init__(name, params)
        
        
    def process(self):
        '''
        Takes an MNE Raw object and trigger data and creates anan Epochs object 
        and Evoked object.
        '''
        Raw = self.args["Raw"]
        sfreq = Raw.info['sfreq']
        
        verboseDict = {None : None, 0 : "DEBUG", 1 : "INFO", 2 : "WARNING", 3 : "ERROR", 4 : "CRITICAL"}
        
        
        idList = self.global_vars["Event Names"].getVal()
        eventIDs = {}
        for i, id in enumerate(idList):
            eventIDs[id[1]] = int(id[0])
        
        print("Converting raw file into epoch data")

        # create Epochs object
        Epochs = mne.Epochs(Raw, 
                            events=self.args["Events"],
                            preload=True, 
                            event_id = eventIDs,
                            proj=False, 
                            picks="eeg", 
                            baseline=(None, None),
                            reject=None, 
                            flat=None,
                            reject_by_annotation=True,
                            detrend=self.parameters["detrend"], 
                            verbose=verboseDict[self.parameters["verbose"]],
                            tmin=self.parameters["tmin"], 
                            tmax=self.parameters["tmax"])

        return {"Epoch Data" : Epochs}