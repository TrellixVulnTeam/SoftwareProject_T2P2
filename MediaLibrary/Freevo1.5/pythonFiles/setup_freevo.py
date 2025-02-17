# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# setup_freevo.py - Autoconfigure Freevo
#
# This is an application that is executed by the "./freevo" script
# after checking for python.
# -----------------------------------------------------------------------
# $Id: setup_freevo.py,v 1.18 2004/07/10 12:33:36 dischi Exp $
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log: setup_freevo.py,v $
# Revision 1.18  2004/07/10 12:33:36  dischi
# header cleanup
#
# Revision 1.17  2004/07/08 12:44:40  rshortt
# Add directfb as a display option.
#
# Revision 1.16  2004/04/20 17:33:59  dischi
# lsdvd check
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


import sys
import os
import getopt
import string

CONFIG_VERSION = 2.1

# For Internationalization purpose
# an exception is raised with Python 2.1 if LANG is unavailable.
import gettext
try:
    gettext.install('freevo', os.environ['FREEVO_LOCALE'])
except: # unavailable, define '_' for all modules
    import __builtin__
    __builtin__.__dict__['_']= lambda m: m


EXTERNAL_PROGRAMS = (("mplayer", "mplayer", 1),
                     ("mencoder", "mencoder", 0),
                     ("tvtime", "tvtime", 0),
                     ("xine", "xine", 0),
                     ("fbxine", "fbxine", 0),
                     ("lsdvd", "lsdvd", 0),
                     ("jpegtran", "jpegtran", 0),
                     ("xmame.x11", "xmame", 0),
                     ("xmame.SDL", "xmame", 0),
                     ("xmame","xmame",0),
                     ("ssnes9x", "snes", 0),
                     ("zsnes", "snes", 0 ),
                     ("lame", "lame",0),
                     ("flac","flac",0),
                     ("cdparanoia","cdparanoia",0),
                     ("oggenc","oggenc",0),
                     ("renice","renice",0),
                     ("setterm", "setterm", 0),
                     ("mpav", "mpav", 0))

# Help text
def print_usage():
    usage = _('''\
Usage: ./freevo setup [OPTION]...
Set up Freevo for your specific environment.

   --geometry=WIDTHxHEIGHT      set the display size
                                  WIDTHxHEIGHT can be 800x600, 768x576 or 640x480

   --display=DISP               set the display
                                  DISP can be x11, fbdev, dxr3, mga, 
                                  directfb, dfbmga or dga
                                  
   --tv=NORM                    set the TV standard
                                  NORM can be ntsc, pal or secam

   --chanlist=LIST              set the channel list
                                  LIST can be us-bcast, us-cable, us-cable-hrc,
                                  japan-bcast, japan-cable, europe-west,
                                  europe-east, italy, newzealand, australia,
                                  ireland, france, china-bcast, southafrica,
                                  argentina, canada-cable

   --help                       display this help and exit

The default is "--geometry=800x600 --display=x11 --tv=ntsc --chanlist=us-cable"
Please report bugs to <freevo-users@lists.sourceforge.net>.
''')

    print usage
    
    
class Struct:
    pass



def match_files_recursively_helper(result, dirname, names):
    if dirname == '.' or dirname[:5].upper() == './WIP':
        return result
    for name in names:
        if os.path.splitext(name)[1].lower()[1:] == 'py':
            fullpath = os.path.join(dirname, name)
            result.append(fullpath)
    return result


def check_config(conf):
    vals_geometry = ['800x600', '768x576', '640x480']
    vals_display = ['x11', 'fbdev', 'directfb', 'dfbmga', 'mga', 'dxr3', 'dga']
    vals_tv = ['ntsc', 'pal', 'secam']
    vals_chanlist = ['us-bcast', 'us-cable', 'us-cable-hrc',
                     'japan-bcast', 'japan-cable', 'europe-west',
                     'europe-east', 'italy', 'newzealand', 'australia',
                     'ireland', 'france', 'china-bcast', 'southafrica',
                     'argentina', 'canada-cable']

    if not conf.geometry in vals_geometry:
        print 'geometry must be one of: %s' % ' '.join(vals_geometry)
        sys.exit(1)
        
    if not conf.display in vals_display:
        print 'display must be one of: %s' % ' '.join(vals_display)
        sys.exit(1)
        
    if not conf.tv in vals_tv:
        print 'tv must be one of: %s' % ' '.join(vals_tv)
        sys.exit(1)
        
    if not conf.chanlist in vals_chanlist:
        print 'chanlist must be one of: %s' % ' '.join(vals_chanlist)
        sys.exit(1)
        

def create_config(conf):
    
    outfile='/etc/freevo/freevo.conf'
    try:
        fd = open(outfile, 'w')
    except:
        if not os.path.isdir(os.path.expanduser('~/.freevo')):
            os.mkdir(os.path.expanduser('~/.freevo'))
        outfile=os.path.expanduser('~/.freevo/freevo.conf')
        fd = open(outfile, 'w')
        
    for val in dir(conf):
        if val[0:2] == '__': continue

        # Some Python magic to get all members of the struct
        fd.write('%s = %s\n' % (val, conf.__dict__[val]))
        
    print
    print 'wrote %s' % outfile


def check_program(conf, name, variable, necessary, sysfirst=1, verbose=1):

    # Check for programs both in the path and the runtime apps dir
    search_dirs_runtime = ['./runtime/apps', './runtime/apps/mplayer',
                           './runtime/apps/tvtime']
    if sysfirst:
        search_dirs = os.environ['PATH'].split(':') + search_dirs_runtime
    else:
        search_dirs = search_dirs_runtime + os.environ['PATH'].split(':')
        
    if verbose:
        print _('checking for %-13s') % (name+'...'),

    for dirname in search_dirs:
        filename = os.path.join(dirname, name)
        if os.path.exists(filename) and os.path.isfile(filename):
            if verbose:
                print filename
            conf.__dict__[variable] = filename
            break
    else:
        if necessary:
            print
            print "********************************************************************"
            print _('ERROR: can\'t find %s') % name
            print _('Please install the application respectively put it in your path.')
            print _('Freevo won\'t work without it.')
            print "********************************************************************"
            print
            print
            sys.exit(1)
        elif verbose:
            print _('not found (deactivated)')




if __name__ == '__main__':
    # Default opts

    # XXX Make this OO and also use the Optik lib
    conf = Struct()
    conf.geometry = '800x600'
    conf.display = 'x11'
    conf.tv = 'ntsc'
    conf.chanlist = 'us-cable'
    conf.version = CONFIG_VERSION
    sysfirst = 0 # Check the system path for apps first, then the runtime
    
    # Parse commandline options
    try:
        long_opts = 'help compile= geometry= display= tv= chanlist= sysfirst'.split()
        opts, args = getopt.getopt(sys.argv[1:], 'h', long_opts)
    except getopt.GetoptError:
        # print help information and exit:
        print_usage()
        sys.exit(2)

    for o, a in opts:
        if o in ("-h", "--help"):
            print_usage()
            sys.exit()
            
        if o == '--geometry':
            conf.geometry = a

        if o == '--display':
            conf.display = a

        if o == '--tv':
            conf.tv = a

        if o == '--chanlist':
            conf.chanlist = a

        if o == '--sysfirst':
            sysfirst = 1

        # this is called by the Makefile, don't call it directly
        if o == '--compile':
            # Compile python files:
            import distutils.util
            try:
                optimize=min(int(a[0]),2)
                prefix=a[2:]
            except:
                sys.exit(1)

            files = []
            os.path.walk('.', match_files_recursively_helper, files)
            distutils.util.byte_compile(files, prefix='.', base_dir=prefix,
                                        optimize=optimize)
            sys.exit(0)


    print _('System path first=%s') % ( [_('No'), _('Yes')][sysfirst])

    for program, valname, needed in EXTERNAL_PROGRAMS:
        check_program(conf, program, valname, needed, sysfirst)

    check_config(conf)

    # set geometry for display/tv combinations without a choice
    if conf.display in ( 'directfb', 'dfbmga' ):
        if conf.tv == 'ntsc':
            conf.geometry = '720x480'
        else:
            conf.geometry = '720x576'

    print
    print
    print _('Settings:')
    print '  %20s = %s' % ('geometry', conf.geometry)
    print '  %20s = %s' % ('display', conf.display)
    print '  %20s = %s' % ('tv', conf.tv)
    print '  %20s = %s' % ('chanlist', conf.chanlist)


    # Build everything
    create_config(conf)
    print
    
    sys.exit()
