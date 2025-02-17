# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# ProgressBox.py - simple box with progress bar
# -----------------------------------------------------------------------
# $Id: ProgressBox.py 8441 2006-10-21 11:15:52Z duncan $
#
# Notes:
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


import config

from GUIObject   import *
from PopupBox    import PopupBox
from Progressbar import Progressbar

class ProgressBox(PopupBox):
    """
    x         x coordinate. Integer
    y         y coordinate. Integer
    width     Integer
    height    Integer
    text      String to print.
    icon      icon
    """

    def __init__(self, text, x=None, y=None, width=0, height=0,
                 icon=None, vertical_expansion=1, text_prop=None,
                 full=0, parent='osd'):

        PopupBox.__init__(self, text, None, x, y, width, height,
                          icon, vertical_expansion, text_prop, parent)

        self.progressbar = Progressbar(full=full, width=self.content.width-20)
        self.add_child(self.progressbar)


    def tick(self):
        self.progressbar.tick()
        self.draw(update=True)
