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
        
        self.eventIDWidget = ExpandingTable("eventIDs", settings)
        self.eventIDWidget.setHorizontalHeaderLabels(["Event ID"])
        
        self.baseLayout.addItem(self.layout)
        self.baseLayout.addWidget(self.eventIDWidget)
        
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
        
        self.detrendLabel.getSettings("detrend", vars, settings)
        self.verboseLabel.getSettings("verbose", vars, settings)
        
        self.eventIDWidget.getSettings("eventIDs", vars, settings)
        
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
        
        T = self.args["Trigger Times/Values"][1]
        Y = self.args["Trigger Times/Values"][0]
        
        print("Converting raw file into epoch data")
        
        # MNE needs trigger data in a certain format
        trigger_data = np.concatenate((np.expand_dims(T*sfreq,axis=1),
                                       np.zeros((T.shape[0],1)),
                                       np.expand_dims(Y,axis=1)),axis=1).astype(int)
        
        # create Epochs object
        Epochs = mne.Epochs(Raw, 
                            events=trigger_data, 
                            event_id = self.parameters["eventIDs"],
                            tmin=-self.parameters["tmin"], 
                            tmax=self.parameters["tmax"],
                            proj=False, 
                            picks="eeg", 
                            baseline=(None,None),
                            reject=None, 
                            flat=None, 
                            preload=True, 
                            reject_by_annotation=True,
                            detrend=self.parameters["detrend"], 
                            verbose=verboseDict[self.parameters["verbose"]])
  
        return {"Epoch Data" : Epochs, "Trigger Data" :trigger_data}