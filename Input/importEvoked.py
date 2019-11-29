from pipeline.Node import Node
import mne

class importEvoked(Node):
    def __init__(self, name, params):
        super(importEvoked, self).__init__(name, params)
        
    def process(self):   
        data = mne.Evoked(self.parameters["filename"])  
        return {"Evoked Data" : data}