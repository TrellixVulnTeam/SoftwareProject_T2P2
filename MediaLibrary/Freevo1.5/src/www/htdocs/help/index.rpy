#!/usr/bin/python

#if 0 /*
# -----------------------------------------------------------------------
# help.rpy - The help index to the web interface.
# -----------------------------------------------------------------------
# $Id: index.rpy,v 1.7 2004/02/19 04:57:59 gsbarbieri Exp $
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log: index.rpy,v $
# Revision 1.7  2004/02/19 04:57:59  gsbarbieri
# Support Web Interface i18n.
# To use this, I need to get the gettext() translations in unicode, so some changes are required to files that use "print _('string')", need to make them "print String(_('string'))".
#
# Revision 1.6  2004/02/09 21:23:42  outlyer
# New web interface...
#
# * Removed as much of the embedded design as possible, 99% is in CSS now
# * Converted most tags to XHTML 1.0 standard
# * Changed layout tables into CSS; content tables are still there
# * Respect the user configuration on time display
# * Added lots of "placeholder" tags so the design can be altered pretty
#   substantially without touching the code. (This means using
#   span/div/etc. where possible and using 'display: none' if it's not in
#   _my_ design, but might be used by someone else.
# * Converted graphical arrows into HTML arrows
# * Many minor cosmetic changes
#
# Revision 1.5  2004/02/06 20:30:33  dischi
# some layout updates
#
# Revision 1.4  2003/11/06 19:57:54  mikeruelle
# remove hard links so we can run when proxied
#
# Revision 1.3  2003/10/31 18:56:15  dischi
# Add framework for plugin writing howto
#
# Revision 1.2  2003/10/07 17:14:21  dischi
# typo
#
# Revision 1.1  2003/09/23 18:24:07  dischi
# moved help to a new directory and add more docs
#
# Revision 1.2  2003/09/12 22:00:00  dischi
# add more documentation
#
# Revision 1.1  2003/09/12 20:34:16  dischi
# start internal help system
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
#endif

import util
from www.web_types import HTMLResource, FreevoResource

class HelpResource(FreevoResource):

    def _render(self, request):
        fv = HTMLResource()
        fv.printHeader(_('Freevo Help'), '/styles/main.css', prefix=request.path.count('/')-1)
        fv.res += '<div id="content">'
        fv.res += '&nbsp;<br/>'
        fv.res += _('This is the internal Freevo documentation. The documents \
        are in an early stage of development, if you like to help, please \
        contact the developers. You find more informations like \
        the <a href="http://freevo.sourceforge.net/cgi-bin/moin.cgi/FrontPage">\
        WiKi (online manual)</a> and mailing lists on the \
        <a href="http://www.freevo.org">Freevo Homepage</a>.\
        Everyone can edit the WiKi (and we can revert them if someone deletes \
        informations), feel free to add informations there.')

        fv.res += '<p><b>'+_('Index')+'</b><ol>'
        
        fv.res += '<li><a href="howto.rpy">'+_('Freevo Installation Howto')+'</a></li>'
        fv.res += '<li><a href="doc.rpy?file=faq">'+_('Frequently Asked Questions')+'</a></li>'
        fv.res += '<li><a href="doc.rpy?file=recording">'+_('Recording Information')+'</a></li>'
        fv.res += '<li><a href="plugins.rpy">'+_('Plugin List')+'</a></li>'
        fv.res += '<li><a href="doc.rpy?file=FxdFiles">'+_('FXD files')+'</a></li>'
        fv.res += '<li><a href="doc.rpy?file=SkinInfo">'+_('Skinning Informations')+'</a></li>'
        fv.res += '<li><a href="howto.rpy?type=plugin">'+_('Plugin Writing Howto')+'</a></li>'

        fv.res += '<br><br>'
        fv.printLinks(request.path.count('/')-1)
        fv.printFooter()
        fv.res+=('</ul>')
        fv.res+='</div>'
        return String( fv.res )
    
resource = HelpResource()
