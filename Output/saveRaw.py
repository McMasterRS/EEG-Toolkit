from wario import Node
import mne
import sys

class saveRaw(Node):

    def __init__(self, name, params):
        super(saveRaw, self).__init__(name, params)
        assert (self.parameters["file"] is not ""), "ERROR: No filename given in 'Save Raw' node. Please update the node settings and re-run"
        
        
    def process(self):
    
        if "globalSaveStart" in self.parameters.keys():
            f = self.parameters["globalSaveStart"] + self.global_vars["Output Filename"] + self.parameters["globalSaveEnd"]
        else:
            f = self.parameters["file"]
                
        self.args["Raw"].save(f, overwrite = True)
        return 