from wario import Node
from wario.CustomSettings import CustomSettings
import mne
import numpy as np
import matplotlib.pyplot as plt

from PyQt5 import QtWidgets
from PyQt5 import QtCore

import pickle
import tempfile

class evokedCustomTimes(Node):

    def __init__(self, name, params):
        super(evokedCustomTimes, self).__init__(name, params)
    
    def process(self):
    
        evokedData = self.args["Evoked Data"]
        for i, evoked in enumerate(evokedData):
        
            max = evoked.times[-1]
            chName, latency, amplitude = evoked.get_peak(return_amplitude = True)
            fig = evoked.plot_joint(title = "Event ID {0}".format(evoked.comment),
                              times=np.arange(max / 10.0, max, max / 10.0), show = False)      
                
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
                    
            if self.parameters["showGraph"] == True:
                with tempfile.NamedTemporaryFile(dir='./wariotmp/plots/', delete=False) as temp:
                    data = {"type" : "customTimes", "data" : evoked}
                    pickle.dump(data, open(temp.name, 'wb'))
                    
            plt.close(fig)
        
        return
