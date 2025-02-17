# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# logger.py - Sqlite Play Counter
# -----------------------------------------------------------------------
# $Id: logger.py,v 1.3 2004/07/10 12:33:38 dischi Exp $
#
# Notes:
# Todo: 
#
# -----------------------------------------------------------------------
# $Log: logger.py,v $
# Revision 1.3  2004/07/10 12:33:38  dischi
# header cleanup
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
# ----------------------------------------------------------------------- */


import skin,audio.player,plugin
import config
from event import *
from util.dbutil import *
import rc
import util
import os
import time

DEBUG = config.DEBUG

class PluginInterface(plugin.DaemonPlugin):
    def __init__(self):
        plugin.DaemonPlugin.__init__(self)
        self.plugin_name = 'audio.logger'
        plugin.register(self, self.plugin_name)
        self.db = MetaDatabase()
        

    def runquery(self,query):
        self.db.runQuery(query)
        self.db.commit()

    def log_track(self, filename):
        query = 'UPDATE music SET play_count=play_count+1,last_play=%f WHERE \
                 path = "%s" and filename = "%s"' % (time.time(),  
                 util.escape(os.path.dirname(filename)), 
                 util.escape(os.path.basename(filename)) )
        self.runquery(query)

    def log_rating(self, filename, rating):
        query = 'UPDATE music SET rating=%i WHERE \
                 path = "%s" and filename = "%s"' % (int(rating),  
                 util.escape(os.path.dirname(filename)), 
                 util.escape(os.path.basename(filename)) )
        self.runquery(query)

    def eventhandler(self, event, menuw=None):
        if event == AUDIO_LOG:
            self.log_track(event.arg)
        if event == RATING and str(event.arg[0]) in '12345':
            self.log_rating(event.arg[1],event.arg[0])
            rc.post_event(Event(OSD_MESSAGE,'Rated: %s' % str(event.arg[0])))
