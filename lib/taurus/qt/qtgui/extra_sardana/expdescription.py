#!/usr/bin/env python

#############################################################################
##
## This file is part of Taurus, a Tango User Interface Library
## 
## http://www.tango-controls.org/static/taurus/latest/doc/html/index.html
##
## Copyright 2011 CELLS / ALBA Synchrotron, Bellaterra, Spain
## 
## Taurus is free software: you can redistribute it and/or modify
## it under the terms of the GNU Lesser General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
## 
## Taurus is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU Lesser General Public License for more details.
## 
## You should have received a copy of the GNU Lesser General Public License
## along with Taurus.  If not, see <http://www.gnu.org/licenses/>.
##
#############################################################################

"""This module provides widget for configuring the data acquisition and display of an experiment"""

__all__ = ["ExpDescriptionEditor"]

from taurus.qt import Qt
import copy
import taurus
from taurus.qt.qtgui.base import TaurusBaseWidget

class ExpDescriptionEditor(Qt.QWidget, TaurusBaseWidget):
    '''
    A widget for editing the configuration of a experiment (measurement groups,
    plot and storage parameters, etc).
    
    It receives a Sardana Door name as its model and gets/sets the configuration
    using the `ExperimentConfiguration` environmental variable for that Door.
    '''
    def __init__(self, parent=None, door=None):
        Qt.QWidget.__init__(self, parent)
        TaurusBaseWidget.__init__(self, 'ExpDescriptionEditor')
        from ui.ui_ExpDescriptionEditor import Ui_ExpDescriptionEditor
        self.ui = Ui_ExpDescriptionEditor()
        self.ui.setupUi(self)
        BB = Qt.QDialogButtonBox
        self.ui.buttonBox.setStandardButtons(BB.Ok | BB.Cancel | BB.Reset | BB.Apply)
        
        self._localConfig = None
        self._originalConfiguration = None
        self.connect(self.ui.activeMntGrpCB, Qt.SIGNAL('currentIndexChanged (QString)'), self.onActiveMntGrpChanged)
        self.connect(self.ui.compressionCB, Qt.SIGNAL('currentIndexChanged (int)'), self.onCompressionCBChanged )
        
        if door is not None:
            self.setModel(door)
        self.connect(self.ui.buttonBox, Qt.SIGNAL("clicked(QAbstractButton *)"), self.onDialogButtonClicked)
             
    def getModelClass(self):
        '''reimplemented from :class:`TaurusBaseWidget`'''
        return taurus.core.TaurusDevice
        
    def onDialogButtonClicked(self, button):
        role = self.ui.buttonBox.buttonRole(button)
        #qmodel = self.ui.channelEditor.getQModel()
        if role in (Qt.QDialogButtonBox.AcceptRole,Qt.QDialogButtonBox.ApplyRole) :
            conf = copy.deepcopy(self.getLocalConfig())
            print self.isDataChanged(), conf
            self._originalConfiguration = conf
            door = self.getModelObj()
            if door is None: 
                return
            door.setExperimentConfiguration(conf)
        elif role == Qt.QDialogButtonBox.ResetRole:
            self._reloadConf()
        if role in (Qt.QDialogButtonBox.AcceptRole,Qt.QDialogButtonBox.RejectRole):
            self.close()
    
    def closeEvent(self,event):
        '''This event handler receives widget close events'''
#        if self.isDataChanged():
#            op = Qt.QMessageBox.question(self, "Discard pending changes?", 
#                                    "There are unsaved changes in the configuration. If you close they will be lost.\n Close anyway?", 
#                                    Qt.QMessageBox.Yes|Qt.QMessageBox.Cancel)
#            if op != Qt.QMessageBox.Yes: 
#                return
        Qt.QWidget.closeEvent(self,event)
    
    def setModel(self, model):
        '''reimplemented from :class:`TaurusBaseWidget`'''
        TaurusBaseWidget.setModel(self, model)
        self._reloadConf(force=True)
        
    def _reloadConf(self, force=False):
        if not force and self.isDataChanged():
            op = Qt.QMessageBox.question(self, "Reload info from door", 
                                    "If you reload, all current experiment configuration changes will be lost. Reload?", 
                                    Qt.QMessageBox.Yes|Qt.QMessageBox.Cancel)
            if op != Qt.QMessageBox.Yes: 
                return
        door = self.getModelObj()
        if door is None: return
        conf = door.getExperimentConfiguration()
        print conf
        self._originalConfiguration = copy.deepcopy(conf)
        self.setLocalConfig(conf)
        
        #set a list of available channels
        from taurus.core.tango.sardana.pool import ExpChannel
        avail = {}
       
        import json #@todo @fixme!!!!
        for channeldesc in door.macro_server.ExpChannelList: 
            channeldesc = json.loads(channeldesc) #@todo: this decoding should be done at the QMacroServer level
            avail[channeldesc['name']] = channeldesc
        
        self.ui.channelEditor.getQModel().setAvailableChannels(avail)
        
    def isDataChanged(self):
        """Tells if the local data has been modified since it was last refreshed
        """
        return self._originalConfiguration != self.getLocalConfig()

    def getLocalConfig(self):
        return self._localConfig

    def setLocalConfig(self, conf):
        '''gets a ExpDescription dictionary and sets up the widget'''
        self._localConfig = conf
        
        #measurement group settings
        mgcfgs = conf['MntGrpConfigs']
        self.ui.activeMntGrpCB.clear()
        self.ui.activeMntGrpCB.addItems(sorted(mgcfgs.keys()))
        idx = self.ui.activeMntGrpCB.findText(self._localConfig['ActiveMntGrp'])
        self.ui.activeMntGrpCB.setCurrentIndex(idx) #note that this triggers a call to onActiveMntGrpChanged 
        
        #other settings
        self.ui.filenameLE.setText(", ".join(self._localConfig['ScanFile']))
        self.ui.pathLE.setText(self._localConfig['ScanDir'])
        self.ui.compressionCB.setCurrentIndex(self._localConfig['DataCompressionRank']+1)
        
    def onActiveMntGrpChanged(self, activeMntGrpName):
        activeMntGrpName = str(activeMntGrpName)
        if self._localConfig is None: return
        if activeMntGrpName not in self._localConfig['MntGrpConfigs']: return
        self._localConfig['ActiveMntGrp'] = activeMntGrpName
        mgconfig = self._localConfig['MntGrpConfigs'][activeMntGrpName]
        self.ui.channelEditor.getQModel().setDataSource(mgconfig)
        
    def onCompressionCBChanged(self, idx):
        if self._localConfig is None: return
        self._localConfig['DataCompressionRank'] = idx - 1
 
    
        
            


  
            
def demo(model="mydoor"):
    """Table panels"""
    #w = main_ChannelEditor()
    w = ExpDescriptionEditor(door=model)
    return w


def main():
    import sys
    import taurus.qt.qtgui.application
    Application = taurus.qt.qtgui.application.TaurusApplication
    
    app = Application.instance()
    owns_app = app is None
    
    if owns_app:
        app = Application(app_name="Exp. Description demo", app_version="1.0",
                          org_domain="Sardana", org_name="Tango community")
    
    args = app.get_command_line_args()
    if len(args)==1:
        w = demo(model=args[0])
    else:
        w = demo()
    w.show()
    
    if owns_app:
        sys.exit(app.exec_())
    else:
        return w
    
if __name__ == "__main__":
    main()
