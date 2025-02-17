# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# base.py - base osd module for livepause osd
# -----------------------------------------------------------------------
# $Id: base.py 11479 2009-05-07 17:34:38Z duncan $
#
# Notes:
#
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

class OSD(object):
    """
    Base class for OSD display.
    """

    def __init__(self):
        """
        Creates an OSD object linked to a Player.
        """

    def display_info(self, info_func):
        """
        Display an OSD for live pause/EPG information.
        The live pause information is return by calling the supplied function,
        this should return a dictionary containing the follow keys:
            - channel      : Channel being viewed.
            - current_time : Current time being viewed.
            - start_time   : Time at the start of the buffer.
            - end_time     : Time at the end of the buffer.
            - percent_through_buffer : Percentage through the buffer contents.
            - percent_buffer_full    : Percentage of the buffer that has been filled.

        @param info_func: Function used to retrieve a dictionary of
        live pause status information.
        """
        pass

    def display_buffer_pos(self, info_func):
        """
        Display an OSD for live pause buffer information.
        The live pause information is return by calling the supplied function,
        this should return a dictionary containing the follow keys:
            - channel      : Channel being viewed.
            - current_time : Current time being viewed.
            - start_time   : Time at the start of the buffer.
            - end_time     : Time at the end of the buffer.
            - percent_through_buffer : Percentage through the buffer contents.
            - percent_buffer_full    : Percentage of the buffer that has been filled.

        @param info_func: Function used to retrieve a dictionary of
        live pause status information.
        """
        pass

    def display_channel_number(self, number):
        """
        Display a channel number as it is being entered by the user.
        @param number: The number entered so far.
        """
        pass

    def hide(self):
        """
        Hide the last dialog/text shown.
        """
        pass
