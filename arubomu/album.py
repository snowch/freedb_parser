#
# $Source: /home/blais/repos/cvsroot/arubomu/lib/python/arubomu/album.py,v $
# $Id: album.py,v 1.15 2004/10/06 03:20:01 blais Exp $
#

"""Data structures and parser for arubomu 'album' format.

This modules provides some format independent data structures and conversion
from/to XML, and implements some assumptions in the data structures conversion.

"""

__version__ = "$Revision: 1.15 $"
__author__ = "Martin Blais <blais@furius.ca>"


import sys, os
import re

#from elementtree import ElementTree

# import strxtra

from arubomu.common import SimpleAttr



def load(f):
    """Reads an XML file and parses as an album file."""

    tree = ElementTree.parse(f)
    root = tree.getroot()
    album = None
    if root.tag == 'album':
        album = Album().fromxml(root)
    return album


def load_list(f):
    """Reads an XML file and parses as an rip or riplist file."""

    tree = ElementTree.parse(f)
    root = tree.getroot()
    l = None
    if root.tag == 'album-list':
        l = []
        for c in root.getchildren():
            if c.tag == 'album' or c.tag == 'album-loose':
                album = Album().fromxml(c)
                l.append(album)
    return l



nodre = re.compile('[0-9]+')

def reldate_to_year(reldate):
    return int(nodre.findall(reldate)[0])



class Album(SimpleAttr):

    """Class that represents an album."""

    attribs = ['res']
    elems_common = ['title', 'subtitle', 'artist',
                    'label',
                    'reldate',
                    'series', 'packaging']
    elems_strict = ['release-type']
    elems = elems_common + elems_strict
    elems_other = ['label_url', 'reldate_num']

    def __init__(self):
        SimpleAttr.__init__(self, self.elems + self.attribs)
        SimpleAttr.__init__(self, self.elems_other)

        # list of (name, catalog-id) string tuples.
        self.catalogs = []

        # list of strings.
        self.reviews = []

        # map of discno -> Disc instances.
        self.discs = {}

        # list of Musician instances.
        self.musicians = []

        # notes, any content.
        self.notes = None

    def __cmp__(x, y):
        "Sort according to artist, then release date, then title."

        c = cmp(x.artist, y.artist)
        if not c:
            c = cmp(x.reldate_num, y.reldate_num)
            if not c:
                c = cmp(x.title, y.title)
        return c

    def __repr__(self):
        r = SimpleAttr.__repr__(self, self.elems)
        r += SimpleAttr.__repr__(self, self.elems_other)

        for name, number in self.catalogs:
            r += 'catalog: %s = %s\n' % (name, number)

        for review in self.reviews:
            r += 'review:\n%s\n' % review

        for m in self.musicians:
            r += repr(m)

        for d in self.discs:
            r += repr(d)

        if self.notes:
            r += self.notes
            ##r += 'notes:\n' + ElementTree.tostring(self.notes)

        return r

    def set_reldate(self, reldate):
        self.reldate = reldate
        if reldate:
            alldates = nodre.findall(reldate)
            self.reldate_num = ', '.join(alldates)

    def get_discs(self):
        return self.discs.keys()

    def get_disc(self, discno):
        "Get the specified disc, works with None value."
        if discno == None:
            discno = 1
        return self.discs[discno]

    def render_oneline(self):
        "Return a single-line description of the album."

        desc = '%s, "%s"' % (self.artist, self.title)
        if self.label:
            desc += ', %s' % self.label
        if self.reldate:
            desc += ', %s' % self.reldate
        return desc
        
    def fromxml(self, xel):

        assert xel.tag in ['album', 'album-loose']

        SimpleAttr.fromxml(self, xel, self.attribs, self.elems)

        self.set_reldate(self.reldate)

        el = xel.find('label')
        if el != None:
            self.label_url = el.get('url')

        el = xel.find('catalogs')
        if el != None:
            for el in el.getchildren():
                self.catalogs.append( (el.get('name'), el.text) )

        for el in xel.findall('review'):
            self.reviews.append(el.text)

        musicians = xel.find('musicians')
        if musicians != None:
            for el in musicians.findall('musician'):
                self.musicians.append(Musician().fromxml(el))

        for el in xel.findall('disc'):
            disc = Disc().fromxml(el)
            self.discs[disc.no] = disc

        # Make sure that if there is a disc without a key, that it is an int and
        # not just "None".
        for k in self.discs.iterkeys():
            if k is None:
                d = self.discs[k]
                self.discs[1] = d
                del self.discs[k]
                break

        # Make sure that there is at least one disc if the XML file is not
        # compliant.
        if len(self.discs) == 0:
            self.discs[1] = Disc(1)

        SimpleAttr.fromxml(self, xel, [], ['notes'])
        ##self.notes = xel.find('notes') # no conversion

        return self

    def toxml(self, loose=False):
        if loose:
            xel = ElementTree.Element('album-loose')
        else:
            xel = ElementTree.Element('album')

        if loose:
            SimpleAttr.toxml(self, xel, self.attribs, self.elems_common)
        else:
            SimpleAttr.toxml(self, xel, self.attribs, self.elems)

        if self.label_url:
            el = xel.find('label')
            assert el != None
            el.set('url', self.label_url)

        if self.catalogs:
            cel = ElementTree.SubElement(xel, 'catalogs')
            for name, number in self.catalogs:
                el = ElementTree.SubElement(cel, 'catalog')
                el.set('name', name)
                el.text = number

        if self.discs and not loose:
            dkeys = self.discs.keys(); dkeys.sort()
            for dk in dkeys:
                disc = self.discs[dk]
                el = disc.toxml()
                xel.append(el)

        if not loose:
            if self.musicians:
                cel = ElementTree.SubElement(xel, 'musicians')
                for musician in self.musicians:
                    el = musician.toxml()
                    cel.append(el)

        for review in self.reviews:
            el = ElementTree.SubElement(xel, 'review')
            el.text = review

        if self.notes:
            SimpleAttr.toxml(self, xel, [], ['notes'])
            ##xel.append(self.notes) # no conversion

        return xel

    def encode(self, encoding):
        SimpleAttr.encode(self, encoding, self.elems + self.attribs)

        for disc in self.discs.itervalues():
            disc.encode(encoding)

        # FIXME we could convert the rest too, reviews, etc.



def guess_id(alb):

    """Tries to construct a valid id from an album's information."""

    from curses.ascii import isalnum

    s = '%s-%s' % (strxtra.idify(alb.artist.encode('iso-8859-1')),
                   strxtra.idify(alb.title.encode('iso-8859-1')))
    ss = ''
    for c in s:
        if isalnum(c) or c == '-':
            ss += c
        else:
            ss += '_'
    s = ss
    return ss


def full_title(alb):

    """Builds a single string that combines title and subtitle."""

    if alb.subtitle:
        return '%s -- %s' % (alb.title, alb.subtitle)
    return alb.title


class Musician(SimpleAttr):

    attribs = ['id']
    elems = ['name', 'instrument']

    def __init__(self):
        SimpleAttr.__init__(self, self.attribs + self.elems)

    def __repr__(self):
        return SimpleAttr.__repr__(self, self.attribs + self.elems)

    def fromxml(self, xel):
        assert xel.tag == 'musician'
        SimpleAttr.fromxml(self, xel, self.attribs, self.elems)
        return self

    def toxml(self):
        xel = ElementTree.Element('musician')
        SimpleAttr.toxml(self, xel, self.attribs, self.elems)
        return xel



class Disc(SimpleAttr):

    attribs = ['no']
    elems = ['disctitle']

    def __init__(self, no=None):
        SimpleAttr.__init__(self, self.attribs + self.elems)
        self.no = no

        # map of no -> Song instance.
        self.songs = {}

    def __repr__(self):
        r = SimpleAttr.__repr__(self, self.attribs + self.elems)
        skeys = self.songs.keys(); skeys.sort()
        for sk in skeys:
            song = self.songs[sk]
            r += repr(song)
        return r

    def fromxml(self, xel):
        assert xel.tag == 'disc'
        SimpleAttr.fromxml(self, xel, self.attribs, self.elems)
        if self.no: self.no = int(self.no)

        self.songs.clear()
        for el in xel.findall('song'):
            song = Song().fromxml(el)
            self.songs[song.no] = song

        return self

    def toxml(self):
        xel = ElementTree.Element('disc')
        SimpleAttr.toxml(self, xel, self.attribs, self.elems)

        skeys = self.songs.keys(); skeys.sort(key=lambda x: int(x))
        for sk in skeys:
            el = self.songs[sk].toxml()
            xel.append(el)

        return xel

    def encode(self, encoding):
        SimpleAttr.encode(self, encoding, self.attribs + self.elems)
        
        for song in self.songs.itervalues():
            song.encode(encoding)



class Song(SimpleAttr):

    attribs = ['no']
    elems = ['title', 'title-alt', 'artist', 'album', 'composer',
             'duration', 'extra', 'lyrics']
    elems_other = ['lyrics_src']

    def __init__(self, no=None):
        SimpleAttr.__init__(self, self.attribs + self.elems)
        SimpleAttr.__init__(self, self.elems_other)
        self.no = no

    def __cmp__(self, other):
        return cmp(self.no, other.no)

    def __repr__(self):
        r = SimpleAttr.__repr__(self, self.attribs + self.elems)
        r += SimpleAttr.__repr__(self, self.elems_other)
        return r

    def fromxml(self, xel):
        assert xel.tag == 'song'
        SimpleAttr.fromxml(self, xel, self.attribs, self.elems)
        if self.no: self.no = int(self.no)

        el = xel.find('lyrics')
        if el != None:
            self.lyrics_src = el.get('src')

        return self

    def toxml(self, doc=None):
        xel = ElementTree.Element('song')
        SimpleAttr.toxml(self, xel, self.attribs, self.elems)

        if self.lyrics_src != None:
            el = xel.find('lyrics')
            if el != None:
                el.set('src', self.lyrics_src)

        return xel

    def encode(self, encoding):
        SimpleAttr.encode(self, encoding, self.attribs + self.elems)
