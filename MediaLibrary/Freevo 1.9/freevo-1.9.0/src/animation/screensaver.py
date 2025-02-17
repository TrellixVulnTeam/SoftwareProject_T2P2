# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# screensaver.py - A screensaver animation
# Author: Viggo Fredriksen <viggo@katatonic.org>
# -----------------------------------------------------------------------
# $Id: screensaver.py 9561 2007-05-11 18:22:36Z duncan $
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

# freevo modules
from animation import BaseAnimation

class Screensaver(BaseAnimation):
    """
    This is _very_ simplistic. Feel free to add what you want
    """
    def __init__(self):
        BaseAnimation.__init__(self, self.get_osd().screen.get_rect(),
                               fps=5, bg_update=True, bg_redraw=True)

        self.overlay = self.get_surface(self.rect.width,
                                        self.rect.height).convert_alpha()
        self.overlay.fill(0x66000000)

    def draw(self):
        self.surface.blit(self.overlay, (0,0))
