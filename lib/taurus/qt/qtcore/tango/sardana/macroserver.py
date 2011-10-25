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

"""MacroServer extension for taurus Qt"""

__all__ = ["QDoor", "QMacroServer", "MacroServerMessageErrorHandler", "registerExtensions"]

import taurus.core
from taurus.core.tango.sardana.macroserver import BaseMacroServer, BaseDoor

from taurus.qt import Qt

CHANGE_EVTS = (taurus.core.TaurusEventType.Change, taurus.core.TaurusEventType.Periodic)

class QDoor(BaseDoor, Qt.QObject):
    
    __pyqtSignals__ = ["resultUpdated","recordDataUpdated", "macroStatusUpdated"]
    __pyqtSignals__ += [ "%sUpdated" % l.lower() for l in BaseDoor.log_streams ]
    
    def __init__(self, name, qt_parent=None, **kw):
        self.call__init__wo_kw(Qt.QObject, qt_parent)
        self.call__init__(BaseDoor, name, **kw)
    
    def resultReceived(self, log_name, result):
        res = BaseDoor.resultReceived(self, log_name, result)
        self.emit(Qt.SIGNAL("resultUpdated"))
        return res
    
    def recordDataReceived(self, s, t, v):
        if t not in CHANGE_EVTS: return
        res = BaseDoor.recordDataReceived(self, s, t, v)
        self.emit(Qt.SIGNAL("recordDataUpdated"), res)
        return res
        
    def macroStatusReceived(self, s, t, v):
        res = BaseDoor.macroStatusReceived(self, s, t, v)
        if t == taurus.core.TaurusEventType.Error:
            macro = None
        else:
            macro = self.getRunningMacro()
        if macro is None: return
        self.emit(Qt.SIGNAL("macroStatusUpdated"), (macro, res))
        return res
    
    def logReceived(self, log_name, output):
        res = BaseDoor.logReceived(self, log_name, output)
        self.emit(Qt.SIGNAL("%sUpdated" % log_name.lower()), output)
        return res
    
#    def getExperimentConfiguration(self, cache=False):
#        '''
#        Returns the ExperimentConfiguration dictionary. 
#        This implementation is a dummy one returning a hardcoded dictionary. 
#        The real implementation should be able to read the info from the
#        ExperimentConfiguration envvar stored in the environment attribute.
#        '''
##        from taurus.qt.qtgui.extra_sardana.measurementgroup import DUMMY_EXP_CONF
#        import copy, json
        
##        ms = self.macroserver
##        poolname = ms.get_property('poolnames')['poolnames'][0]
##        pool = taurus.Device(poolname) 
#        ActiveMntGrp = json.loads(str(self.Environment[1]))['ActiveMntGrp']
#        MNTGRPCONFIGS = {}
#        for element in self.macro_server.MeasurementGroupList:
#            mginfo = json.loads(element)
#            name = mginfo['name']
#            mg = taurus.Device(str(name))
#            conf = json.loads(mg.configuration)
#            MNTGRPCONFIGS[name] = conf
#        default = {'MntGrpConfigs': MNTGRPCONFIGS,
#               'ActiveMntGrp' : ActiveMntGrp,
#               'ScanDir':'/tmp/scandir',
#               'ScanFile':'dummyscan.h5',
#               'DataCompressionRank':-1}
#        return copy.deepcopy(getattr(self, "_dummy_exp_conf", default))
    
    
#    def setExperimentConfiguration(self, conf):
#        '''
#        Sets the ExperimentConfiguration dictionary. 
#        This implementation is a dummy one which saves it as the "_dummy_exp_conf" member 
#        The real implementation should be able to write it as the
#        ExperimentConfiguration envvar stored in the environment attribute.
#        '''
#        import copy
#        self._dummy_exp_conf = copy.deepcopy(conf)


class QMacroServer(BaseMacroServer, Qt.QObject):
    
    def __init__(self, name, qt_parent=None, **kw):
        self.call__init__wo_kw(Qt.QObject, qt_parent)
        self.call__init__(BaseMacroServer, name, **kw)
        
    def typesChanged(self, s, t, v):
        res = BaseMacroServer.typesChanged(self, s, t, v)
        self.emit(Qt.SIGNAL("typesUpdated"))
        return res
    
    def elementsChanged(self, s, t, v):
        res = BaseMacroServer.elementsChanged(self, s, t, v)
        self.emit(Qt.SIGNAL("elementsUpdated"))
        return res
    
    def macrosChanged(self, s, t, v):
        res = BaseMacroServer.macrosChanged(self, s, t, v)
        self.emit(Qt.SIGNAL("macrosUpdated"))
        return res
    
# ugly access to qtgui level: in future find a better way to register error
# handlers, maybe in TangoFactory & TaurusManager

from taurus.qt.qtgui.panel import TaurusMessageErrorHandler
class MacroServerMessageErrorHandler(TaurusMessageErrorHandler):

    def setError(self, err_type=None, err_value=None, err_traceback=None):
        """Translates the given error object into an HTML string and places it
        in the message panel
        
        :param error: an error object (typically an exception object)
        :type error: object"""
        
        msgbox = self._msgbox
        msgbox.setText(err_value)
        msg = "<html><body><pre>%s</pre></body></html>" % err_value
        msgbox.setDetailedHtml(msg)

        html_orig = """<html><head><style type="text/css">{style}</style></head><body>"""
        exc_info = "".join(err_traceback)
        style = ""
        try:
            import pygments
            import pygments.highlight
            import pygments.formatters
            import pygments.lexers

        except:
            pygments = None
        if pygments is not None:
            formatter = pygments.formatters.HtmlFormatter()
            style = formatter.get_style_defs()
        html = html_orig.format(style=style)
        if pygments is None:
            html += "<pre>%s</pre>" % exc_info
        else:
            formatter = pygments.formatters.HtmlFormatter()
            html += pygments.highlight(exc_info, pygments.lexers.PythonTracebackLexer(), formatter)
        html += "</body></html>"
        msgbox.setOriginHtml(html)


def registerExtensions():
    """Registers the macroserver extensions in the :class:`taurus.core.tango.TangoFactory`"""
    import taurus
    factory = taurus.Factory()
    factory.registerDeviceClass('MacroServer', QMacroServer)
    factory.registerDeviceClass('Door', QDoor)
    
    # ugly access to qtgui level: in future find a better way to register error
    # handlers, maybe in TangoFactory & TaurusManager
    import taurus.core.tango.sardana.macro
    import taurus.qt.qtgui.panel
    MacroRunException = taurus.core.tango.sardana.macro.MacroRunException
    TaurusMessagePanel = taurus.qt.qtgui.panel.TaurusMessagePanel
    
    TaurusMessagePanel.registerErrorHandler(MacroRunException, MacroServerMessageErrorHandler)
