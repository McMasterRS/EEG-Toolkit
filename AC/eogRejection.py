from pipeline.Node import Node
import mne

class eogRejection(Node):

    def __init__(self, name, params):
        super(eogRejection, self).__init__(name, params)
        
        
    def process(self):
        print("Beep")
        raw = self.args["Raw"]
        ica = self.args["ICA Solution"]
        raw.filter(1, 20, picks=["A1", "B1"], n_jobs=4, fir_design='firwin')
        ch_names = ["A1", "B1"]
        eog_inds = []
        for name in ch_names:
            eog_epochs = mne.preprocessing.create_eog_epochs(raw.copy(), ch_name=name)
            inds, scores = ica.find_bads_eog(eog_epochs, ch_name=name, h_freq=15, threshold=1.5, reject_by_annotation=True)
            eog_inds.extend(inds)

        eog_inds = list(set(eog_inds))
        nInds = len(eog_inds)
        ica.exclude.extend(eog_inds)
        
        return {"Corrected ICA" : ica}