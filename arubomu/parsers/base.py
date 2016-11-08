#
# $Source: /home/blais/repos/cvsroot/arubomu/lib/python/arubomu/parsers/base.py,v $
# $Id: base.py,v 1.1 2004/02/12 23:47:53 blais Exp $
#

"""Base class for fetchers.
"""

__version__ = "$Revision: 1.1 $"
__author__ = "Martin Blais <blais@furius.ca>"


import urllib



class Fetcher:

    def geturl(self, catalog_number):
        raise SystemExit("Error: not implemented.")

    def fetch(self, url):
        try:
            import urllib
            htfile = urllib.urlopen(url)
            text = htfile.read()
            htfile.close()
        except StandardError, e:
            raise RuntimeError("Error: fetching URL (%s)." % e)

        return self.parse(text)

    def parse(self, text):
        """Return an instance of album and a list of cover images."""
        raise SystemExit("Error: not implemented.")


class ParseError(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)
    pass
