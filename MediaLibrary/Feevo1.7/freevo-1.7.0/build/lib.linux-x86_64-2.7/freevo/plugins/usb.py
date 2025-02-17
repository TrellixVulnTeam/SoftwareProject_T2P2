# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# usb.py - the Freevo usb plugin
# -----------------------------------------------------------------------
# $Id: usb.py 9120 2007-01-31 20:50:52Z duncan $
#
# Notes: This plugin sends an event if an usb device is added
#        or removed
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


import os

import config
import plugin
import util
import rc
from gui import PopupBox

class PluginInterface(plugin.DaemonPlugin):
    """
    This Plugin to scan for usb devices. You should activate this
    plugin if you use mainmenu plugins for special usb devices
    like camera.py.

    You can also set USB_HOTPLUG in your local_config.py to call
    an external program when a device is added. USB_HOTPLUG is a
    list with actions. Each action is also a list of device, message
    and program to call. Limitation: this works only when Freevo shows
    the menu and is not running a video.
    
    Example:
    call pilot-xfer when a pda with the id 082d:0100 is pluged in:
    USB_HOTPLUG = [ ('082d:0100', 'Synchronizing',
                     '/usr/bin/pilot-xfer -t -u /local/visor/current') ]
    """
    def __init__(self):
        plugin.DaemonPlugin.__init__(self)
        self.devices = util.list_usb_devices()
        self.poll_interval = 100 # 1 second


    def config(self):
        return [( 'USB_HOTPLUG', [], 'action list when a devices comes up' )]

    
    def poll(self, menuw=None, arg=None):
        """
        poll to check for devices
        """
        changes = False

        current_devices = util.list_usb_devices()
        for d in current_devices:
            try:
                self.devices.remove(d)
            except ValueError:
                print 'usb.py: new device %s' %d
                for device, message, action in config.USB_HOTPLUG:
                    if d == device:
                        pop = PopupBox(text=message)
                        pop.show()
                        os.system(action)
                        pop.destroy()
                        break
                else:
                    changes = True
                        
        for d in self.devices:
            changes = True
            print 'usb.py: removed device %s' % d

        if changes:
            rc.post_event(plugin.event('USB'))
            
        self.devices = current_devices
