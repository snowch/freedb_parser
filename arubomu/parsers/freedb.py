#
# $Source: /home/blais/repos/cvsroot/arubomu/lib/python/arubomu/parsers/freedb.py,v $
# $Id: freedb.py,v 1.7 2004/02/13 05:16:45 blais Exp $
#

"""Parser for CDDB files from the FreeDB database."""

__version__ = "$Revision: 1.7 $"
__author__ = "Martin Blais <blais@furius.ca>"

# The format is described at the end of this file.


import sys, os
import string, re
import StringIO

from arubomu.parsers.base import Fetcher
from arubomu.album import Album, Song, Disc
from pprint import pprint, pformat


# regular expressions
com_re = re.compile('^#')
lineno_re = re.compile('^(.*)(\d+)=(.*)$')
line_re = re.compile('^(.*)=(.*)$')
spl_re = re.compile('^(.*) / (.*)$')

# discid_re = re.compile('^DISCID=(.*)$') # " / " splits artist / title
# dtitle_re = re.compile('^DTITLE=(.*)$') # " / " splits artist / title
# dyear_re = re.compile('^DYEAR=(.*)$')
# dgenre_re = re.compile('^DGENRE=(.*)$')
# did3_re = re.compile('^DID3=(.*)$')
# titlet_re = re.compile('^TITLET(\d)=(.*)$')
#                        # " / " splits when more than one artist
# extd_re = re.compile('^EXTD=(.*)$') # concatenate
# extt_re = re.compile('^EXTT(\d)=(.*)$') # concatenate
# playorder_re = re.compile('^PLAYORDER=(.*)$')


__all__ = ['FreedbFetcher']


def create_fetcher():
    return FreedbFetcher()


class FreedbFetcher(Fetcher):

    # Note: you *must* include both the genre and the discid.
    urlt = 'http://www.freedb.org/freedb/%s'

    def geturl(self, catalog_number):
        # remove spaces.
        return self.urlt % ''.join(catalog_number.split())
        
    def parse(self, text):
        alb = parseText(text)
        return (alb, [])



def parseText(text):

    a = Album()
    songs = {}
    for line in text.splitlines():
        if com_re.match(line):
            continue

        mo = lineno_re.match(line)
        if mo:
            (tag, no, content) = mo.groups()
            no = int(no)
            if no not in songs:
                # songs[no] = Song(no+1, '')
                songs[no] = Song(no+1)
            song = songs[no]

            if content:
                if tag == 'TTITLE':
                    mo = spl_re.match(content)
                    if mo:
                        song.artist = mo.group(2)
                        song.title = mo.group(1)
                    else:
                        song.title = content
                elif tag == 'EXTT':
                    song.extra = content
        else:
            mo = line_re.match(line)
            if mo:
                (tag, content) = mo.groups()
                
                if content:
                    if tag == 'DISCID':
                        a.catalogs.append( ('freedb', '%s' % content) )
                    elif tag == 'DTITLE':
                        mo = spl_re.match(content)
                        if mo:
                            a.artist, a.title = mo.groups()
                        else:
                            a.title = content
                    elif tag == 'EXTD':
                        pass
                        ## a.attribs['misc'] =
                        ##  a.attribs.get('misc', '') + content
                    elif tag == 'DYEAR':
                        a.reldate = content
                    elif tag == 'DGENRE':
                        a.category = content
                    elif tag == 'DID3':
                        pass
                    elif tag == 'PLAYORDER':
                        pass
            else:
                print >> sys.stderr, "Error: parsing CDDB file."
                return None

    disc = Disc()
    disc.no = 1
    a.discs[disc.no] = disc
    disc.songs = songs

    return a
    

def selftest():
    print parseFile(sys.argv[1])
    return 1

# Run main if loaded as a script
if __name__ == "__main__":
    selftest()



# DISCID: The data following this keyword should be a comma-separated list of
# 	8-byte disc IDs. The disc ID indicated by the track offsets in the
# 	comment section must appear somewhere in the list. Other disc IDs
# 	represent links to this database entry. Note that linking entries is
# 	now deprecated and should not be used by submitting programs!
# 	The algorithm for generating the disc ID is described in the freedb.howto.
#
# DTITLE: Technically, this may consist of any data, but by convention contains
# 	the artist and disc title (in that order) separated by a "/" with a
# 	single space on either side to separate it from the text. There may be
# 	other "/" characters in the DTITLE, but not with space on both sides,
# 	as that character sequence is exclusively reserved as delimiter of
# 	artist and disc title! If the "/" is absent, it is implied that the
# 	artist and disc title are the same, although in this case the name
# 	should rather be specified twice, separated by the delimiter.
# 	If the disc is a sampler containing titles of various artists, the disc
# 	artist should be set to "Various" (without the quotes).
#
# DYEAR:  This field contains the (4-digit) year, in which the CD was released.
# 	It should  be empty (not 0) if the user hasn't entered a year.
#
# DGENRE: This field contains the exact genre of the disc in a textual form
# 	(i.e. write the genre here and do not use e.g. simply the MP3 ID3V1
# 	genre code). Please note that this genre is not limited to the
# 	11 CDDB-genres. The Genre in this field should be capitalized, e.g.
# 	"New Age" instead of "newage" or "new age".
#
# TTITLEN:There must be one of these for each track in the CD. The track
# 	number should be substituted for the "N", starting with 0. This field
# 	should contain the title of the Nth track on the CD. If the disc is a
# 	sampler and there are different artists for the track titles, the
# 	track artist and the track title (in that order) should be separated
# 	by a "/" with a single space on either side to separate it from the text.
#
# EXTD:	This field contains the "extended data" for the CD. This is intended
# 	to be used as a place for interesting information related to the CD,
# 	such as credits, et cetera. If there is more than one of these lines
# 	in the file, the data is concatenated. This allows for extended data
# 	of arbitrary length.
#
# EXTTN:	This field contains the "extended track data" for track "N". There
# 	must be one of these for each track in the CD. The track number
# 	should be substituted for the "N", starting with 0. This field is
# 	intended to be used as a place for interesting information related to
# 	the Nth track, such as the author and other credits, or lyrics. If
# 	there is more than one of these lines in the file, the data is
# 	concatenated. This allows for extended data of arbitrary length.
#
# PLAYORDER:
# 	This field contains a comma-separated list of track numbers which
# 	represent a programmed track play order. This field is generally
# 	stripped of data in non-local database entries. Applications that
# 	submit entries for addition to the main database should strip this
# 	keyword of data.
