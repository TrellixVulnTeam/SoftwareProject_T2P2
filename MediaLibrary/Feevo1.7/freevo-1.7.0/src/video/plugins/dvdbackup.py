#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# dvdbackup.py - Plugin for encoding DVD's with the EncodingServer
# -----------------------------------------------------------------------
# $Id: dvdbackup.py 9034 2007-01-21 17:25:06Z duncan $
#
# Author: 
# Todo:
# niceness & pausing queue
#
# -----------------------------------------------------------------------
# Copyright (C) 2004 den_RDC (RVDM)
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
# with this program; if not, write to the Free Software Foundation
#
# -----------------------------------------------------------------------

#Import statements
from os.path import join, split
import plugin, config, menu
from video.encodingclient import *
from gui.AlertBox import AlertBox
from gui.PopupBox import PopupBox
import config

DEBUG=config.DEBUG

class PluginInterface(plugin.ItemPlugin):
    """
    PLugin for making DVD backups (aka dvdrips) using EncodingServer
    
    This plugin NEEDS a running encodingserver to work properly.
    You can start an encodingserver with "freevo encodingserver start".
    Don't forget that you need some free diskspace in order to use this plugin, 
    and don't forget a dvdrip eats quite a bit of space :)
    """

    def actions(self, item):
        if DEBUG >= 1:
            #testing stuff
            if hasattr(item, 'type'):
                print 'item.type=\"%s\"' % (item.type)
            if hasattr(item, 'mode'):
                print 'item.mode=\"%s\"' % (item.mode)
            if hasattr(item, 'info_type'):
                print 'item.info_type=\"%s\"' % (item.info_type)
            if hasattr(item, 'name'):
                print 'item.name=\"%s\"' % (item.name)
            if hasattr(item, 'filename'):
                print 'item.filename=\"%s\"' % (item.filename)
            if hasattr(item, 'parentname'):
                print 'item.parentname=\"%s\"' % (item.parentname)
            if hasattr(item, 'media') and hasattr(item.media, 'devicename'):
                print 'item.media.devicename=\"%s\"' % (item.media.devicename)
            
        if item.type == 'video' and item.mode == 'dvd' and hasattr(item, 'info_type'):
            if item.info_type == "track": #and item.media and item.media.devicename: 
                #for dvd on disc
                self.dvdsource = item.filename
                self.title = int(split(item.url)[-1])
                
                if hasattr(item, 'media') and hasattr(item.media, 'devicename'):
                    #we have a "real" dvd disc
                    self.dvdsource = item.media.devicename
                    self.title = int(item.url[6:])

                self.item = item
                return [ (self.encoding_profile_menu, _('Backup this dvd title...')) ]
        return []
        
    def encoding_profile_menu(self, menuw=None, arg=None):
        #create a menu with a few encoding options (1cd, 2cd, xvid, mpeg4)
        #args : tuple, (videocodec, size, multipass
        menu_items = [ menu.MenuItem("XviD, 700mb", self.create_job, (1,700,False,0)) ]
        menu_items.append( menu.MenuItem("XviD, 700mb, High Quality", self.create_job, (1,700,True,0)) )
        menu_items.append( menu.MenuItem("XviD, 1400mb", self.create_job, (1,1400,False,0)) )
        menu_items.append( menu.MenuItem("XviD, 1400mb, High Quality", self.create_job, (1,1400,True,0)) )
        menu_items.append( menu.MenuItem("DivX, 700mb", self.create_job, (0,700,False,0)) )
        menu_items.append( menu.MenuItem("DivX, 700mb, High Quality", self.create_job, (0,700,True,0)) )
        menu_items.append( menu.MenuItem("DivX, 1400mb", self.create_job, (0,1400,False,0)) )
        menu_items.append( menu.MenuItem("DivX, 1400mb, High Quality", self.create_job, (0,1400,True,0)) )
        
        encoding_menu = menu.Menu(_('Choose your encoding profile'), menu_items)
        menuw.pushmenu(encoding_menu)
        
    def create_job(self, menuw=None, arg=None):
        '''
        '''
        #create a filename for the to-be-encoded dvd title
        #title = int(self.item.url[6:])
        fname = join(config.VIDEO_ITEMS[0][1], "%s_%s.avi" % (self.item.parent.name, self.title))
        #print title, fname
        print arg
        #unwrap settings tupple
        vcodecnr, tgtsize, mpass, vbitrate = arg

        #we are going to create a job and send it to the encoding server, this can take some time while analyzing
        
        box = PopupBox(text=_('Please wait, analyzing video...'))
        box.show()

        (status, resp) = initEncodeJob(self.dvdsource, fname, 
                self.item.parent.name, self.title)
                
        box.destroy()
        
        if not status:
            self.error(resp)
            return
            
        idnr = resp
        
        #ask for possible containers and set the first one (should be avi), we will get a list
        (status, resp) = getContainerCAP(idnr)
            
        if not status:
            self.error(resp)
            return
        
        container = resp[0]
        
        (status, resp) = setContainer(idnr, container)
        
        if not status:
            self.error(resp)
            return
            
        #ask for possible videocodec and set the first one (should be mpeg4), we will get a list
        (status, resp) = getVideoCodecCAP(idnr)
            
        if not status:
            self.error(resp)
            return
        
        vcodec = resp[vcodecnr]
        
        (status, resp) = setVideoCodec(idnr, vcodec, tgtsize, mpass, vbitrate)
        
        if not status:
            self.error(resp)
            return
            
        #ask for possible audiocodec and set the first one (should be mp3), we will get a list
        #Audiocodec call isn't necessary atm, it defaults to 128 kbit mp3, but this might change in the future
        #so we play safe
        (status, resp) = getAudioCodecCAP(idnr)
            
        if not status:
            self.error(resp)
            return
        
        acodec = resp[0]
        
        (status, resp) = setAudioCodec(idnr, acodec, 128)
        
        if not status:
            self.error(resp)
            return
        
        #And finally, qeue and start the job
        (status, resp) = queueIt(idnr, True)
            
        if not status:
            self.error(resp)
            return
        
        self.menuw = menuw
        AlertBox(width=400, height=200, text=_("Encoding started"), handler=self.mopup).show()
        
        print "boe"
        #menuw.delete_menu()
        #menuw.delete_menu()       
        
        
        
    def error(self, text=""):
        AlertBox(width=400, height=200, text="ERROR: %s" % text).show()
        
    
    def mopup(self):
        self.menuw.delete_menu()
        self.menuw.back_one_menu()
