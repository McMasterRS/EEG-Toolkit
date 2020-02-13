from wario import Node
import mne
import os
import pickle
import tempfile
import matplotlib.pyplot as plt

class plotComponents(Node):
    def __init__(self, name, params):
        super(plotComponents, self).__init__(name, params)
        
        if self.parameters["saveGraph"] is not None:
            assert(self.parameters["saveGraph"] is not ""), "ERROR: Plot Components node set to save but no filename has been given. Please update the node settings and re-run"

    def process(self):

        ica = self.args["ICA Solution"]
        figs = ica.plot_components(show = False)
                
        if self.parameters["saveGraph"] is not None:
            for i, fig in enumerate(figs):
                if "globalSaveStart" in self.parameters.keys():
                    f = self.parameters["globalSaveStart"] + self.global_vars["Output Filename"] + self.parameters["globalSaveEnd"]
                else:
                    f = self.parameters["saveGraph"]
                name = f.split(".")[0]
                type = f.split(".")[-1]
                f = name + "_" +  str(i) + "." + type
                if type == "png":
                    fig.savefig(f, dpi = 300, format = "png")
                elif type == "pdf":
                    fig.savefig(f, format = "pdf")
                elif type == "pkl":
                    pickle.dump(fig, open(f, "wb"))
                

        data = {"type" : "showMulti", "data" : figs}
        name = os.path.join(".", "wariotmp", self.global_vars["Output Filename"].split("\\")[0], self.node_id)
        pickle.dump(data, open(name, 'wb'))
                    
        for fig in figs:
            plt.close(fig)