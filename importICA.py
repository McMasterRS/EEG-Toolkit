from pipeline.Node import Node
import mne

class importICA(Node):
    def __init__(self, name, params):
        super(importICA, self).__init__(name, params)
        
    def process(self):   
        data = mne.preprocessing.read_ica(self.parameters["filename"])  
        return {"ICA Solution" : data}