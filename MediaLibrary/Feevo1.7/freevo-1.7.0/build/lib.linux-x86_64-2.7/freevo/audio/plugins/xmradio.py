# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# xmradio.py - a simple plugin to listen to xmradio online
# -----------------------------------------------------------------------
# $Id: xmradio.py 9127 2007-02-02 18:05:51Z duncan $
#
# Notes: 
# need to have an XM Radio account with a username and password
# to activate put the following in your local_conf.py
# plugin.activate('audio.xmradio')
# plugin.activate('audio.xmradioplayer')
# XM_USER='Your user name'
# XM_PASS='Your password'
# XM_RATE='high'
# XM_STATIONS = [ ('High Voltage', '202'),
#                 ('Home Ice', '204'),
#                 ('Music Lab', '51') ]
# Todo: 
#
# -----------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2003 Krister Lagerstrom, et al. 
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


#python modules
import os, popen2, fcntl, select, time, re

#freevo modules
import config, menu, rc, plugin, util, re
from audio.player import PlayerGUI
from audio.audioitem import AudioItem
from item import Item


class XmRadioItem(AudioItem):
    """
    This is the class that actually runs the commands. Eventually
    hope to add actions for different ways of running commands
    and for displaying stdout and stderr of last command run.
    """
    def actions(self):
        """
        return a list of actions for this item
        """
        items = [ ( self.play , _( 'Listen to XM Station' ) ) ]
        return items


    def play(self, arg=None, menuw=None):
        self.elapsed = 0

        if not self.menuw:
            self.menuw = menuw

        self.player = PlayerGUI(self, menuw)
        error = self.player.play()

        if error and menuw:
            AlertBox(text=error).show()
            rc.post_event(rc.PLAY_END)

    def stop(self, arg=None, menuw=None):
        """
        Stop the current playing
        """
        print 'XmRadioItem stop'
        self.player.stop()



class XmRadioMainMenuItem(Item):
    """
    this is the item for the main menu and creates the list
    of commands in a submenu.
    """
    def __init__(self, parent):
        Item.__init__(self, parent, skin_type='radio')
        self.name = _( 'XM Radio' )


    def actions(self):
        """
        return a list of actions for this item
        """
        return [ ( self.create_channels_menu , 'XM channels' ) ]

 
    def create_channels_menu(self, arg=None, menuw=None):
        string='rm -f /%s/xmonline.cookies'%config.LOGDIR
        os.system(string)

        string=('curl -s -c /%s/xmonline.cookies -d "user_id=%s" -d "pword=%s" \
                "http://xmro.xmradio.com/xstream/login_servlet.jsp" > /%s/xmonlinelogin.out' \
                % (config.LOGDIR, config.XM_USER, config.XM_PASS, config.LOGDIR))
        os.system(string)

        channel_items = []
        for rchannel in config.XM_STATIONS:
            string='rm -f /%s/xmonlinechannel.out'%config.LOGDIR
            os.system(string)

            string=('curl -s \
                    -b /%s/xmonline.cookies \
                    -d "" \
                    "http://player.xmradio.com/player/2ft/playMedia.jsp?ch=%s&speed=%s" \
                    > /%s/xmonlinestream.out' \
                    % (config.LOGDIR,rchannel[1],config.XM_RATE,config.LOGDIR))
            os.system(string)
            file = open('/%s/xmonlinestream.out'%config.LOGDIR,'r')
            text = file.readlines()
            file.close()
            for line in text:
                if re.search('FileName', line):
                   (split)=re.split('"', line)
                   url=split[3]
            radio_item = XmRadioItem(url,self,str(rchannel[0]))
            channel_items += [ radio_item ]
        if (len(channel_items) == 0):
            channel_items += [menu.MenuItem( _( 'No XM channels found' ), menwu.goto_prev_page, 0)]
        channel_menu = menu.Menu( _( 'XM channels' ), channel_items)
        rc.app(None)
        menuw.pushmenu(channel_menu)
        menuw.refresh()



class PluginInterface(plugin.MainMenuPlugin):
    """
    need to have an XM Radio account with a username and password
    to activate put the following in your local_conf.py          
    plugin.activate('audio.xmradioplayer')
    plugin.activate('audio.xmradio')      
    XM_CMD='xine'
    XM_STATIONS = [ ('High Voltage', '202'),
                    ('Home Ice', '204'),
                    ('Music Lab', '51') ]
    """
    def items(self, parent):
        return [ XmRadioMainMenuItem(parent) ]
