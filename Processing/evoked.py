from wario import Node
from wario import CustomSettings
from wario.CustomWidgets import ExpandingTable
import mne

from PyQt5 import QtWidgets
from PyQt5 import QtCore

class EvokedSettings(CustomSettings):
    def __init__(self, parent, settings):
        super(EvokedSettings, self).__init__(parent, settings)
        
    # Build the settings UI
    def buildUI(self, settings):
        self.layout = QtWidgets.QFormLayout()
        self.eventIDWidget = ExpandingTable("eventIDs", settings)
        self.eventIDWidget.setHorizontalHeaderLabels(["Event ID"])
        #self.layout.addWidget(self.eventIDWidget)
        
        self.setLayout(self.layout)
        
    def genSettings(self):
    
        settings = {}
        vars = {}
        
        settings["settingsFile"] = self.settings["settingsFile"]
        settings["settingsClass"] = self.settings["settingsClass"]
        
        #self.eventIDWidget.getSettings("eventIDs", vars, settings)
        
        self.parent.settings = settings
        self.parent.variables = vars

class evoked(Node):

    def __init__(self, name, params):   
        super(evoked, self).__init__(name, params)
    
    def process(self):
        epochs = self.args["Epoch Data"]
        
        eventIDs = [str(i[1]) for i in self.global_vars["Event Names"].getVal()]
        
        # create Evoked object
        evoked = [epochs[name].average() for name in eventIDs]
        for i, name in enumerate(eventIDs):
            evoked[i].comment = name[1]
        
        return {"Evoked Data" : evoked}