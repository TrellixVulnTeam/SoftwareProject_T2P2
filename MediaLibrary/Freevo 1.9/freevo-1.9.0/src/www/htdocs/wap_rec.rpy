# -*- coding: iso-8859-1 -*-
# vim:autoindent:tabstop=4:softtabstop=4:shiftwidth=4:expandtab:filetype=python:
# -----------------------------------------------------------------------
# Wap shedule recording page.
# -----------------------------------------------------------------------
# $Id: wap_rec.rpy 11501 2009-05-14 16:05:25Z duncan $
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

import sys, time

import tv.epg_xmltv
import tv.epg_types
from www.wap_types import WapResource, FreevoWapResource
from www.web_types import RecordClientResource

class WRecResource(FreevoWapResource):
    def __init__(self):
        self.recordclient = RecordClientResource()


    def _render(self, request):
        """ Render the page """
        fv = WapResource()
        form = request.args
        fv.session = request.getSession()
        fv.validate(request)
        start = fv.formValue(form, 'start')
        stop = fv.formValue(form, 'stop')
        startdate = fv.formValue(form, 'date')
        stopdate = startdate
        channel = fv.formValue(form, 'channel')
        action = fv.formValue(form, 'action')
        errormsg = ''

        if fv.session.validated <> 'yes':
            errormsg = 'not validated'

        fv.printHeader()

        # look for action to do an add
        if action:
            if action == 'add':
                starttime = time.mktime(time.strptime(str(startdate)+' '+str(start)+':00', '%d/%m/%y %H:%M:%S'))
                stoptime = time.mktime(time.strptime(str(startdate)+' '+str(stop)+':00', '%d/%m/%y %H:%M:%S'))
                if stoptime < starttime:
                    stoptime = stoptime + 86400
                prog = tv.epg_types.TvProgram()
                prog.channel_id = channel
                prog.title = "Wap Recorded"
                prog.start = starttime
                prog.stop = stoptime
                self.recordclient().scheduleRecordingNow(prog)
                fv.res += '  <card id="card3" title="Freevo">\n'
                fv.res += '   <p><strong>Rec. Sheduled</strong><br/>\n'
                fv.res += '          Date : %s<br/>\n' % startdate
                fv.res += '          Start : %s<br/>\n' % start
                fv.res += '          Stop : %s<br/>\n' % stop
                fv.res += '          Chan.: %s</p>\n' % channel
                fv.res += '  </card>\n'

        else:

            if errormsg == 'not validated':
                fv.res += '  <card id="card9" title="Freevo">\n'
                fv.res += '   <p> Please login!<br/>\n'
                fv.res += '     <anchor>Go to login\n'
                fv.res += '       <go href="wap_login.rpy"/>\n'
                fv.res += '     </anchor></p>\n'
                fv.res += '  </card>\n'
            else:
                guide = tv.epg_xmltv.get_guide()

                fv.res += '  <card id="card1" title="Freevo" ontimer="#card2">\n'
                fv.res += '  <timer value="30"/>\n'
                fv.res += '   <p><big><strong>Freevo WAP Sheduler</strong></big></p>\n'

                server_available = self.recordclient().pingNow()
                if not server_available:
                    fv.res += '<p>'+_('ERROR')+': '+self.recordclient().recordserverdown+'</p>\n'
                else:
                    fv.res += '   <p>Record Server online!</p>\n'

                fv.res += '  </card>\n'
                fv.res += '  <card id="card2" title="Freevo">\n'
                fv.res += '       <p>Date: <input  name="date" title="Date (dd/mm/yy)" format="NN/NN/NN" '+\
                    'size="6" value="%s" /><br/>\n' % time.strftime("%d/%m/%y", time.localtime(time.time()))
                fv.res += '          Start Time: <input  name="start" title="Start Time (hh:mm)" format="NN:NN" '+\
                    'size="4" value="%s" /><br/>\n' % time.strftime("%H:%M", time.localtime(time.time()))
                fv.res += '          Stop Time: <input  name="stop" title="Stop Time (hh:mm)" format="NN:NN" '+\
                    'size="4" value="%s" /><br/>\n' % time.strftime("%H:%M", time.localtime(time.time() + 3600))
                fv.res += '          Channel: <select  name="channel">\n'
                for ch in guide.chan_list:
                    fv.res += '                   <option value="'+ch.id+'">'+ch.displayname+"</option>\n"
                fv.res += '                  </select></p>\n'
                fv.res += '   <do type="accept" label="Record">\n'
                fv.res += '     <go href="wap_rec.rpy" method="post">\n'
                fv.res += '       <postfield name="action" value="add"/>\n'
                fv.res += '       <postfield name="date" value="$date"/>\n'
                fv.res += '       <postfield name="start" value="$start"/>\n'
                fv.res += '       <postfield name="stop" value="$stop"/>\n'
                fv.res += '       <postfield name="channel" value="$channel"/>\n'
                fv.res += '     </go>\n'
                fv.res += '   </do>\n'
                fv.res += '  </card>\n'

        fv.printFooter()

        return String( fv.res )

resource = WRecResource()
