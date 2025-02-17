# -----------------------------------------------------------------------
# detach.py - Detach plugin for the audio player
# -----------------------------------------------------------------------
# $Id: detach.py 10118 2007-11-14 20:23:21Z duncan $
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


import config
import plugin
import menu
import rc
import audio.player

from event import *

class PluginInterface(plugin.MainMenuPlugin):
    """
    plugin to detach the audio player to e.g. view pictures while listening
    to music
    """

    def __init__(self):
        _debug_('detach.PluginInterface.__init__(self)', 2)
        plugin.MainMenuPlugin.__init__(self)
        config.EVENTS['audio'][config.DETACH_KEY] = Event(FUNCTION_CALL, arg=self.detach)
        self.show_item = menu.MenuItem(_('Show player'), action=self.show)
        self.show_item.type = 'detached_player'


    def config(self):
        '''config is called automatically,
        freevo plugins -i audio.detach returns the info
        '''
        return [
            ('DETACH_KEY', 'DISPLAY', 'Event to activate the detach bar, DISPLAY, ENTER, EXIT'),
        ]

    def detach(self):
        _debug_('detach(self)', 2)
        gui  = audio.player.get()

        # hide the player and show the menu
        mpav = plugin.getbyname( 'audio.mpav' )
        if mpav:
            mpav.stop_mpav()

        mplvis = plugin.getbyname( 'audio.mplayervis' )
        if mplvis:
            mplvis.stop_visual()

        gui.hide()
        gui.menuw.show()

        # set all menuw's to None to prevent the next title to be
        # visible again
        gui.menuw = None
        gui.item.menuw = None
        if gui.item.parent:
            gui.item.parent.menuw = None
        rc.post_event(plugin.event('DETACH'))

    def eventhandler(self, event, menuw=None):
        _debug_('eventhandler(self, event, menuw=None)', 2)
        if event == BUTTON:
            gui = audio.player.get()
            if gui:
                p = gui.player
                if event.arg=='FFWD':
                    p.eventhandler(Event('SEEK', arg='10', context='audio'))
                elif event.arg=='REW':
                    p.eventhandler(Event('SEEK', arg='-10', context='audio'))
                elif event.arg=='PAUSE':
                    p.eventhandler(Event('PLAY', context='audio'))
                elif event.arg=='STOP':
                    p.eventhandler(Event('STOP'))
                elif event.arg=='NEXT':
                    p.eventhandler(Event('PLAYLIST_NEXT', context='audio'))
                elif event.arg=='PREV':
                    p.eventhandler(Event('PLAYLIST_PREV', context='audio'))
        elif event == VIDEO_START:
            gui = audio.player.get()
            if gui:
                gui.player.eventhandler(Event('STOP'))


    def items(self, parent):
        _debug_('items(self, parent)', 2)
        gui = audio.player.get()
        if gui and gui.player.is_playing():
            self.show_item.parent = parent
            return [ self.show_item ]
        return []


    def show(self, arg=None, menuw=None):
        _debug_('show(self, arg=None, menuw=None)', 2)
        gui = audio.player.get()

        # restore the menuw's
        gui.menuw = menuw
        gui.item.menuw = menuw
        if gui.item.parent:
            gui.item.parent.menuw = menuw

        # hide the menu and show the player
        menuw.hide()
        gui.show()

        ### TODO: is this plugin still around?
        # maybe we can remove this lines savely
        mpav = plugin.getbyname( 'audio.mpav' )
        if mpav:
            mpav.start_mpav()

        mplvis = plugin.getbyname( 'audio.mplayervis' )
        if mplvis:
            mplvis.stop_visual()
            mplvis.start_visual()
