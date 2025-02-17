# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# imageitem.py - Item for image files
# -----------------------------------------------------------------------
# $Id: imageitem.py 8440 2006-10-21 10:07:55Z duncan $
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002 Krister Lagerstrom, et al. 
# Please see the file freevo/Docs/CREDITS for a complete list of authors.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MER-
# CHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
# Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
#
# -----------------------------------------------------------------------


import util
import os
import time
import kaa.metadata as mmpython

import config
import viewer

from item import Item
from event import *


class ImageItem(Item):
    def __init__(self, url, parent, name = None, duration = config.IMAGEVIEWER_DURATION):
        #print "__init__(self, url, parent, name=%s, duration=%s)" % (name, duration)
        self.type = 'image'
        self.autovars = [ ( 'rotation', 0 ) ]
        Item.__init__(self, parent)

        if name:
            self.name = name

        self.set_url(url, search_image=False)

        if self.mode == 'file':
            self.image = self.filename
        self.duration = duration

        
    def __getitem__(self, key):
        #print "__getitem__(self=%s, key=%s)" % (self.filename, key)
        """
        return the specific attribute as string or an empty string
        """
        if key == "geometry":
            if self['width'] and self['height']:
                return '%sx%s' % (self['width'], self['height'])
            return ''
        
        if key == "date":
            try:
                t = str(Item.__getitem__(self, key))
                if t:
                    return time.strftime(config.TV_DATETIMEFORMAT,
                                         time.strptime(t, '%Y:%m:%d %H:%M:%S'))
            except:
                pass
            
        return Item.__getitem__(self, key)
        

    def sort(self, mode=None):
        #print "sort(self, mode=%s)" % (mode)
        """
        Returns the string how to sort this item
        """
        if mode == 'date':
            return u'%s%s' % (os.stat(self.filename).st_ctime, Unicode(self.filename))
        return Unicode(self.filename)


    def actions(self):
        #print "actions(self)"
        """
        return a list of possible actions on this item.
        """
        return [ ( self.view, _('View Image') ) ]


    def cache(self):
        #print "cache(self)"
        """
        caches (loads) the next image
        """
        viewer.get_singleton().cache(self)


    def view(self, arg=None, menuw=None):
        #print "view(self, arg=%s, menuw=%s)" % (arg, menuw)
        """
        view the image
        """
        if not self.menuw:
            self.menuw = menuw
        self.parent.current_item = self

        if self.menuw.visible:
            self.menuw.hide()

        viewer.get_singleton().view(self, rotation=self['rotation'])

        if self.parent and hasattr(self.parent, 'cache_next'):
            self.parent.cache_next()
