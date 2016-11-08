#
# $Source: /home/blais/repos/cvsroot/arubomu/lib/python/arubomu/parsers/__init__.py,v $
# $Id: __init__.py,v 1.6 2005/03/02 05:13:25 blais Exp $
#

"""Main module for all fetchers.

This module contains the base interface for fetchers (converters, parsers,
whatever you prefer to call it).
"""

__version__ = "$Revision: 1.6 $"
__author__ = "Martin Blais <blais@furius.ca>"


import urllib

import freedb



def get_catalog_names():
    return [ 'freedb' ]


def getfetcher(name):
    try:
        return globals()[name].create_fetcher()
    except KeyError:
        raise RuntimeError("Error: cannot get fetcher '%s'" % name)
