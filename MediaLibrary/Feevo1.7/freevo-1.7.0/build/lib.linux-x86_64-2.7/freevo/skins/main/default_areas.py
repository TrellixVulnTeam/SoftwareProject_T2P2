# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# default_areas.py - Some areas for the skin
# -----------------------------------------------------------------------
# $Id: default_areas.py 8594 2006-11-21 22:32:05Z duncan $
#
# Notes: This file contains only small areas, other areas like
#        ListingArea have there own file
#
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
import osd
import plugin

from area import Skin_Area

# Create the OSD object
osd = osd.get_singleton()


class Screen_Area(Skin_Area):
    """
    this area is the screen or background of the skin
    """
    def __init__(self):
        Skin_Area.__init__(self, 'screen', imagecachesize=3)

    def update_content_needed(self):
        """
        this area needs never a content update
        """
        return False

    def update_content(self):
        """
        there is no content in this area
        """
        pass



class Title_Area(Skin_Area):
    """
    in this area the title of the menu is drawn
    """
    def __init__(self):
        Skin_Area.__init__(self, 'title')
        self.text = ''

        
    def update_content_needed(self):
        """
        check if the content needs an update. This function does the same as
        update_content, so it's faster to return always 1
        """
        return 1


    def update_content(self):
        """
        update the content
        """
        menu      = self.menu
        layout    = self.layout
        area      = self.area_val
        content   = self.calc_geometry(layout.content, copy_object=True)

        text = ''
        try:
            item = menu.selected
            if content.type == 'menu':
                text = menu.heading
            elif len(menu.choices) == 0:
                text = ''
            elif content.type == 'short item':
                if item.type == 'video' and item.tv_show and \
                       ((item.image and not item.image.endswith('.raw')) or \
                        (item.parent and item.parent.name == item.show_name[0])):
                    sn   = item.show_name
                    text = sn[1] + "x" + sn[2] + " - " + sn[3] 
                elif item.parent and len(item.parent.name) > 5 and \
                         Unicode(item.name).startswith(Unicode(item.parent.name)):
                    text = item.name[len(item.parent.name):].strip(' -_')
                    if not text:
                        text = item.name
                else:
                    text = item.name
            else:
                text = item.name
        except AttributeError:
            try:
                if menu.type == 'tv':
                    if content.type == 'item' or content.type == 'short item':
                        text = menu.table[1].title
                    else:
                        text = _('TV GUIDE')
            except:
                pass

        if not text:
            if hasattr(self.infoitem, 'name'):
                text = self.infoitem.name
            else:
                if content.type == 'short item' and hasattr(menu, 'subtitle'):
                    text = menu.subtitle
                elif hasattr(menu, 'title'):
                    text = menu.title

        self.text = text
        self.drawstring(text, content.font, content, mode='hard')



class Subtitle_Area(Title_Area):
    """
    in this area the subtitle of the menu is drawn
    """
    def __init__(self):
        Skin_Area.__init__(self, 'subtitle')
        self.text = ''



class Plugin_Area(Skin_Area):
    """
    in this area all plugins can draw
    """
    def __init__(self):
        Skin_Area.__init__(self, 'plugin')
        self.plugins = None
        self.x = config.OSD_OVERSCAN_X
        self.y = config.OSD_OVERSCAN_Y
        self.width   = osd.width  - 2 * config.OSD_OVERSCAN_X
        self.height  = osd.height - 2 * config.OSD_OVERSCAN_Y

        
    def __str__(self):
        return 'x=%s, y=%s, width=%s, height=%s' % (self.x, self.y, self.width, self.height)


    def get_font(self, name):
        try:
            return self.xml_settings.font[name]
        except:
            return self.xml_settings.font['default']
    

    def update_content(self):
        """
        there is no content in this area
        """
        if self.plugins == None:
            self.plugins = plugin.get('daemon_draw')

        for p in self.plugins:
            p.draw((self.widget_type, self.menuw), self)

