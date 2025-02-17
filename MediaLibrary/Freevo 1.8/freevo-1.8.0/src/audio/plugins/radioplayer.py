# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# radioplayer.py - the Freevo Radioplayer plugin for radio
# -----------------------------------------------------------------------
# $Id: radioplayer.py 10206 2007-12-13 20:38:15Z duncan $
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


import time, os
import string
import re
import thread

import rc         # To post events
import config     # Configuration handler. reads config file.
import util       # Various utilities
import plugin
from event import *


class PluginInterface(plugin.Plugin):
    """
    This is the player plugin for the radio. Basically it tunes all the
    radio stations set in the radio plugin and does the interaction
    between the radio command line program and freevo. please see the
    audio.radio plugin for setup information
    """

    def __init__(self):
        plugin.Plugin.__init__(self)

        # register it as the object to play audio
        plugin.register(RadioPlayer(), plugin.AUDIO_PLAYER, True)

class RadioPlayer:

    def __init__(self):
        self.mode = 'idle'
        self.name = 'radioplayer'
        self.app_mode = 'audio'
        self.app = None
        self.starttime = 0

    def rate(self, item):
        """
        How good can this player play the file:
        2 = good
        1 = possible, but not good
        0 = unplayable
        """
        try:
            _debug_('url=%r' % (item.url), 2)
            _debug_('item.__dict__=%r' % (item.__dict__))
        except Exception, e:
            _debug_('%s' % e)
        if item.url.startswith('radio://'):
            _debug_('%r good' % (item.url))
            return 2
        _debug_('%r unplayable' % (item.url))
        return 0


    def play(self, item, playerGUI):
        """
        play a radioitem with radio player
        """
        self.playerGUI = playerGUI
        self.item = item
        self.item.elapsed = 0
        self.starttime = time.time()

        try:
            _debug_('play() %s' % self.item.station)
        except AttributeError:
            return 'Cannot play with RadioPlayer - no station'

        self.mode = 'play'

        mixer = plugin.getbyname('MIXER')
        if mixer:
            mixer_vol = config.MIXER_VOLUME_RADIO_IN
            mixer.setLineinVolume(mixer_vol)
            mixer.setIgainVolume(mixer_vol)
            mixer.setMicVolume(mixer_vol)
        #print 'RadioPlayer mixer is %s' % mixer

        if config.RADIO_CMD.find('ivtv-radio') >= 0:
            # IVTV cards
            _debug_('%s -f %s &' % (config.RADIO_CMD, self.item.station))
            os.system('%s -f %s &' % (config.RADIO_CMD, self.item.station))
        else:
            # BTTV cards
            _debug_('%s' % (config.RADIO_CMD_START % self.item.station))
            os.system('%s' % (config.RADIO_CMD_START % self.item.station))
        thread.start_new_thread(self.__update_thread, ())

        rc.app(self)
        rc.post_event(PLAY_START)
        return None


    def stop(self):
        """
        Stop mplayer and set thread to idle
        """
        print 'Radio Player Stop'
        self.mode = 'stop'
        mixer = plugin.getbyname('MIXER')
        if mixer:
            mixer.setLineinVolume(0)
            mixer.setMicVolume(0)
            mixer.setIgainVolume(0) # Input on emu10k cards.
        #else:
        #    print 'Radio Player failed to find a mixer'
        if config.RADIO_CMD.find('ivtv-radio') >= 0:
            # IVTV cards
            os.system('killall -9 aplay')
        else:
            # BTTV cards
            _debug_('%s' % (config.RADIO_CMD_STOP))
            os.system('%s' % config.RADIO_CMD_STOP)

        rc.post_event(PLAY_END)
        rc.app(None)


    def is_playing(self):
        #print 'Radio Player IS PLAYING?'
        return self.mode == 'play'


    def refresh(self):
        #print 'Radio Player refresh'
        self.item.elapsed = int(time.time() - self.starttime)
        self.playerGUI.refresh()


    def eventhandler(self, event, menuw=None):
        """
        eventhandler for mplayer control. If an event is not bound in this
        function it will be passed over to the items eventhandler
        """
        print 'Radio Player event handler %s' % event
        if event in ( STOP, PLAY_END, USER_END ):
            self.playerGUI.stop()
            return self.item.eventhandler(event)
        else:
            # everything else: give event to the items eventhandler
            return self.item.eventhandler(event)


    def __update_thread(self):
        """
        OSD update thread
        """
        while self.is_playing():
            self.refresh()
            time.sleep(0.3)
