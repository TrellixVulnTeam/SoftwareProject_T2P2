# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# mame_types.py - Some classes to keep track of information from MAME
#                 roms.  The cache makes use of this.
# -----------------------------------------------------------------------
# $Id: mame_types.py 8441 2006-10-21 11:15:52Z duncan $
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


import sys
import time, os, string
import config

# The file format version number. It must be updated when incompatible
# changes are made to the file format.
TYPES_VERSION = 2

# Set to 1 for debug output
DEBUG = config.DEBUG

TRUE = 1
FALSE = 0


class MameRom:

    def __init__(self):
        self.filename = ''
        self.title = ''
        self.name = ''
        self.description = ''
        self.year = ''
        self.manufacturer = ''
        self.cloneof = ''
        self.romof = ''


    def getFilename(self):
        return self.filename

    def setFilename(self, f):
        self.filename = f

    def getDirname(self):
        return self.dirname

    def setDirname(self, d):
        self.dirname = d

    def getTitle(self):
        return self.title

    def setTitle(self, t):
        self.title = t

    def getImageFile(self):
        return self.imageFile

    def setImageFile(self, i):
        self.imageFile = i

    def getPartial(self):
        return self.partial

    def setPartial(self, p):
        self.partial = p

    def getMatched(self):
        return self.matched

    def setMatched(self, m):
        self.matched = m

    def getTrashme(self):
        return self.trashme

    def setTrashme(self, t):
        self.trashme = t


class MameRomList:
    # We are using a dictionary that will be keyed on the
    # absolute filename of the actual rom.
    mameRoms = {}
 
    def __init__(self):
        self.TYPES_VERSION = TYPES_VERSION
        
    def addMameRom(self, rom):
        if not self.mameRoms.has_key(rom.getFilename()):
            self.mameRoms[rom.getFilename()] = rom
        else:
            print "We already know about %s." % rom.getFilename()

    def getMameRoms(self):
        return self.mameRoms

    def setMameRoms(self, mr):
        self.mameRoms = mr

    def Sort(self):
        self.mameRoms.Sort()
        

