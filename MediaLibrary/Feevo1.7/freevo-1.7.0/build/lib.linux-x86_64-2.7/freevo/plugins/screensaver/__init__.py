# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# screensaver/__init__.py - the Freevo Screensaver
# -----------------------------------------------------------------------
# $Id: __init__.py 9181 2007-02-08 20:35:29Z duncan $
#
# Notes:
#
# Todo:
#
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


import time
import os
import random 
import thread
import traceback
import pygame

import config
import plugin
import rc

from event import Event
import osd
import skin

# Set to 1 for debug output
DEBUG = config.DEBUG

osd = osd.get_singleton()
skin = skin.get_singleton()

class PluginInterface(plugin.DaemonPlugin):
    """
    """
    def __init__(self):
        plugin.DaemonPlugin.__init__(self)
        self.event_listener = True
        self.poll_menu_only = True
        
        self.last_event = time.time()
        self.screensaver_showing = False
        self.menuw = None
        self.start_delay = config.SCREENSAVER_DELAY
        self.cycle_time = config.SCREENSAVER_CYCLE_TIME
        self.plugins = None   
        _debug_('Screensaver install (delay = %d)' % self.start_delay)


    def config(self):
        return [ ('SCREENSAVER_DELAY', 300, '# of seconds to wait to start saver.'),
                  ('SCREENSAVER_CYCLE_TIME', 60, '# of seconds to run a screensaver before starting another saver.')
                ]

    def eventhandler(self, event = None, menuw=None, arg=None):
        """
        eventhandler to handle the events. Always return False since we
        are just a listener and really can't send back True.
        """
        _debug_("Saver saw %s" % event.name)
        if menuw:
            self.menuw = menuw

        if event.name == 'SCREENSAVER_START':
            if not self.screensaver_showing:
                self.start_saver()
            return True

        if event.name == 'SCREENSAVER_STOP' and self.screensaver_showing :
            self.stop_saver()
            return True

        # gotta ignore these or video screensavers shutoff before they begin
        if event.name == 'VIDEO_START' or event.name == 'PLAY_START' or event.name == 'VIDEO_END' or event.name == 'PLAY_END':
            return False

        if not event.name == 'IDENTIFY_MEDIA':
            self.last_event = time.time()
            
        if self.screensaver_showing :
            self.stop_saver()
            return True

        return False

    def poll(self):
        #_debug_("Saver got polled %f" % time.time())
        time_diff = time.time() - self.last_event
        if not self.screensaver_showing and  time_diff > self.start_delay :
            rc.post_event(Event("SCREENSAVER_START"))

    def start_saver (self):
        _debug_("start screensaver")
        self.screensaver_showing = True
        if self.plugins is None:
            self.plugins = plugin.get('screensaver')
            print 'Plugins =', self.plugins
        skin.clear()
        # Start Screensaver thread
        self.stop_screensaver = False
        thread.start_new_thread(self.__run__,())

    def stop_saver (self):
        _debug_("stop screensaver")
        self.stop_screensaver = True

    def __run__(self):
        _debug_('Screensaver thread started')
        current_saver = None
        index = 0
        plugins_count = len(self.plugins)
        while not self.stop_screensaver:
            # No current screensaver so select one of the installed screensaver
            # plugins at random
            if current_saver is None:
                if plugins_count == 1:
                    current_saver = self.plugins[0]
                elif plugins_count > 1 and plugins_count <= 4:
                    current_saver = self.plugins[index]
                    index += 1
                    if index > plugins_count:
                        index = 0
                elif plugins_count > 4:
                    index = random.randint(0, len(self.plugins) - 1)
                    current_saver = self.plugins[index]
            
            # No screensaver found just sleep for 200ms
            if current_saver is None:
                time.sleep(0.200)
            else:
                self.__run_screensaver__(current_saver)

        self.screensaver_showing = False
        skin.force_redraw = True
        skin.redraw()
        osd.update()
        _debug_('Screensaver thread stopped')
        
    def __run_screensaver__(self, screensaver):
        _debug_('Running %s' % screensaver.plugin_name)
        try:
            fps = screensaver.start(osd.width, osd.height)
            
            max_iterations = int(self.cycle_time / (1.0 / fps))
            iteration = 0
            clock = pygame.time.Clock()
            
            while (not self.stop_screensaver) and (iteration < max_iterations):
                # Draw the screen and update the display
                screensaver.draw(osd.screen)
                pygame.display.flip()
                
                clock.tick(fps)
                iteration += 1
                
            screensaver.stop()
        except:
            print 'Screensaver %s crashed!' % screensaver.plugin_name
            traceback.print_exc()
            # Remove the broken screensaver so we don't try to run it again
            self.plugins.remove(screensaver)
            
        osd.clearscreen(osd.COL_BLACK)
        osd.update()



class ScreenSaverPlugin(plugin.Plugin):
    def __init__(self):
        plugin.Plugin.__init__(self)
        self._type = 'screensaver'


    def start(self, width, height):
        """
        Initialise the screensaver before each run.
        Returns the number of frames per second the saver
        wants to run at.
        """
        return 25

    
    def stop(self):
        """
        Deinitialise the screensaver after each run.
        """
        pass

    
    def draw(self, surface):
        """
        Draw a frame onto the supplied surface called
        every 1/fps seconds (where fps was returned by start())
        """
        pass
