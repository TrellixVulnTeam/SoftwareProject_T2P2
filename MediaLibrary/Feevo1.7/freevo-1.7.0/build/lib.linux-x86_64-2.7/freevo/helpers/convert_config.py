# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# convert_config.py - This is the Freevo helper module
# -----------------------------------------------------------------------
# $Id: convert_config.py 8442 2006-10-21 11:37:16Z duncan $
#
# Notes:
#   Run with freevo convert_config
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

import sys
import os
import re
import util

change_map = {
    'DIR_MOVIES': 'VIDEO_ITEMS',
    'DIR_AUDIO' : 'AUDIO_ITEMS',
    'DIR_IMAGES': 'IMAGE_ITEMS',
    'DIR_GAMES' : 'GAMES_ITEMS',
    'DIR_RECORD': 'TV_RECORD_DIR',
    'SUFFIX_VIDEO_FILES': 'VIDEO_SUFFIX',
    'SUFFIX_VIDEO_MPLAYER_FILES': 'VIDEO_MPLAYER_SUFFIX',
    'SUFFIX_VIDEO_XINE_FILES': 'VIDEO_XINE_SUFFIX',
    'ONLY_SCAN_DATADIR': 'VIDEO_ONLY_SCAN_DATADIR',
    'SUFFIX_AUDIO_FILES': 'AUDIO_SUFFIX',
    'SUFFIX_AUDIO_PLAYLISTS': 'PLAYLIST_SUFFIX',
    'SUFFIX_IMAGE_FILES': 'IMAGE_SUFFIX',
    'SUFFIX_IMAGE_SSHOW': 'IMAGE_SSHOW_SUFFIX',
    'MAME_CACHE': 'GAMES_MAME_CACHE',
    'OSD_SKIN': 'SKIN_MODULE',
    'FORCE_SKIN_LAYOUT': 'DIRECTORY_FORCE_SKIN_LAYOUT',
    'AUDIO_FORMAT_STRING': 'DIRECTORY_AUDIO_FORMAT_STRING',
    'USE_MEDIAID_TAG_NAMES': 'DIRECTORY_USE_MEDIAID_TAG_NAMES',
    'OVERSCAN_X': 'OSD_OVERSCAN_X',
    'OVERSCAN_Y': 'OSD_OVERSCAN_Y',
    'TV_SHOW_DATA_DIR': 'VIDEO_SHOW_DATA_DIR',
    'TV_SHOW_REGEXP': 'VIDEO_SHOW_REGEXP',
    'TV_SHOW_REGEXP_MATCH': 'VIDEO_SHOW_REGEXP_MATCH',
    'TV_SHOW_REGEXP_SPLIT': 'VIDEO_SHOW_REGEXP_SPLIT',
    'STOP_OSD_WHEN_PLAYING': 'OSD_STOP_WHEN_PLAYING',
    'TV_RECORD_SERVER_IP': 'RECORDSERVER_IP',
    'TV_RECORD_SERVER_PORT': 'RECORDSERVER_PORT',
    'RECORD_SCHEDULE': 'TV_RECORD_SCHEDULE',
    'RECORD_PADDING': 'TV_RECORD_PADDING',
    'IVTV_OPTIONS': 'TV_IVTV_OPTIONS',
    'VCR_SETTINGS': 'TV_VCR_SETTINGS',
    'WWW_SERVER_UID': 'WEBSERVER_UID',
    'WWW_SERVER_GID': 'WEBSERVER_GID',
    'WWW_PORT': 'WEBSERVER_PORT',
    'recordable=True': 'record_group=None',
    'recordable=False': 'record_group=None',
    'recordable = True': 'record_group=None',
    'recordable = False': 'record_group=None',
    }

def help():
    print 'convert local_conf.py to use the new variable names'
    print 'usage: convert_config local_conf.py [ -w ]'
    print
    print 'if -w is given the local_conf.py will be rewritten, without the option'
    print 'the script will only print the changes.'
    print
    print 'Developer may use the option -s (without local_conf) to scan for files'
    print 'which use the deleted variables'
    print
    sys.exit(0)




seperator = ' #=[]{}().:,\n'

def change(file, print_name=False):
    out = None
    try:
        cfg = open(file)
    except:
        help()

    data = cfg.readlines()
    cfg.close()

    if len(sys.argv) == 3 and sys.argv[2] == '-w':
        print 'write output file %s' % file
        out = open(file, 'w')

    change = True
    if file == 'freevo_config.py':
        change = False

    for line in data:
        if line.startswith('FREEVO_CONF_VERSION'):
            change = True

        if not change:
            if out:
                out.write(line)
            continue

        for var in change_map:
            if line.find(var) >= 0 and \
               (line.startswith(var) or line[line.find(var)-1] in seperator) and \
               line[line.find(var)+len(var)] in seperator:
                if print_name:
                    print '**** %s **** ' % file
                    print_name = False
                if out:
                    line = line.replace(var, change_map[var])
                else:
                    print 'changing config file line:'
                    print line[:-1]
                    print line[:-1].replace(var, change_map[var])
                    print
        if out:
            out.write(line)

    if out:
        out.close()




if len(sys.argv) <= 3 and sys.argv[1] == '-s':
    print 'searching for files using old style variables'
    # s = ''
    # for var in change_map:
    #     s += '|%s' % var
    # s = '(%s)' % s[1:]
    # pipe = 'xargs egrep \'%s\' | grep -v helpers/convert_config' % s
    # os.system('find . -name \*.py | %s' % pipe)
    # os.system('find . -name \*.rpy | %s' % pipe)
    # print
    # print
    # print 'starting scanning all files in detail:'
    for f in util.match_files_recursively('src', [ 'py', 'rpy' ]):
        change(f, print_name=True)
    sys.exit(0)
    
    
change(sys.argv[1])
