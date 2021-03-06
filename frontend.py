from wario import PipelineThread

from PyQt5.QtCore import *
from PyQt5 import QtWidgets, QtGui, uic
from blinker import signal
import sys, os, shutil
import pickle

import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt

import mne
import numpy as np

from WarioEditor.extensions.WalkTree import WalkTree, TreeItem

def runPipeline(file):
    threadhandler = ThreadHandler()
    threadhandler.show()
    threadhandler.startPipeline(file)
    
def getIcon(str):
    return QtWidgets.QWidget().style().standardIcon(getattr(QtWidgets.QStyle,str))
    
def getHandler(file):
    handler = ThreadHandler()
    handler.show()
    handler.startPipeline(file)
    return handler

class ThreadHandler(QtWidgets.QWidget):
    pipelineComplete = pyqtSignal(bool)
    
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        
        self.running = False
        
        # Pipeline running variables
        signal("end").connect(self.finishRun)
        signal("crash").connect(self.updateCrash)
        self.pipelineComplete.connect(self.showPlots)
        
        # Progress tracking variables
        signal('node complete').connect(self.incrimentCount)        
        signal('eegNodeCount').connect(self.getCount)
       
        
        uiFile = os.path.join(os.path.dirname(os.path.realpath(__file__)), "eegWindow.ui")
        uic.loadUi(uiFile, self)
        self.treeWidget.itemClicked.connect(self.showPlot)
        self.progress.setValue(0)
        
        self.btStop.clicked.connect(self.stopRun)
         
        self.treeItem = {}
        self.walk = {}
        self.currentPlot = None
        
        self.nodeCount = 0
        self.numNodes = 1
        self.numNodesMultiplyer = 1
        
    def startPipeline(self, file):
    
        self.thread = PipelineThread(file)
        self.walk = WalkTree(file)
        self.numNodes = len(self.walk.nodes)
        self.treeWidget.clear()
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateProgress)
        self.timer.start(50)

        # Build temporary files
        if os.path.exists("./wariotmp"):
            shutil.rmtree("./wariotmp/")
        
        os.makedirs("./wariotmp")
    
        self.thread.file = file
        self.lbStatus.setText("Running")
        self.updatePalette("#0000FF")
        
        self.running = True
        self.thread.start()
        
    def getCount(self, sender, **kw):
        self.numNodesMultiplyer = kw["count"]
        
    def incrimentCount(self, sender, **kw):
        self.nodeCount += 1
        
    def updateProgress(self):
        self.progress.setValue(100 * (self.nodeCount) / (self.numNodes * self.numNodesMultiplyer))
    
    def updatePalette(self, color):
        palette = self.lbStatus.palette()
        palette.setColor(palette.Foreground, QtGui.QColor(color))
        self.lbStatus.setPalette(palette)
        
    def updateCrash(self, sender):
        self.lbStatus.setText("Crash - See terminal")
        self.updatePalette("#FF0000")
        self.running = False
        
    def stopRun(self):
        if self.running == True:
            self.thread.kill()
            self.thread.join()
            
            self.lbStatus.setText("Run Stopped")
            self.updatePalette("#FF0000")
            
            self.running = False
        
    # Swap from Blinker signal to PyQt5 signal to preserve
    # plots after thread dies.
    def finishRun(self, sender):
        self.lbStatus.setText("Complete")
        self.updatePalette("#00FF00")
        self.running = False
        self.pipelineComplete.emit(True)
    
    def showPlot(self, item, column):
        
        if item.file is None:
            return
            
        f = pickle.load(open(item.file, 'rb'))
        
        if self.currentPlot is not None:
            plt.close('all')
            
        if f["type"] == "show":
            self.currentPlot = f["data"]
            self.currentPlot.show()
        elif f["type"] == "showMulti":
            for d in f["data"]:
                d.show()
            self.currentPlot = f["data"]
        elif f["type"] == "raw":
            self.currentPlot = f["data"].plot(show = False, scalings = 'auto')
            self.currentPlot.set_size_inches(8, 6)
            self.currentPlot.show()
        elif f["type"] == "sources":
            self.currentPlot = f["ica"].plot_sources(f["data"], show = False)
            self.currentPlot.show()
        elif f["type"] == "customTimes":
            evoked = f["data"]
            max = evoked.times[-1]
            chName, latency, amplitude = evoked.get_peak(return_amplitude = True)
            self.currentPlot = evoked.plot_joint(title = "Event ID {0}".format(evoked.comment),
                  times=np.arange(max / 10.0, max, max / 10.0), show = False)
            self.currentPlot.show()             
        elif f["type"] == "localPeak":
            evoked = f["data"]
            chName, latency, amplitude = evoked.get_peak(return_amplitude = True)
            self.currentPlot = evoked.plot_joint(title = "Local Peaks for event ID {0}".format(evoked.comment), show = False)
            self.currentPlot.show()
            
        elif f["type"] == "peak":
            evoked = f["data"]
            chName, latency, amplitude = evoked.get_peak(return_amplitude = True)
            self.currentPlot = evoked.plot_joint(title = "Peak for event ID {0}".format(evoked.comment), times=latency, show = False)
            self.currentPlot.show()
        elif f["type"] == "batchAnalysis":
            data = f["data"]
            
            fig, ax = plt.subplots()
            width = 0.35
            for i in range(len(meanLatencies)):
                ax.bar(np.arange(len(meanLatencies[i])) + width * i, meanLatencies.transpose(2, 0, 1)[0][i], yerr = stdevLatencies.transpose(2, 0, 1)[0][i], width = width, align = 'center')
                
            ax.set_xticks(np.arange(len(meanLatencies[i])))
            ax.set_xticklabels(self.chanNames)
            ax.set_title("Mean Peak Latencies".format(self.eventNames[i]))
            ax.set_ylabel("Mean Peak Latency")
            ax.set_xlabel("Channel")
            
            fig.tight_layout()
            fig.legend(self.eventNames, title = "Event ID", framealpha = 1)
            
    def showPlots(self, val):

        # Walk through the tree and build the base layout for each output
        for root, directories, files in os.walk(os.path.join(".", "wariotmp")):
            for dir in directories:
                dirRoot = TreeItem(self.treeWidget, [dir], None)
                self.treeItem[dir] = self.walk.buildWidget(dirRoot)
        
                # Add the plots for each output
                for f in os.listdir(os.path.join(".", "wariotmp", dir)): 
                    splitName = f.split(".")
                    node = splitName[0]
                    if len(splitName) == 1:
                        self.treeItem[dir][node].file = os.path.join(".", "wariotmp", dir, f)
                        self.treeItem[dir][node].setIcon(0, getIcon("SP_FileDialogContentsView"))
                    else:
                        self.treeItem[dir][f] = TreeItem(self.treeItem[dir][node], [splitName[1]], None)
                        self.treeItem[dir][f].file = os.path.join(".", "wariotmp", dir, f)
                        self.treeItem[dir][f].setIcon(0, getIcon("SP_FileDialogContentsView"))
            
        for f in os.listdir(os.path.join(".", "wariotmp")): 
            if os.path.isdir(os.path.join(".", "wariotmp", f)):
                continue
                
            if "bulk" not in self.treeItem.keys():
                self.treeItem["bulk"] = TreeItem(self.treeWidget, ["Grand Results"], None)
                
            item = TreeItem(self.treeItem["bulk"], [f], None)
            item.file = os.path.join(".", "wariotmp", f)
            item.setIcon(0, getIcon("SP_FileDialogContentsView"))

if __name__ == "__main__":

    runPipeline(sys.argv[1])
    
    app.exec_()