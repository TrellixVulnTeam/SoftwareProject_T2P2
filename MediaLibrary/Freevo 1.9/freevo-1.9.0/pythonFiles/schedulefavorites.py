#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# A helper to run in order to schedule any favories for recording.  This
# should be ran after updating your program guide.  This step will
# eventually be handled by the recording server.
# -----------------------------------------------------------------------
# $Id: schedulefavorites.py 11499 2009-05-13 20:14:48Z duncan $
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
import kaa
from tv.record_client import RecordClient

def handler(result):
    if result:
        print _('Updated recording schedule')
    else:
        print _('Not updated recording schedule')
    raise SystemExit

rc = RecordClient()
try:
    kaa.inprogress(rc.channel).wait()
except Exception, why:
    print 'Cannot connect to record server'
    raise SystemExit

print _('Updating recording schedule')
if not rc.updateFavoritesSchedule(handler):
    print rc.recordserverdown
    raise SystemExit

kaa.main.run()
