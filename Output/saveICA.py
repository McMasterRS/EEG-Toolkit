from wario import Node
import mne

class saveICA(Node):

    def __init__(self, name, params):
        super(saveICA, self).__init__(name, params)
        assert (self.parameters["file"] is not ""), "ERROR: No filename given in 'Save ICA' node. Please update the node settings and re-run"
        
    def process(self):
    
        ICA = self.args["ICA Solution"]
        
        if "globalSaveStart" in self.parameters.keys():
            f = self.parameters["globalSaveStart"] + self.global_vars["Output Filename"] + self.parameters["globalSaveEnd"]
        else:
            f = self.parameters["file"]
        
        ICA.save(f)
