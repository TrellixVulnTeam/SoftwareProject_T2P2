#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# proginfo.rpy - Dynamically update program info popup box.
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

import sys, string
import time

from www.web_types import HTMLResource, FreevoResource
from twisted.web.woven import page

import util.tv_util as tv_util
import util
import config
import tv.epg_xmltv
import tv.record_client as ri
from twisted.web import static

MAX_DESCRIPTION_CHAR = 1000

class ProgInfoResource(FreevoResource):

    def _render(self, request):
        fv = HTMLResource()
        form = request.args
        id = fv.formValue(form, 'id')
        chanid = id[:id.find(":")]
        starttime = int( id[id.find(":")+1:] )

        guide = tv.epg_xmltv.get_guide()

        chan = guide.chan_dict[chanid]
        for prog in chan.programs:
            if prog.start == starttime:
                break

        title = prog.title

        if prog.desc == '':
            desc = (_('Sorry, the program description for %s is unavailable.')) \
                % ('<b>'+prog.title+'</b>')
        else:
            desc = prog.desc

        desc = desc.lstrip()
        if MAX_DESCRIPTION_CHAR and len(desc) > MAX_DESCRIPTION_CHAR:
            desc=desc[:desc[:MAX_DESCRIPTION_CHAR].rfind('.')] + '. [...]'

        if prog.sub_title:
            desc = '"%s"<br/>%s' % (prog.sub_title,desc)
        desc = desc.replace("\n", "<br/>")

        #print 'type(title)=%s, title=%r' % (type(title), title)
        #print "type(desc)=%s, desc=%r" % (type(desc), desc)

        #if config.LOCALE.lower() != 'utf8' and config.LOCALE.lower() != 'utf-8':
        #    title = title.encode('ascii', 'ignore')
        #    desc = desc.encode('ascii', 'ignore')
        start = time.strftime(config.TV_TIMEFORMAT, time.localtime(prog.start))
        stop = time.strftime(config.TV_TIMEFORMAT, time.localtime(prog.stop))
        fv.res += u"<script>\n"
        fv.res += u"var doc = parent.top.document;\n"
        fv.res += u"doc.getElementById('program-title').innerHTML = '"+Unicode(title).replace("'", "\\'")+"';\n"
        fv.res += u"doc.getElementById('program-desc').innerHTML = '"+Unicode(desc).replace("'", "\\'")+"';\n"
        fv.res += u"doc.getElementById('program-start').innerHTML = '"+start+"';\n"
        fv.res += u"doc.getElementById('program-end').innerHTML = '"+stop+"';\n"
        fv.res += u"doc.getElementById('program-runtime').innerHTML = '%s';\n" % int((prog.stop - prog.start) / 60)
        fv.res += u"doc.getElementById('program-record-button').onclick = %s;\n" % \
            "function() { doc.location=\"record.rpy?chan=%s&start=%s&action=add\"; }" % (chanid, starttime)
        fv.res += u"doc.getElementById('program-favorites-button').onclick = %s;\n" % \
            "function() { doc.location=\"edit_favorite.rpy?chan=%s&start=%s&action=add\"; }" % (chanid, starttime)
        fv.res += u"doc.getElementById('program-waiting').style.display = 'none';\n"
        fv.res += u"doc.getElementById('program-info').style.visibility = 'visible';\n"
        fv.res += u"</script>\n"

        return String(fv.res)


resource = ProgInfoResource()
