# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# game.py - Freevo module to run games. 
# -----------------------------------------------------------------------
# $Id: game.py 8695 2006-12-04 16:19:13Z duncan $
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
import random
import time, os, glob
import string, popen2, fcntl, select, struct
import threading, signal

import config     # Configuration handler. reads config file.
import util       # Various utilities
import childapp   # Handle child applications
import menu       # The menu widget class
import osd        # The OSD class, used to communicate with the OSD daemon
import rc         # The RemoteControl class.
import plugin
import event as em

DEBUG = config.DEBUG

TRUE  = 1
FALSE = 0

# Setting up the default objects:
osd        = osd.get_singleton()

# Module variable that contains an initialized Game() object
_singleton = None

def get_singleton():
    global _singleton

    # One-time init
    if _singleton == None:
        _singleton = Game()
        
    return _singleton

class Game:

    def __init__(self):
        self.mode = None
        self.app_mode = 'games'

    def play(self, item, menuw):

        self.item = item
        self.filename = item.filename 
        self.command = item.command
        self.mode = item.mode
        self.menuw = menuw
        
        if not os.path.isfile(self.filename):
            osd.clearscreen()
            osd.drawstring(_('File "%s" not found!') % self.filename, 30, 280)
            osd.update()
            time.sleep(2.0) 
            self.menuw.refresh()
            return 0

        if plugin.getbyname('MIXER'):
            plugin.getbyname('MIXER').reset()

        if plugin.is_active('joy'):
            try:
                plugin.getbyname('JOY').enable(FALSE)
            except Exception, e:
                print 'getbyname(\'JOY\')', e

        if DEBUG:
            print 'Game.play(): Starting thread, cmd=%s' % self.command
        
        self.app=GameApp(self.command, stop_osd=1)
        self.prev_app = rc.app()
        rc.app(self)


    def stop(self):
        self.app.stop()
        rc.app(None)
        if plugin.is_active('joy'):
            try:
                plugin.getbyname('JOY').enable(TRUE)
            except Exception, e:
                print 'getbyname(\'JOY\')', e


    def eventhandler(self, event, menuw=None):
        return self.item.eventhandler(event, self.menuw)

 
# ======================================================================
class GameApp(childapp.ChildApp2):
    def stop_event(self):
        return em.STOP
