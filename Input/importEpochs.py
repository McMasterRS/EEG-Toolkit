from wario import Node
from wario.CustomSettings import CustomSettings
from wario.CustomWidgets import loadWidget
from PyQt5 import QtWidgets
import mne

class ImportEpochSettings(CustomSettings):
    def __init__(self, parent, settings):
        super(ImportEpochSettings, self).__init__(parent, settings)
        
    def buildUI(self, settings):
        self.layout = QtWidgets.QHBoxLayout()
        
        self.loadWidget = loadWidget(self, "Epoch File (*.fif)")
        self.loadWidget.loadSettings(settings)
        self.layout.addItem(self.loadWidget)
        
        self.setLayout(self.layout)
        
    def genSettings(self):
        settings = {}
        vars = {}
        settings["settingsFile"] = self.settings["settingsFile"]
        settings["settingsClass"] = self.settings["settingsClass"]
        
        self.loadWidget.genSettings(settings, vars)
        
        self.parent.settings = settings
        self.parent.variables = vars

class importEpochs(Node):
    def __init__(self, name, params):
        super(importEpochs, self).__init__(name, params)
        
    def process(self):   
        data = mne.read_epochs(self.parameters["filename"])  
        return {"Epoch Data" : data}