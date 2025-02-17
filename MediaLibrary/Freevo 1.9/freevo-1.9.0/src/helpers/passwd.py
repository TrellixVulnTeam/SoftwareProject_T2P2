# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# Classes useful for the web interface.
# -----------------------------------------------------------------------
# $Id: passwd.py 11273 2009-01-31 08:41:03Z duncan $
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

import base64
import crypt
import string
import os
import sys

username = raw_input('Username: ')
try:
    os.system("stty -echo")
    password1 = raw_input('Password: ')
    password2 = raw_input('\nRetype Password: ')
    os.system("stty echo")
except KeyboardInterrupt, SystemExit:
    print
    os.system("stty echo")
    sys.exit(0)

if password1 != password2:
    print "\nPasswords don't match; try again."
    sys.exit(1)

salt_chars = string.letters + string.digits + '/.'
salt = [ salt_chars[ord(x) % len(salt_chars)] for x in os.urandom(8) ]
cryptpass = crypt.crypt(password1, '$1$%s$' % "".join(salt))
print "\n\nAdd this line to WWW_USERS in local_conf.py:"
print "'%s' : '%s'" % (username, cryptpass)
