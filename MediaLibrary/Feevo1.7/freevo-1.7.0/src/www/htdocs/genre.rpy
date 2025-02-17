#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# genre.rpy - Show what is on for today for a particular category
# -----------------------------------------------------------------------
# $Id: genre.rpy 9032 2007-01-21 13:37:55Z duncan $
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

import sys, time, string

import tv.record_client as ri
from www.web_types import HTMLResource, FreevoResource
import tv.epg_xmltv
import util, config

TRUE = 1
FALSE = 0

class GenreResource(FreevoResource):

# need sub to get list of possible categories

    def makecategorybox(self, categories, category):
        retval = u'<select name="category">\n'
        category = Unicode( category )
        for cat in categories:
            cat = Unicode( cat )
            retval += u'<option value="%s" ' % cat
            if cat == category:
                retval += u'selected="selected"'
            retval += u'>%s</option>\n' % cat
        retval += u'</select>\n'
        return retval

    def _render(self, request):
        fv = HTMLResource()
        form = request.args

        mfrguidestart = time.time()
        mfrguideinput = fv.formValue(form, 'stime')
        if mfrguideinput:
            mfrguidestart = int(mfrguideinput)
        # a little before midnight the day of mfrguidestart
        myt_t=time.localtime(mfrguidestart)
        mfrnextguide=time.mktime((myt_t[0], myt_t[1], myt_t[2], 23, 59, 5, myt_t[6], myt_t[7], -1))
        # a little after midnight the day before mfrguidestart
        mfrprevguide=time.mktime((myt_t[0], myt_t[1], myt_t[2]-1, 0, 0, 5, myt_t[6], myt_t[7], -1))
        # kill mfrprevguide to zero if it is less than now
        if mfrprevguide < time.time():
            now_t = time.localtime(time.time())
            newmyt2 = myt_t[2]-1
            if (myt_t[0] == now_t[0] and myt_t[1] == now_t[1] and newmyt2 == now_t[2]):
                mfrprevguide = time.time()
            else:
                mfrprevguide = 0

        category = fv.formValue(form, 'category')

        guide = tv.epg_xmltv.get_guide()
        (got_schedule, schedule) = ri.getScheduledRecordings()
        if got_schedule:
            schedule = schedule.getProgramList()

        fv.printHeader(_('TV Genre for %s') % time.strftime('%a %b %d', time.localtime(mfrguidestart)), \
            config.WWW_STYLESHEET, config.WWW_JAVASCRIPT)

        if not got_schedule:
            fv.printMessages(['<b>'+_('ERROR')+'</b>: '+_('Recording server is unavailable.')])

        allcategories = []
        for chan in guide.chan_list:
            for prog in chan.programs:
                if prog.categories:
                    allcategories.extend(prog.categories)
        if allcategories:
            allcategories=util.unique(allcategories)
            allcategories.sort()

        stime=''
        if mfrguideinput:
            stime='<input name="stime" type="hidden" value="%i"/>' % int(mfrguideinput)
        keepcat = ''
        if category:
            keepcat = '&amp;category=%s' % category
        bforcell=''
        acelltime=mfrnextguide + 60
        aftercell=('&nbsp;&nbsp;&nbsp;<a href="genre.rpy?stime=%i%s">'
                   +'<img src="images/RightArrow.png" alt="right" border="0"/></a>') \
                   % (acelltime, keepcat)
        if mfrprevguide > 0:
            bforcell=('<a href="genre.rpy?stime=%i%s">'
                      +'<img src="images/LeftArrow.png" alt="left" border="0"/></a>&nbsp;&nbsp;&nbsp;') \
                      % (mfrprevguide, keepcat)
        
        fv.tableOpen('border="0" cellpadding="4" cellspacing="1" width="100%"')
        fv.tableRowOpen('class="chanrow"')
        fv.tableCell('<form action="">'+bforcell+_('Show')+'&nbsp;'+_('Category')+':&nbsp;'\
            +self.makecategorybox(allcategories, category)+stime+'<input type="submit" value="'+_('Change')+'"/>'\
            +aftercell+'</form>', 'class="guidehead"')
        fv.tableRowClose()
        fv.tableClose()

        if not category:
            fv.printSearchForm()
            fv.printLinks()
            fv.printFooter()
            return String( fv.res )

        fv.tableOpen('border="0" cellpadding="4" cellspacing="1" width="100%"')
        fv.tableRowOpen('class="chanrow"')
        fv.tableCell('Channel', 'class="guidehead"')
        fv.tableCell('Program', 'class="guidehead"')
        fv.tableCell('Start', 'class="guidehead"')
        fv.tableCell('Stop', 'class="guidehead"')
        fv.tableRowClose()

        desc = ''
        gotdata = 0
        for chan in guide.chan_list:
            for prog in chan.programs:
                if prog.stop > mfrguidestart and prog.start < mfrnextguide:
                    status = 'program'

                    # match the category
                    if category in prog.categories:
                        print 'found it'
                    else:
                        continue

                    # figure out if in progress

                    # use counter to see if we have data
                    gotdata += 1
                    if got_schedule:
                        (result, message) = ri.isProgScheduled(prog, schedule)
                        if result:
                            status = 'scheduled'
                            really_now = time.time()
                            if prog.start <= really_now and prog.stop >= really_now:
                                # in the future we should REALLY see if it is
                                # recording instead of just guessing
                                status = 'recording'

                    fv.tableRowOpen('class="chanrow"')
                    fv.tableCell(chan.displayname, 'class="channel"')
                    popid = '%s:%s' % (prog.channel_id, prog.start)
                        
                    fv.tableCell(prog.title+'&nbsp;&nbsp;-&nbsp;&nbsp;'+prog.desc, 'class="'+status+'" \
                        onclick="guide_click(this, event)" id="%s"  width="80%%"' % popid )
                    fv.tableCell(time.strftime('%H:%M', time.localtime(prog.start)), 'class="channel"')
                    fv.tableCell(time.strftime('%H:%M', time.localtime(prog.stop)), 'class="channel"')
                    fv.tableRowClose()

        if gotdata == 0:
            fv.tableRowOpen('class="chanrow"')
            fv.tableCell('<center>'+_('NO SHOWS MATCHING CATEGORY')+'</center>', 'class="utilhead" colspan="4"')
            fv.tableRowClose()
        fv.tableClose()

        fv.printSearchForm()
        fv.printLinks()
        fv.res += (
            u"<div id=\"popup\" class=\"proginfo\" style=\"display:none\">\n"\
            u"<div id=\"program-waiting\" style=\"background-color: #0B1C52; position: absolute\">\n"\
            u"  <br /><b>Fetching program information ...</b>\n"\
            u"</div>\n"\
            u"   <table id=\"program-info\" class=\"popup\">\n"\
            u"      <thead>\n"\
            u"         <tr>\n"\
            u"            <td id=\"program-title\">\n"\
            u"            </td>\n"\
            u"         </tr>\n"\
            u"      </thead>\n"\
            u"      <tbody>\n"\
            u"         <tr>\n"\
            u"            <td class=\"progdesc\" id=\"program-desc\">\n"\
            u"            </td>\n"\
            u"         </tr>\n"\
            u"         <tr>\n"\
            u"            <td class=\"progtime\">\n"\
            u"               <b>"+_('Start')+u":</b> <span id=\"program-start\"></span>, \n"\
            u"               <b>"+_('Stop')+u":</b> <span id=\"program-end\"></span>, \n"\
            u"               <b>"+_('Runtime')+u":</b> <span id=\"program-runtime\"></span> min\n"\
            u"            </td>\n"\
            u"         </tr>\n"\
            u"      </tbody>\n"\
            u"      <tfoot>\n"\
            u"         <tr>\n"\
            u"            <td>\n"\
            u"               <table class=\"popupbuttons\">\n"\
            u"                  <tbody>\n"\
            u"                     <tr>\n"\
            u"                        <td id=\"program-record-button\">\n"\
            u"                           "+_('Record')+u"\n"\
            u"                        </td>\n"\
            u"                        <td id=\"program-favorites-button\">\n"\
            u"                        "+_('Add to Favorites')+u"\n"\
            u"                        </td>\n"\
            u"                        <td onclick=\"program_popup_close();\">\n"\
            u"                        "+_('Close Window')+u"\n"\
            u"                        </td>\n"\
            u"                     </tr>\n"\
            u"                  </tbody>\n"\
            u"               </table>\n"\
            u"            </td>\n"\
            u"         </tr>\n"\
            u"      </tfoot>\n"\
            u"   </table>\n"\
            u"</div>\n" )
        fv.res += "<iframe id='hidden' style='visibility: hidden; width: 1px; height: 1px'></iframe>\n"
        fv.printFooter()

        return String( fv.res )


resource = GenreResource()
