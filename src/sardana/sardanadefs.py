#!/usr/bin/env python

##############################################################################
##
## This file is part of Sardana
##
## http://www.tango-controls.org/static/sardana/latest/doc/html/index.html
##
## Copyright 2011 CELLS / ALBA Synchrotron, Bellaterra, Spain
## 
## Sardana is free software: you can redistribute it and/or modify
## it under the terms of the GNU Lesser General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
## 
## Sardana is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU Lesser General Public License for more details.
## 
## You should have received a copy of the GNU Lesser General Public License
## along with Sardana.  If not, see <http://www.gnu.org/licenses/>.
##
##############################################################################

"""This module contains the most generic sardana constants and enumerations"""

__all__ = ["EpsilonError", "SardanaServer", "State",
           "DataType", "DataFormat", "DataAccess", "DTYPE_MAP", "DACCESS_MAP",
           "from_dtype_str", "from_access_str", "to_dtype_dformat",
           "to_daccess", "InvalidId", "InvalidAxis", "ElementType",
           "TYPE_ELEMENTS", "TYPE_GROUP_ELEMENTS", "TYPE_MOVEABLE_ELEMENTS",
           "TYPE_PHYSICAL_ELEMENTS", "TYPE_ACQUIRABLE_ELEMENTS",
           "TYPE_PSEUDO_ELEMENTS", "INTERFACES", "INTERFACES_EXPANDED",
           "is_number", "ScalarNumberFilter"]

__docformat__ = 'restructuredtext'

import functools
import numbers

from taurus.core.util import Enumeration

#: maximum difference between two floats so that they are considered equal
EpsilonError = 1E-16

#: sardana element state enumeration
State = Enumeration("State", ( \
    "On",
    "Off",
    "Close",
    "Open",
    "Insert",
    "Extract",
    "Moving",
    "Standby",
    "Fault",
    "Init",
    "Running",
    "Alarm",
    "Disable",
    "Unknown",
    "Invalid") )

class _SardanaServer(object):
    """Class representing the current sardana server state"""
    
    def __init__(self):
        self.server_state = State.Invalid
    
    def __repr__(self):
        return "SardanaServer()"
    
    
#: the global object containing the SardanaServer information
SardanaServer = _SardanaServer()

#: sardana data types (used by device pool controllers)
DataType = Enumeration("DataType", ( \
    "Integer",
    "Double",
    "String",
    "Boolean",
    "Encoded",
    "Invalid") )

#: sardana data format enumeration (used by device pool controllers)
DataFormat = Enumeration("DataFormat", ( \
    "Scalar",
    "OneD",
    "TwoD",
    "Invalid") )

#: sardana data access (used by device pool controllers)
DataAccess = Enumeration("DataAccess", ( \
    "ReadOnly",
    "ReadWrite",
    "Invalid") )

#: dictionary dict<data type, :class:`sardana.DataType`>
DTYPE_MAP = { 
    'int'            : DataType.Integer,
    'integer'        : DataType.Integer,
    int              : DataType.Integer,
    long             : DataType.Integer,
    'long'           : DataType.Integer,
    DataType.Integer : DataType.Integer,
    'float'          : DataType.Double,
    'double'         : DataType.Double,
    float            : DataType.Double,
    DataType.Double  : DataType.Double,
    'str'            : DataType.String,
    'string'         : DataType.String,
    str              : DataType.String,
    DataType.String  : DataType.String,
    'bool'           : DataType.Boolean,
    'boolean'        : DataType.Boolean,
    bool             : DataType.Boolean,
    DataType.Boolean : DataType.Boolean,
}
#DTYPE_MAP.setdefault(DataType.Invalid)

#: dictionary dict<access type, :class:`sardana.DataAccess`>
DACCESS_MAP = { 
    'read'               : DataAccess.ReadOnly,
    DataAccess.ReadOnly  : DataAccess.ReadOnly,
    'readwrite'          : DataAccess.ReadWrite,
    'read_write'         : DataAccess.ReadWrite,
    DataAccess.ReadWrite : DataAccess.ReadWrite,
}
#DACCESS_MAP.setdefault(DataAccess.Invalid)

def from_dtype_str(dtype):
    """Transforms the given dtype parameter (string/:obj:`DataType` or None)
    into a tuple of two elements (str, :obj:`DataFormat`) where the first
    element is a string with a simplified data type.
    
        - If None is given, it returns
          ('float', :obj:`DataFormat.Scalar`)
        - If :obj:`DataType` is given, it returns
          (:obj:`DataType`, :obj:`DataFormat.Scalar`)
          
    :param dtype: the data type to be transformed
    :type dtype: str or None or :obj:`DataType`
    :return: a tuple <str, :obj:`DataFormat`> for the given dtype
    :rtype: tuple<str, :obj:`DataFormat`>"""
    dformat = DataFormat.Scalar
    if dtype is None:
        dtype = 'float'
    elif isinstance(dtype, (str, unicode)):
        dtype = dtype.lower()
        if dtype.startswith("pytango."):
            dtype = dtype[len("pytango."):]
        if dtype.startswith("dev"):
            dtype = dtype[len("dev"):]
        if dtype.startswith("var"):
            dtype = dtype[len("var"):]
        if dtype.endswith("array"):
            dtype = dtype[:dtype.index("array")]
            dformat = DataFormat.OneD
    return dtype, dformat

def from_access_str(access):
    """Transforms the given access parameter (string or :obj:`DataAccess`) into
    a simplified data access string.
    
    :param dtype: the access to be transformed
    :type dtype: str
    :return: a simple string for the given access
    :rtype: str"""
    if type(access) == str:
        access = access.lower()
        if access.startswith("pytango."):
            access = access[len("pytango."):]
    return access

def to_dtype_dformat(data):
    """Transforms the given data parameter (string/ or sequence of string or
    sequence of sequence of string/:obj:`DataType`) into a tuple of two
    elements (:obj:`DataType`, :obj:`DataFormat`).
    
    :param data: the data information to be transformed
    :type data: str or seq<str> or seq<seq<str>>
    :return: a tuple <:obj:`DataType`, :obj:`DataFormat`> for the given data
    :rtype: tuple<:obj:`DataType`, :obj:`DataFormat`>
    """
    import operator
    dtype, dformat = data, DataFormat.Scalar
    if isinstance(data, (str, unicode)):
        dtype, dformat = from_dtype_str(data)
    elif operator.isSequenceType(data):
        dformat = DataFormat.OneD
        dtype = data[0]
        if type(dtype) == str:
            dtype, dformat2 = from_dtype_str(dtype)
            if dformat2 == DataFormat.OneD:
                dformat = DataFormat.TwoD
        elif operator.isSequenceType(dtype):
            dformat = DataFormat.TwoD
            dtype = dtype[0]
            if type(dtype) == str:
                dtype, _ = from_dtype_str(dtype)
    dtype = DTYPE_MAP.get(dtype, DataType.Invalid)
    return dtype, dformat

def to_daccess(data):
    """Transforms the given access parameter (string or None) into a
    :obj:`DataAccess`. If None is given returns :obj:`DataAccess.ReadWrite`
    
    :param dtype: the access to be transformed
    :type dtype: str
    :return: a :obj:`DataAccess` for the given access
    :rtype: :obj:`DataAccess`"""
    daccess = DataAccess.Invalid
    if isinstance(data , (str, unicode)):
        daccess = DACCESS_MAP.get(from_access_str(data), DataAccess.ReadWrite)
    return daccess

#: A constant representing  an invalid ID
InvalidId = 0

#: A constant representing an invalid axis
InvalidAxis = 0

#: An enumeration describing the all possible element types in sardana
ElementType = Enumeration("ElementType", ( \
    "Pool",
    "Controller",
    "Motor",
    "CTExpChannel",
    "ZeroDExpChannel",
    "OneDExpChannel",
    "TwoDExpChannel",
    "ComChannel",
    "IORegister",
    "PseudoMotor",
    "PseudoCounter",
    "Constraint",
    "MotorGroup",
    "MeasurementGroup",
    "Instrument",
    "ControllerClass",
    "ControllerLibrary",
    "MacroClass",
    "MacroLibrary",
    "External",
    "Unknown") )

ET = ElementType

#: a set containning all "controllable" element types.
#: Constant values belong to :class:`~sardana.sardanadefs.ElementType`
TYPE_ELEMENTS = set((ET.Motor, ET.CTExpChannel, ET.ZeroDExpChannel, \
    ET.OneDExpChannel, ET.TwoDExpChannel, \
    ET.ComChannel, ET.IORegister, ET.PseudoMotor, \
    ET.PseudoCounter, ET.Constraint))

#: a set containing all group element types.
#: Constant values belong to :class:`~sardana.sardanadefs.ElementType`
TYPE_GROUP_ELEMENTS = set((ET.MotorGroup, ET.MeasurementGroup))

#: a set containing the type of elements which are moveable.
#: Constant values belong to :class:`~sardana.sardanadefs.ElementType`
TYPE_MOVEABLE_ELEMENTS = set((ET.Motor, ET.PseudoMotor, ET.MotorGroup))

#: a set containing the possible types of physical elements.
#: Constant values belong to :class:`~sardana.sardanadefs.ElementType`
TYPE_PHYSICAL_ELEMENTS = set((ET.Motor, ET.CTExpChannel, ET.ZeroDExpChannel, \
    ET.OneDExpChannel, ET.TwoDExpChannel, \
    ET.ComChannel, ET.IORegister))

#: a set containing the possible types of acquirable elements.
#: Constant values belong to :class:`~sardana.sardanadefs.ElementType`
TYPE_ACQUIRABLE_ELEMENTS = set((ET.Motor, ET.CTExpChannel, ET.ZeroDExpChannel, \
    ET.OneDExpChannel, ET.TwoDExpChannel, \
    ET.ComChannel, ET.IORegister, ET.PseudoMotor, \
    ET.PseudoCounter))

#: a set containing the possible types of pseudo elements.
#: Constant values belong to :class:`~sardana.sardanadefs.ElementType`
TYPE_PSEUDO_ELEMENTS = set((ET.PseudoMotor, ET.PseudoCounter))

#: a dictionary containing the direct interfaces supported by each type
INTERFACES = {
    "Object" : set(),
    "SardanaObject" : "Object",
    "Element" : "Object",
    "SardanaElement" : "Element",
    "Class" : "SardanaObject",
    "Library" : "SardanaObject",
    "PoolObject" : "SardanaObject",
    "PoolElement" : set(("SardanaElement", "PoolObject")),
    "Pool" : "PoolElement",
    "Controller" : "PoolElement",
    "Moveable" : "PoolElement",
    "Acquirable" : "PoolElement",
    "Instrument" : "PoolElement",
    "Motor" : set(("Moveable", "Acquirable")),
    "PseudoMotor" : set(("Moveable", "Acquirable")),
    "IORegister" : set(("Moveable", "Acquirable")),
    "ExpChannel" : "Acquirable",
    "CTExpChannel" : "ExpChannel",
    "ZeroDExpChannel" : "ExpChannel",
    "OneDExpChannel" : "ExpChannel",
    "TwoDExpChannel" : "ExpChannel",
    "PseudoCounter" : "ExpChannel",
    "ComChannel" : "PoolElement",
    "MotorGroup" : set(("Moveable", "Acquirable")),
    "MeasurementGroup" : "PoolElement",
    "ControllerLibrary" : set(("Library", "PoolObject")),
    "ControllerClass" : set(("Class", "PoolObject")),
    "Constraint" : "PoolObject",
    "External" : "Object",
    
    "MacroServerObject" : "SardanaObject",
    "MacroServerElement" : set(("SardanaElement", "MacroServerObject")),
    "MacroServer" : "MacroServerElement",
    "MacroLibrary" : set(("Library", "MacroServerObject")),
    "MacroClass" : set(("Class", "MacroServerObject")),
    "Macro" : "MacroClass",
}

#: a dictionary containing the *all* interfaces supported by each type
INTERFACES_EXPANDED = {}

def __expand(name):
    direct_expansion = INTERFACES[name]
    if isinstance(direct_expansion, (str, unicode)):
        direct_expansion = direct_expansion,
    exp = set(direct_expansion)
    for e in direct_expansion:
        if e in INTERFACES_EXPANDED:
            exp.update(INTERFACES_EXPANDED[e])
        else:
            exp.update(__expand(e))
    exp.add(name)
    return exp

for i in INTERFACES:
    INTERFACES_EXPANDED[i] = __expand(i)

try:
    import numpy
except ImportError:
    numpy = None

risinstance = lambda kls_typ_or_tpl, obj : isinstance(obj, kls_typ_or_tpl)

_is_pure_number = functools.partial(risinstance, numbers.Number)

def is_number(value):
    """utility function to determine if an object is a number"""
    if _is_pure_number(value):
        return True
    if numpy:
        return numpy.isreal(value) and numpy.isscalar(value)
    return False


class ScalarNumberFilter(object):
    """A simple scalar number filter that returns ``False`` if two numbers are
    indentical (i.e. |a-b| < error)"""
    
    def __call__(self, a, b):
        try:
            return fabs(a-b) > EpsilonError
        except:
            return a != b