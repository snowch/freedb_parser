#
# $Source: /home/blais/repos/cvsroot/arubomu/lib/python/arubomu/common.py,v $
# $Id: common.py,v 1.6 2004/04/25 21:21:03 blais Exp $
#

"""Common code for data structure and parsing in arubomu.

"""

__version__ = "$Revision: 1.6 $"
__author__ = "Martin Blais <blais@furius.ca>"


import sys, os
import re
import StringIO
from types import UnicodeType

from elementtree import ElementTree
import elementtree_helpers


xml_encoding = 'ISO-8859-1'


class SimpleAttr:

    """Simple base class that provides for initialization of some direct
    children elements and attributes."""

    def __init__(self, names):
        for a in names:
            setattr(self, a.replace('-', '_'), None)

    def __repr__(self, names):
        r = ''
        for a in names:
            r +=  '%s: %s\n' % (a, getattr(self, a.replace('-', '_')))
        return r

    def fromxml(self, xel, attribnames, elemnames):
        for a in attribnames:
            setattr(self, a.replace('-', '_'), xel.get(a))
        for a in elemnames:
            subel = xel.find(a)
            if subel != None:
                setattr(self, a.replace('-', '_'), subel.text)

    def toxml(self, el, attribnames, elemnames):
        for a in attribnames:
            av = getattr(self, a.replace('-', '_'))
            if av != None:
                if not type(av) is type(''):
                    av = str(av)
                el.set(a, unicode(av))
        for a in elemnames:
            av = getattr(self, a.replace('-', '_'))
            if av != None:
                e = ElementTree.SubElement(el, a)
                if type(av) is type(''):
                    av = av.decode('iso-8859-1')
                e.text = unicode(av)

    def encode(self, encoding, elemnames):
        for e in elemnames:
            en = e.replace('-', '_')
            av = getattr(self, en)
            if av != None and isinstance(av, UnicodeType):
                setattr(self, en, av.encode(encoding))
