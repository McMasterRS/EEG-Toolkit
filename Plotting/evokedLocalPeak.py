from wario import Node
from wario.CustomSettings import CustomSettings
from wario.CustomWidgets import BatchSaveTab
import mne
import numpy as np
import matplotlib.pyplot as plt
import os

from PyQt5 import QtWidgets
from PyQt5 import QtCore

import pickle
import tempfile

class EvokedLocalPeakSettings(CustomSettings):
    def __init__(self, parent, settings):
        super(EvokedLocalPeakSettings, self).__init__(parent, settings)
        
    # Build the settings UI
    def buildUI(self, settings):
        self.layout = QtWidgets.QFormLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        self.saveTab = BatchSaveTab("Graph", "graph", settings, pkl = False)
        self.layout.addWidget(self.saveTab)
        
        self.setLayout(self.layout)
        
    def genSettings(self):
    
        settings = {}
        vars = {}
        
        settings["settingsFile"] = self.settings["settingsFile"]
        settings["settingsClass"] = self.settings["settingsClass"]
        
        self.saveTab.genSettings(settings, vars)
        
        self.parent.settings = settings
        self.parent.variables = vars
        
    def updateGlobals(self, globals):
        self.saveTab.updateGlobals(globals)

class evokedLocalPeak(Node):

    def __init__(self, name, params):
        super(evokedLocalPeak, self).__init__(name, params)
    
    def process(self):
    
        evokedData = self.args["Evoked Data"]
        for i, evoked in enumerate(evokedData):
            chName, latency, amplitude = evoked.get_peak(return_amplitude = True)
            fig = evoked.plot_joint(title = "Local Peaks for event ID {0}".format(evoked.comment), show = False)
            
            if self.parameters["saveGraph"] is not None:
                if "globalSaveStart" in self.parameters.keys():
                    f = self.parameters["globalSaveStart"] + self.global_vars["Output Filename"] + self.parameters["globalSaveEnd"]
                else:
                    f = self.parameters["saveGraphGraph"]
                type = f.split(".")[-1]
                name = f.split(".")[0]
                f = name + "_{0}.".format(i) + type
                if type == "png":
                    fig.savefig(f, dpi = 300, format = "png")
                elif type == "pdf":
                    fig.savefig(f, format = "pdf")
                elif type == "pkl":
                    pickle.dump(fig, open(f, "wb"))
                
            data = {"type" : "localPeak", "data" : evoked}
            name = os.path.join(".", "wariotmp", self.global_vars["Output Filename"].split("\\")[0], self.node_id + "." + evoked.comment)
            pickle.dump(data, open(name, 'wb'))
            plt.close(fig)