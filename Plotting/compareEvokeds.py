from wario import Node
from wario.CustomSettings import CustomSettings
import mne
import matplotlib.pyplot as plt
import pickle
import tempfile
import os

from PyQt5 import QtWidgets
from PyQt5 import QtCore

class compareEvokeds(Node):

    def __init__(self, name, params):
        super(compareEvokeds, self).__init__(name, params)
    
    def process(self):
        evokedData = self.args["Evoked Data"]
        evokedDict = {}
        for evoked in evokedData:
            evokedDict[evoked.comment] = evoked
            
        figs = mne.viz.plot_compare_evokeds(evokedDict, show = False)
        for fig in figs:
            if self.parameters["saveGraph"] is not None:
                if "globalSaveStart" in self.parameters.keys():
                    f = self.parameters["globalSaveStart"] + self.global_vars["Output Filename"] + self.parameters["globalSaveEnd"]
                else:
                    f = self.parameters["saveGraph"]
                type = f.split(".")[-1]
                if type == "png":
                    fig.savefig(f, dpi = 300, format = "png")
                elif type == "pdf":
                    fig.savefig(f, format = "pdf")
                elif type == "pkl":
                    pickle.dump(fig, open(f, "wb"))
        
        data = {"type" : "showMulti", "data" : figs}
        name = os.path.join(".", "wariotmp", self.global_vars["Output Filename"].split("\\")[0], self.node_id)
        pickle.dump(data, open(name, 'wb'))
                    
        plt.close(fig)
