from wario import Node
from wario.CustomSettings import CustomSettings
from wario.CustomWidgets import ExpandingTable
import mne
from PyQt5 import QtWidgets

class RereferenceSettings(CustomSettings):
    def __init__(self, parent, settings):
        super(RereferenceSettings, self).__init__(parent, settings)
        
    def buildUI(self, settings):
        self.layout = QtWidgets.QVBoxLayout()
        
        self.table = ExpandingTable("target", settings)
        self.table.setHorizontalHeaderLabels(["Referencing Target"])
        self.layout.addWidget(self.table)
        
        addLayout = QtWidgets.QHBoxLayout()
        
        self.btAdd = QtWidgets.QPushButton("Add")
        self.btAdd.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.btAdd.clicked.connect(self.addRow)
        addLayout.addWidget(self.btAdd)
        
        self.cbTypes = QtWidgets.QComboBox()
        self.cbTypes.addItems(["Average"])
        addLayout.addWidget(self.cbTypes)
        
        addLayout.setSpacing(5)
        self.layout.addItem(addLayout)
        
        # Holds the selected channel so that the first global update can select it
        self.channelHold = ""
        if "reference" in settings.keys():
            self.channelHold = settings["reference"]

        self.setLayout(self.layout)
        
    def addRow(self):
        self.table.setItem(self.table.rowCount() - 1, 0, QtWidgets.QTableWidgetItem(self.cbTypes.currentText()))
        
    def genSettings(self):
        settings = {}
        vars = {}
        
        settings["settingsFile"] = self.settings["settingsFile"]
        settings["settingsClass"] = self.settings["settingsClass"]
        
        self.table.getSettings("target", vars, settings)
        
        self.parent.settings = settings
        self.parent.variables = vars
        
    def updateGlobals(self, globals):
        
        if "Channel Names" not in globals.keys():
            return
        
        currentType = self.cbTypes.currentText()
        typeList = ["Average"]
        for ch in globals["Channel Names"]["value"]:
            typeList.append(ch)
        
        while self.cbTypes.count() > 0:
            self.cbTypes.removeItem(0)
            
        self.cbTypes.addItems(typeList)
        
        # Update with saved value when needed
        if self.channelHold != "":  
            i = self.cbTypes.findText(self.channelHold)
            # Only update when the value is found
            if (i != -1):
                self.cbTypes.setCurrentIndex(i)
                self.channelHold = ""
        else:
            self.cbTypes.setCurrentText(currentType)
        

class rereference(Node):

    # Re-reference the data
    def __init__(self, name, params):
        super(rereference, self).__init__(name, params)
    
    def process(self):
        data = self.args["Raw"]
        
        reference = list(self.parameters["target"].keys())
        if reference == ["Average"]:
            reference = "average"
            data.set_eeg_reference('average', projection=False)
        else:
            data, _ = mne.set_eeg_reference(data, reference)
        
        return {"Re-referenced Raw" : data}   
