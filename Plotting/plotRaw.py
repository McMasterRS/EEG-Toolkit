from wario import Node
import mne
import pickle
import tempfile
import matplotlib.pyplot as plt
import os

class plotRaw(Node):
    def __init__(self, name, params):
        super(plotRaw, self).__init__(name, params)
        
        if self.parameters["saveGraph"] is not None:
            assert(self.parameters["saveGraph"] is not ""), "ERROR: Plot Raw node set to save but no filename has been given. Please update the node settings and re-run"

    def process(self):

        raw = self.args["Raw"]
        fig = raw.plot(show = False)
            
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
                    
        data = {"data" : raw, "type" : "raw"}
        name = os.path.join(".", "wariotmp", self.global_vars["Output Filename"].split("\\")[0], self.node_id)
        pickle.dump(data, open(name, 'wb'))
                    
        plt.close(fig)