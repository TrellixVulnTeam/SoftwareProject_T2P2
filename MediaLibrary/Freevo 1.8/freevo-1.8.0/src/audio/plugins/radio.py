# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# radio.py - a simple plugin to listen to radio
# -----------------------------------------------------------------------
# $Id: radio.py 10206 2007-12-13 20:38:15Z duncan $
#
# Notes:
# need to have radio installed before using this plugin
# to activate put the following in your local_conf.py
# plugin.activate('audio.radioplayer')
# plugin.activate('audio.radio')
# RADIO_CMD='/usr/bin/radio'
# RADIO_STATIONS = [ ('Sea FM', '90.9'),
#                    ('Kiss 108', '108'),
#                    ('Mix 98.5', '98.5'),
#                    ('Magic 106', '106.7') ]
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
import os, popen2, fcntl, select, time
import glob

#freevo modules
import config, menu, rc, plugin, util
from audio.player import PlayerGUI
from item import Item
from menu import MenuItem
from gui import AlertBox, ConfirmBox


class RadioItem(Item):
    """
    This is the class that actually runs the commands. Eventually
    hope to add actions for different ways of running commands
    and for displaying stdout and stderr of last command run.
    """
    def actions(self):
        """
        return a list of actions for this item
        """
        items = [ ( self.play , _( 'Listen to Radio Station' ) ) ]
        return items


    def checktv(self):
        """ Check if something is recording """
        self.tvlockfile = config.FREEVO_CACHEDIR + '/record.*'
        if len(glob.glob(self.tvlockfile)) > 0:
            return True
        return False


    def play(self, arg=None, menuw=None):
        _debug_('station=%r station_index=%r name=%r' % (self.station, self.station_index, self.name))
        # self.parent.current_item = self
        self.elapsed = 0

        if not self.menuw:
            self.menuw = menuw

        if self.checktv():
            AlertBox(text=_('Cannot play - recording in progress'), handler=self.confirm).show()
            return 'Cannot play with RadioPlayer - recording in progress'

        self.player = PlayerGUI(self, menuw)
        error = self.player.play()

        if error and menuw:
            AlertBox(text=error).show()
            rc.post_event(rc.PLAY_END)


    def confirm (self, arg=None, menuw=None):
        _debug_('confirm (self, arg=%r, menuw=%r)' % (arg, menuw))
        if menuw:
            menuw.menu_back()
            #menuw.refresh()


    def stop(self, arg=None, menuw=None):
        """
        Stop the current playing
        """
        _debug_('stop')
        self.player.stop()



class RadioMainMenuItem(MenuItem):
    """
    this is the item for the main menu and creates the list
    of commands in a submenu.
    """
    def __init__(self, parent):
        MenuItem.__init__(self, parent, arg='radio', skin_type='radio')
        self.name = _( 'Radio' )


    def actions(self):
        """
        return a list of actions for this item
        """
        return [ ( self.create_stations_menu , 'stations' ) ]


    def create_stations_menu(self, arg=None, menuw=None):
        station_items = []
        for rstation in config.RADIO_STATIONS:
            radio_item = RadioItem()
            radio_item.name = rstation[0]
            radio_item.station = rstation[1]
            radio_item.url = 'radio://' + str(rstation[1])
            radio_item.type = 'radio'
            radio_item.station_index = config.RADIO_STATIONS.index(rstation)
            radio_item.length = 0
            radio_item.remain = 0
            radio_item.elapsed = 0
            radio_item.info = {'album':'', 'artist':'', 'trackno': '', 'title':''}
            station_items += [ radio_item ]
        if (len(station_items) == 0):
            station_items += [menu.MenuItem( _( 'No Radio Stations found' ),
                                             menwu.goto_prev_page, 0)]
        station_menu = menu.Menu( _( 'Radio Stations' ), station_items)
        rc.app(None)
        menuw.pushmenu(station_menu)
        menuw.refresh()



class PluginInterface(plugin.MainMenuPlugin):
    """
    This plugin uses the command line program radio to tune a
    bttv card with a radio tuner to a radio station to listen
    to. You need to also use the RadioPlayer plugin to actually
    listen to the station.

    need to have radio installed before using this plugin.
    radio is availble in binary form for most linux distros.

    to activate put the following in your local_conf.py:
    | plugin.activate('audio.radioplayer')
    | plugin.activate('audio.radio')
    | RADIO_CMD='/usr/bin/radio'
    | RADIO_STATIONS = [
    |     ('Sea FM', '90.9'),
    |     ('Kiss 108', '108'),
    |     ('Mix 98.5', '98.5'),
    |     ('Magic 106', '106.7')
    | ]
    """

    def items(self, parent):
        return [ RadioMainMenuItem(parent) ]
