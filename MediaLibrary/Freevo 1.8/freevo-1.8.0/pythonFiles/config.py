# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# config.py - Handle the configuration file init. Also start logging.
# -----------------------------------------------------------------------
# $Id: config.py 10547 2008-03-19 07:06:04Z duncan $
#
# Notes:
#
#   Try to find the freevo_config.py config file in the following places:
#   1) ~/.freevo/freevo_config.py       The user's private config
#   2) /etc/freevo/freevo_config.py     Systemwide config
#   3) ./freevo_config.py               Defaults from the freevo dist
#
#   Customize freevo_config.py from the freevo dist and copy it to one
#   of the other places where it will not get overwritten by new
#   checkouts/installs of freevo.
#
#   The format of freevo_config.py might change, in that case you'll
#   have to update your customized version.
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


import sys, os, time, re, string, pwd, thread
import setup_freevo
import traceback
import __builtin__
import locale
import logging

try:
    import freevo.version as version
    import freevo.revision as revision
except:
    import version
    import revision

DINFO = 0
DWARNING = -1
DERROR = -2
DCRITICAL = -3

locale.setlocale(locale.LC_TIME, '')

if sys.hexversion >= 0x02030000:
    import warnings
    warnings.simplefilter("ignore", category=FutureWarning)
    warnings.simplefilter("ignore", category=DeprecationWarning)

# For Internationalization purpose
# an exception is raised with Python 2.1 if LANG is unavailable.
import gettext
try:
    gettext.install('freevo', os.environ['FREEVO_LOCALE'], 1)
except: # unavailable, define '_' for all modules
    import __builtin__
    __builtin__.__dict__['_'] = lambda m: m


# temp solution until this is fixed to True and False
# in all freevo modules
__builtin__.__dict__['TRUE']  = 1
__builtin__.__dict__['FALSE'] = 0


# String helper function. Always use this function to detect if the
# object is a string or not. It checks against str and unicode
def __isstring__(s):
    return isinstance(s, str) or isinstance(s, unicode)

__builtin__.__dict__['isstring'] = __isstring__


class Logger:
    """
    Class to create a logger object which will send messages to stdout and log them
    into a logfile
    """
    def __init__(self, logtype='(unknown)'):
        self.lineno = 1
        self.logtype = logtype
        appname = os.path.splitext(os.path.basename(sys.argv[0]))[0]
        if not appname:
            appname = 'prompt'
        try:
            self.logfile = '%s/%s-%s.log' % (FREEVO_LOGDIR, appname, os.getuid())
            self.fp = open(self.logfile, 'a')
            logging.basicConfig(level=LOGGING, \
                #datefmt='%a, %H:%M:%S',
                format='%(asctime)s %(levelname)-8s %(message)s', \
                filename=self.logfile, filemode='a')
        except IOError, e:
            print '%s' % e
            self.logfile = '/dev/null'
            self.fp = open(self.logfile, 'a')
            logging.basicConfig(level=LOGGING, \
                format='%(asctime)s %(levelname)-8s %(message)s', \
                filename=self.logfile, filemode='a')


    def write(self, msg):
        global lock
        if lock:
            lock.acquire()
        try:
            if isinstance(msg, unicode):
                msg = msg.encode(LOCALE, 'replace')
            sys.__stdout__.write(msg)
            sys.__stdout__.flush()
            self.fp.write(msg)
            self.fp.flush()
        finally:
            if lock:
                lock.release()
        return

    def log(self, msg):
        self.fp.write('%s\n' % msg)
        self.fp.flush()
        return

    def flush(self):
        pass

    def close(self):
        pass


class VideoGroup:
    """
    @ivar vdev:
        The video recording device, such as /dev/video0.
    @ivar vvbi:
        The video vbi device, such as /dev/vbi0.
    @ivar adev:
        The audio device, such as: None, /dev/dsp.
    @ivar input_type:
        tuner, webcam
    @ivar input_num:
        The number of this input according to V4L
    @ivar tuner_type:
        internal (on a v4l device), or external (cable or sat box)
    @ivar tuner_norm:
        NTSC, PAL, SECAM
    @ivar tuner_chanlist:
        us-cable,
    @ivar tuner_chan:
        If using input_type=tuner and tuner_type=external set this to
        what channel it needs to be to get the signal, usually 3 or 4.
    @ivar irsend_trans:
        IR transmitter to use for multiple external tuners.
    @ivar record_group:
        VideoGroup that records for this tuner, default is to use the
        same device for record and play
    @ivar desc:
        A nice description for this VideoGroup.
    @ivar group_type:
        Special variable to identify devices like dvb or ivtv.  This
        can be one of: 'normal', 'ivtv', 'dvb', 'tvalsa' or 'webcam'.
    @ivar cmd:
        Command for execute external prog after the channel switched,
        such as 'sudo /usr/local/bin/setuptuner'
    """

    def __init__(self, vdev=None, vvbi='/dev/vbi', adev=None, input_type=None,
                 input_num=0, tuner_norm=None, tuner_chanlist=None,
                 tuner_type='internal', tuner_chan=None, irsend_trans=None,
                 record_group=None, desc='Freevo Default Video Group',
                 group_type='normal', cmd=None):

        (v_norm, v_input, v_clist, v_dev) = TV_SETTINGS.split()
        if vdev is None:
            vdev = v_dev
        if input_type is None:
            input_type = v_input
        if tuner_norm is None:
            tuner_norm = v_norm
        if tuner_chanlist is None:
            tuner_chanlist = v_clist

        self.vdev = vdev
        self.vvbi = vvbi
        self.adev = adev
        self.input_type = string.lower(input_type)
        self.input_num  = int(input_num)
        self.tuner_type = tuner_type
        self.tuner_norm = string.upper(tuner_norm)
        self.tuner_chanlist = tuner_chanlist
        self.tuner_chan = tuner_chan
        self.irsend_trans = irsend_trans
        self.record_group = record_group
        self.desc = desc
        self.group_type = group_type
        self.in_use = FALSE
        self.tuner = None
        self.cmd = None
        if cmd != None and isinstance(cmd, str) and cmd.strip() != '':
            self.cmd = cmd.strip()

    def __str__(self):
        s = '<%s: %s %s %s %s %s %s>' % (self.group_type, self.vdev, self.vvbi, self.adev,
            self.input_type, self.tuner_chanlist, self.tuner_chan)
        return s


    def checkvdev(self, vdev):
        """
        Check if the video device is correctly configured
        """
        from tv.v4l2 import Videodev
        try:
            dev = Videodev(vdev)
            try:
                if input_type != 'webcam':
                    try:
                        if input_type:
                            input_num = dev.getinputbyname(input_type)[0]
                    except KeyError, e:
                        print 'cannot find tuner %r for %r\npossible values are: %r' % \
                            (input_type, vdev, dev.inputs.keys())
                        sys.exit(1)
                    try:
                        if tuner_norm:
                            tuner_std = dev.getstdbyname(tuner_norm)
                    except KeyError, e:
                        print 'cannot find norm %r for %r\npossible values are: %r' % \
                            (tuner_norm, vdev, dev.standards.keys())
                        sys.exit(1)
                    print '%r:%r=%r' % (vdev, input_type, input_num)
                    print '%r:%r=%r' % (vdev, tuner_norm, tuner_std)
                else:
                    print '%r:%r=%r' % (vdev, input_type, dev.inputs.keys())
                    print '%r:%r=%r' % (vdev, tuner_norm, dev.standards.keys())
            finally:
                dev.close()
        except OSError, e:
            print 'Video device %r: %s' % (vdev, e)


def print_config_changes(conf_version, file_version, changelist):
    """
    print changes made between version on the screen
    """
    ver_old = float(file_version)
    ver_new = float(conf_version)
    if ver_old == ver_new:
        return
    print
    print 'You are using version %s, changes since then:' % file_version
    changed = [(cv, cd) for (cv, cd) in changelist if cv > ver_old]
    if not changed:
        print 'The changelist has not been updated, please notify the developers!'
    else:
        for change_ver, change_desc in changed:
            print 'Version %s:' % change_ver
            for line in change_desc.split('\n'):
                print '    ', line.strip()
            print
    print


def print_help():
    """
    print some help about config files
    """
    print 'Freevo is not completely configured to start'
    print 'The configuration is based on three files. This may sound oversized, but this'
    print 'way it\'s easier to configure.'
    print
    print 'First Freevo loads a file called \'freevo.conf\'. This file will be generated by'
    print 'calling \'freevo setup\'. Use \'freevo setup --help\' to get information'
    print 'about the parameter. Based on the information in that file, Freevo will guess'
    print 'some settings for your system. This takes place in a file called '
    print '\'freevo_config.py\'. Since this file may change from time to time, you should'
    print 'not edit this file. After freevo_config.py is loaded, Freevo will look for a file'
    print 'called \'local_conf.py\'. You can overwrite the variables from \'freevo_config.py\''
    print 'in here. There is an example for \'local_conf.py\' called \'local_conf.py.example\''
    print 'in the Freevo distribution.'
    print
    print 'If you need more help, use the internal webserver to get more information'
    print 'how to setup Freevo. To do this, you need to set'
    print 'WWW_USERS = { \'username\' : \'password\' }'
    print 'in your local_conf.py and then you can access the doc at '
    print 'http://localhost:8080/help/'
    print
    print 'The location of freevo_config.py is %s' % os.environ['FREEVO_CONFIG']
    print 'Freevo searches for freevo.conf and local_conf.py in the following locations:'
    for dirname in cfgfilepath:
        print '  '+dirname
    print



#
# get information about what is started here:
# helper = some script from src/helpers or is webserver or recordserver
#
HELPER          = 0
IS_RECORDSERVER = 0
IS_WEBSERVER    = 0
IS_ENCODINGSERVER = 0
IS_RSSSERVER = 0

__builtin__.__dict__['__freevo_app__'] = os.path.splitext(os.path.basename(sys.argv[0]))[0]

if sys.argv[0].find('main.py') == -1:
    HELPER=1
    if sys.argv[0].find('recordserver.py') != -1:
        IS_RECORDSERVER = 1
    elif sys.argv[0].find('webserver.py') != -1:
        IS_WEBSERVER = 1
    elif sys.argv[0].find('encodingserver.py') != -1:
        IS_ENCODINGSERVER = 1
    elif sys.argv[0].find('rssserver.py') != -1:
        IS_RSSSERVER = 1

#
# Send debug to stdout as well as to the logfile?
#
DEBUG_STDOUT = 1

#
# debugging messages are set by the logging level
# except for higher debugging message levels
# the DEBUG setting is overridden in local_conf.py
#
DEBUG = 0

LOGGING = logging.DEBUG


def make_freevodir(envvar, linux_dir, bsd_dir, private_dir):
    """
    Make the freevo specific directory and return it's name
    """
    if os.environ.has_key('OS_' + envvar):
        os_dirname = os.environ['OS_' + envvar]
    elif os.uname()[0] == 'FreeBSD':
        os_dirname = bsd_dir
    else:
        os_dirname = linux_dir

    if os.environ.has_key('FREEVO_' + envvar):
        freevo_dirname = os.environ['FREEVO_' + envvar]
    else:
        freevo_dirname = os.path.join(os_dirname, 'freevo')

    if not os.path.isdir(freevo_dirname):
        try:
            print 'trying "%s"...' % (freevo_dirname)
            os.makedirs(freevo_dirname)
        except OSError:
            freevo_dirname = os.path.join(os.environ['HOME'], '.freevo', private_dir)
            if not os.path.isdir(freevo_dirname):
                try:
                    print 'trying "%s"...' % (freevo_dirname)
                    os.makedirs(freevo_dirname)
                except OSError, e:
                    print 'Warning: %s does not exists and can\'t be created' % freevo_dirname
                    print 'Please create this directory as root and set permissions for the'
                    print 'Freevo user to write to it.'
                    os_dirname = '/tmp'
                    freevo_dirname = os.path.join(os_dirname, 'freevo')
                    if not os.path.isdir(freevo_dirname):
                        try:
                            print 'trying "%s"...' % (freevo_dirname)
                            os.makedirs(freevo_dirname)
                        except OSError:
                            os_dirname = '/tmp'
                            freevo_dirname = os.path.join(os_dirname, ('freevo-' + os.getuid()), private_dir)
                            if not os.path.isdir(freevo_dirname):
                                print 'trying "%s"...' % (freevo_dirname)
                                os.makedirs(freevo_dirname)
                    print 'Using %s as cache directory, but this is a bad idea' % freevo_dirname
                    print
    return (os_dirname, freevo_dirname)


#
# find the log directory
#
OS_LOGDIR, FREEVO_LOGDIR = make_freevodir('LOGDIR', '/var/log', '/var/log', 'log')

#
# Freevo static dir:
#
# Under Linux, use /var/lib. Under FreeBSD, use /var/db.
#
OS_STATICDIR, FREEVO_STATICDIR = make_freevodir('STATICDIR', '/var/lib', '/var/db', 'static')

#
# Freevo cache dir:
#
# Under Linux, use /var/cache. Under FreeBSD, use /var/db.
#
OS_CACHEDIR, FREEVO_CACHEDIR = make_freevodir('CACHEDIR', '/var/cache', '/var/db', 'cache')

#
# Redirect stdout and stderr to stdout and /tmp/freevo.log
#
#if not HELPER:
lock = thread.allocate_lock()
sys.stdout = Logger(sys.argv[0] + ':stdout')
sys.stderr = Logger(sys.argv[0] + ':stderr')
ts = time.asctime(time.localtime(time.time()))
sys.stdout.log('=' * 80)
sys.stdout.log('Freevo %s r%s started at %s' % (version.__version__, revision.__revision__, ts))
sys.stdout.log('-' * 80)

def shutdown():
    sys.stdout.log('-' * 80)
    sys.stdout.log('Freevo %s r%s finished at %s' % (version.__version__, revision.__revision__, ts))
    sys.stdout.log('=' * 80)
    sys.stdout.close()
    sys.stderr.close()
    return

def _stack_function_(message='', limit=None):
    import traceback
    stack = traceback.extract_stack()
    if stack:
        if limit:
            logging.debug('%s\n*** %s' % (message, '*** '.join(traceback.format_list(stack[-limit-1:-1]))))
        else:
            logging.debug('%s\n*** %s' % (message, '*** '.join(traceback.format_list(stack)[0:-1])))


def _debug_function_(s, level=1):
    """
    The debug function that is mapped to the _debug_ builtin There are different
    levels of debugging and logging. Debug messages range from 1 (default) to 9
    (most verbose), logging messages range from NOTSET to DCRITICAL
    """
    if DEBUG < level:
        return
    if not s:
        return
    global lock
    global DEBUG_STDOUT
    if lock:
        lock.acquire()
    try:
        try:
            # add the current trace to the string
            if isinstance(s, unicode):
                s = s.encode(encoding, 'replace')
            where =  traceback.extract_stack(limit = 2)[0]
            msg = '%s (%s): %s' % (where[0][where[0].rfind('/')+1:], where[1], s)
            # log all the messages
            if level <= DCRITICAL:
                logging.critical(msg)
            elif level == DERROR:
                logging.error(msg)
            elif level == DWARNING:
                logging.warning(msg)
            elif level == DINFO:
                logging.info(msg)
            else:
                logging.debug(msg)
            # print the message for info, warning, error and critical
            if level <= DWARNING and DEBUG_STDOUT:
                sys.__stdout__.write('%s\n' % (s))
                sys.__stdout__.flush()
        except UnicodeEncodeError:
            print "_debug_ failed. %r" % msg
        except Exception, e:
            print "_debug_ failed: %r" % e
    finally:
        if lock:
            lock.release()


__builtin__.__dict__['_debug_'] = _debug_function_
__builtin__.__dict__['_stack_'] = _stack_function_
__builtin__.__dict__['DCRITICAL'] = DCRITICAL
__builtin__.__dict__['DERROR'] = DERROR
__builtin__.__dict__['DWARNING'] = DWARNING
__builtin__.__dict__['DINFO'] = DINFO


#
# Config file handling
#
cfgfilepath = ['.', os.path.expanduser('~/.freevo'), '/etc/freevo', '/usr/local/etc/freevo']


#
# Default settings
# These will be overwritten by the contents of 'freevo.conf'
#
CONF = setup_freevo.Struct()
CONF.geometry = '800x600'
CONF.position = '0,0'
CONF.width, CONF.height = 800, 600
CONF.x, CONF.y = 0, 0
CONF.display = 'x11'
CONF.tv = 'ntsc'
CONF.chanlist = 'us-cable'
CONF.version = 0

#
# Read the environment set by the start script
#
SHARE_DIR   = os.path.abspath(os.environ['FREEVO_SHARE'])
CONTRIB_DIR = os.path.abspath(os.environ['FREEVO_CONTRIB'])

SKIN_DIR  = os.path.join(SHARE_DIR, 'skins')
ICON_DIR  = os.path.join(SHARE_DIR, 'icons')
IMAGE_DIR = os.path.join(SHARE_DIR, 'images')
FONT_DIR  = os.path.join(SHARE_DIR, 'fonts')

RUNAPP = os.environ['RUNAPP']
_debug_('RUNAPP: %s' % (RUNAPP))

_debug_('LOGDIR: %s %s' % (OS_LOGDIR, FREEVO_LOGDIR), DINFO)
_debug_('STATICDIR: %s %s' % (OS_STATICDIR, FREEVO_STATICDIR), DINFO)
_debug_('CACHEDIR: %s %s' % (OS_CACHEDIR, FREEVO_CACHEDIR), DINFO)

#
# Check that freevo_config.py is not found in the config file dirs
#
for dirname in cfgfilepath[1:]:
    freevoconf = dirname + '/freevo_config.py'
    if os.path.isfile(freevoconf):
        print (('\nERROR: freevo_config.py found in %s, please remove it ' +
                'and use local_conf.py instead!') % freevoconf)
        sys.exit(1)

#
# Search for freevo.conf:
#
for dirname in cfgfilepath:
    freevoconf = dirname + '/freevo.conf'
    _debug_('Trying freevo configuration file "%s"...' % freevoconf)
    if os.path.isfile(freevoconf):
        _debug_('Loading freevo configuration file "%s"' % freevoconf, DINFO)

        commentpat = re.compile('([^#]*)( *#.*)')
        c = open(freevoconf)
        for line in c.readlines():
            if commentpat.search(line):
                line = commentpat.search(line).groups()[0]
            line = line.strip()
            if len(line) == 0:
                continue
            vals = line.split()
            _debug_('Cfg file data: "%s"' % line, 2)
            try:
                name, val = vals[0].strip(), vals[2].strip()
            except:
                print 'Error parsing config file data "%s"' % line
                continue
            CONF.__dict__[name] = val

        c.close()
        w, h = CONF.geometry.split('x')
        x, y = CONF.position.split(',')
        CONF.width, CONF.height = int(w), int(h)
        CONF.x, CONF.w = int(x), int(y)
        break
else:
    print
    print 'Error: freevo.conf not found'
    print
    print_help()
    sys.exit(1)


#
# search missing programs at runtime
#
for program, valname, needed in setup_freevo.EXTERNAL_PROGRAMS:
    if not hasattr(CONF, valname) or not getattr(CONF, valname):
        setup_freevo.check_program(CONF, program, valname, needed, verbose=0)
    if not hasattr(CONF, valname) or not getattr(CONF, valname):
        setattr(CONF, valname, '')

#
# fall back to x11 if display is mga or fb and DISPLAY ist set
# or switch to fbdev if we have no DISPLAY and x11 or dga is used
#
if not HELPER:
    if os.environ.has_key('DISPLAY') and os.environ['DISPLAY']:
        if CONF.display in ('mga', 'fbdev'):
            print
            print 'Warning: display is set to %s, but the environment ' % CONF.display + \
                  'has DISPLAY=%s.' % os.environ['DISPLAY']
            print 'this could mess up your X display, setting display to x11.'
            print 'If you really want to do this, start \'DISPLAY="" freevo\''
            print
            CONF.display = 'x11'
    else:
        if CONF.display == 'x11':
            print
            print 'Warning: display is set to %s, but the environment ' % CONF.display + \
                  'has no DISPLAY set. Setting display to fbdev.'
            print
            CONF.display='fbdev'

elif CONF.display == 'dxr3':
    # don't use dxr3 for helpers. They don't use the osd anyway, but
    # it may mess up the dxr3 output (don't ask why).
    CONF.display='fbdev'

#
# Load freevo_config.py:
#
if os.path.isfile(os.environ['FREEVO_CONFIG']):
    _debug_('Loading cfg: %s' % os.environ['FREEVO_CONFIG'])
    execfile(os.environ['FREEVO_CONFIG'], globals(), locals())
else:
    print
    print "Error: %s: no such file" % os.environ['FREEVO_CONFIG']
    print
    sys.exit(1)


#
# Search for local_conf.py:
#
for dirname in cfgfilepath:
    overridefile = dirname + '/local_conf.py'
    _debug_('Trying local configuration file "%s"...' % overridefile)
    if os.path.isfile(overridefile):
        _debug_('Loading local configuration file "%s"' % overridefile, DINFO)
        execfile(overridefile, globals(), locals())

        try:
            CONFIG_VERSION
        except NameError:
            print
            print 'Error: your local_conf.py file has no version information'
            print 'Please check freevo_config.py for changes and set CONFIG_VERSION'
            print 'in %s to %s' % (overridefile, LOCAL_CONF_VERSION)
            print
            sys.exit(1)

        if int(str(CONFIG_VERSION).split('.')[0]) != \
           int(str(LOCAL_CONF_VERSION).split('.')[0]):
            print
            print 'Error: The version information in freevo_config.py doesn\'t'
            print 'match the version in your local_conf.py.'
            print 'Please check freevo_config.py for changes and set CONFIG_VERSION'
            print 'in %s to %s' % (overridefile, LOCAL_CONF_VERSION)
            print_config_changes(LOCAL_CONF_VERSION, CONFIG_VERSION,
                                 LOCAL_CONF_CHANGES)
            sys.exit(1)

        if int(str(CONFIG_VERSION).split('.')[1]) != \
           int(str(LOCAL_CONF_VERSION).split('.')[1]):
            print
            print 'Warning: freevo_config.py was changed, please check local_conf.py'
            print_config_changes(LOCAL_CONF_VERSION, CONFIG_VERSION,
                                 LOCAL_CONF_CHANGES)
        break

else:
    print
    print 'Error: local_conf.py not found'
    print
    print_help()
    print
    print 'Since it\'s highly unlikly you want to start Freevo without further'
    print 'configuration, Freevo will exit now.'
    sys.exit(0)


# set the umask
os.umask(UMASK)


#if not HELPER:
logging.getLogger('').setLevel(LOGGING)

#
# force fullscreen when freevo is it's own windowmanager
#
if len(sys.argv) >= 2 and sys.argv[1] == '--force-fs':
    START_FULLSCREEN_X = 1


#
# set default font
#
OSD_DEFAULT_FONTNAME = os.path.join(FONT_DIR, OSD_DEFAULT_FONTNAME)

#
# set list of video files to []
# (fill be filled from the plugins)
#
VIDEO_SUFFIX = []

for p in plugin.getall():
    if p.startswith('video'):
        try:
            for s in eval('VIDEO_%s_SUFFIX' % p[6:].upper()):
                if not s in VIDEO_SUFFIX:
                    VIDEO_SUFFIX.append(s)
        except:
            pass


#
# set data dirs
# if not set, set it to root and home dir
# if set, make all path names absolute
#
for type in ('video', 'audio', 'image', 'games'):
    n = '%s_ITEMS' % type.upper()
    x = eval(n)
    if x == None:
        x = []
        if os.environ.has_key('HOME') and os.environ['HOME']:
            x.append(('Home', os.environ['HOME']))
        x.append(('Root', '/'))
        exec('%s = x' % n)
        if not HELPER and plugin.is_active('mediamenu', type):
            print
            print 'Error: %s not set, set it to Home directory' % n
            print
        if type == 'video':
            VIDEO_ONLY_SCAN_DATADIR = True

    elif type == 'games':
        abs = []
        for d in x:
            pos = d[1].find(':')
            if pos == -1:
                abs.append((d[0], os.path.abspath(d[1]), d[2]))
            else:
                if pos > d[1].find('/'):
                    abs.append((d[0], os.path.abspath(d[1]), d[2]))
                else:
                    abs.append((d[0], d[1][0:pos+1] + os.path.abspath(d[1][pos+1:]), d[2]))
        exec ('%s = abs' % n)
    else:
        # The algorithm doesn't work for GAMES_ITEMS, so we leave it out
        abs = []
        for d in x:
            if isstring(d):
                pos = d.find(':')
                if pos == -1:
                    abs.append(os.path.abspath(d))
                else:
                    if pos > d.find('/'):
                        abs.append(os.path.abspath(d))
                    else:
                        abs.append(d[0:pos+1] + os.path.abspath(d[pos+1:]))
            else:
                pos = d[1].find(':')
                if pos == -1:
                    abs.append((d[0], os.path.abspath(d[1])))
                else:
                    if pos > d[1].find('/'):
                        abs.append((d[0], os.path.abspath(d[1])))
                    else:
                        abs.append((d[0], d[1][0:pos+1] + os.path.abspath(d[1][pos+1:])))
        exec ('%s = abs' % n)



if not TV_RECORD_DIR:
    TV_RECORD_DIR = VIDEO_ITEMS[0][1]
    if not HELPER and plugin.is_active('tv'):
        print
        print 'Error: TV_RECORD_DIR not set'
        print 'Please set TV_RECORD_DIR to the directory, where recordings should be stored'
        print 'or remove the tv plugin. Autoset variable to %s.' % TV_RECORD_DIR
        print

if not VIDEO_SHOW_DATA_DIR and not HELPER:
    print 'Error: VIDEO_SHOW_DATA_DIR not found'

#
# Autodetect the CD/DVD drives in the system if not given in local_conf.py
#
# ROM_DRIVES == None means autodetect
# ROM_DRIVES == [] means ignore ROM drives
#
if ROM_DRIVES == None:
    ROM_DRIVES = []
    if os.path.isfile('/etc/fstab'):
        re_cd        = re.compile('^(/dev/cdrom[0-9]*|/dev/[am]?cd[0-9]+[a-z]?)[ \t]+([^ \t]+)[ \t]+', re.I)
        re_cdrec     = re.compile('^(/dev/cdrecorder[0-9]*)[ \t]+([^ \t]+)[ \t]+', re.I)
        re_dvd       = re.compile('^(/dev/dvd[0-9]*)[ \t]+([^ \t]+)[ \t]+', re.I)
        re_iso       = re.compile('^([^ \t]+)[ \t]+([^ \t]+)[ \t]+(iso|cd)9660', re.I)
        re_automount = re.compile('^none[ \t]+([^ \t]+).*supermount.*dev=([^,]+).*', re.I)
        re_bymountcd = re.compile('^(/dev/[^ \t]+)[ \t]+([^ ]*cdrom[0-9]*)[ \t]+', re.I)
        re_bymountdvd= re.compile('^(/dev/[^ \t]+)[ \t]+([^ ]*dvd[0-9]*)[ \t]+', re.I)
        fd_fstab = open('/etc/fstab')
        for line in fd_fstab:
            # Match on the devices /dev/cdrom, /dev/dvd, and fstype iso9660
            match_cd        = re_cd.match(line)
            match_cdrec     = re_cdrec.match(line)
            match_dvd       = re_dvd.match(line)
            match_iso       = re_iso.match(line)
            match_automount = re_automount.match(line)
            match_bymountcd = re_bymountcd.match(line)
            match_bymountdvd= re_bymountdvd.match(line)
            mntdir = devname = ''
            if match_cd or match_bymountcd:
                m = match_cd or match_bymountcd
                mntdir = m.group(2)
                devname = m.group(1)
                dispname = 'CD-%s' % (len(ROM_DRIVES)+1)
            elif match_cdrec:
                mntdir = match_cdrec.group(2)
                devname = match_cdrec.group(1)
                dispname = 'CDREC-%s' % (len(ROM_DRIVES)+1)
            elif match_dvd or match_bymountdvd:
                m = match_dvd or match_bymountdvd
                mntdir = m.group(2)
                devname = m.group(1)
                dispname = 'DVD-%s' % (len(ROM_DRIVES)+1)
            elif match_iso:
                mntdir = match_iso.group(2)
                devname = match_iso.group(1)
                dispname = 'CD-%s' % (len(ROM_DRIVES)+1)
            elif match_automount:
                mntdir = match_automount.group(1)
                devname = match_automount.group(2)
                # Must check that the supermount device is cd or dvd
                if devname.lower().find('cd') != -1:
                    dispname = 'CD-%s' % (len(ROM_DRIVES)+1)
                elif devname.lower().find('dvd') != -1:
                    dispname = 'DVD-%s' % (len(ROM_DRIVES)+1)
                elif devname.lower().find('hd') != -1:
                    print 'Trying to autodetect type of %s' % devname
                    if os.path.exists('/proc/ide/' + re.sub(r'^(/dev/)', '', devname) + '/media'):
                        if open('/proc/ide/'+  re.sub(r'^(/dev/)', '', devname) +\
                             '/media', 'r').read().lower().find('cdrom') !=1:
                            dispname = 'CD-%s' % (len(ROM_DRIVES)+1)
                            print ("%s is a cdrom drive" %devname)
                    else:
                        print ("%s doesn't seems to be a cdrom drive" %devname)
                        mntdir = devname = dispname = ''
                else:
                    mntdir = devname = dispname = ''

            if os.uname()[0] == 'FreeBSD':
                # FreeBSD-STABLE mount point is often device name + "c",
                # strip that off
                if devname and devname[-1] == 'c':
                    devname = devname[:-1]
                # Use native FreeBSD device names
                dispname = devname[5:]

            # Weed out duplicates
            for rd_mntdir, rd_devname, rd_dispname in ROM_DRIVES:
                if os.path.realpath(rd_devname) == os.path.realpath(devname):
                    if not HELPER:
                        print (('ROM_DRIVES: Auto-detected that %s is the same ' +
                                'device as %s, skipping') % (devname, rd_devname))
                    break
            else:
                # This was not a duplicate of another device
                if mntdir and devname and dispname:
                    ROM_DRIVES += [(mntdir, devname, dispname)]
                    if not HELPER:
                        print 'ROM_DRIVES: Auto-detected and added "%s"' % (ROM_DRIVES[-1], )
        fd_fstab.close()



#
# List of objects representing removable media, e.g. CD-ROMs,
# DVDs, etc.
#
REMOVABLE_MEDIA = []

#
# Auto detect xmltv channel list
#

def sortchannels(list, key):
    # This should be more generic, but I couldn't get it
    # to sort properly without specifying the nested array
    # index for the tunerid and forcing 'int'
    for l in list:
        if len(l[key]) == 1:
            l[key].append(('0', ))
    nlist = map(lambda x, key=key: (string.split(x[key][1][0])[0], x), list)
    nlist.sort()
    return map(lambda (key, x): x, nlist)


def detect_channels():
    """
    Auto detect a list of possible channels in the xmltv file
    """
    import codecs
    try:
        import cPickle as pickle
    except ImportError:
        import pickle

    file = XMLTV_FILE

    pname = os.path.join(FREEVO_CACHEDIR, 'xmltv_channels.pickle')

    if not os.path.isfile(file):
        if not HELPER:
            print
            print 'Error: can\'t find %s' % file
            print 'Use xmltv to create this file or when you don\'t want to use the tv'
            print 'module at all, add TV_CHANNELS = [] and plugin.remove(\'tv\') to your'
            print 'local_conf.py. TVguide is deactivated now.'
            print
        return []

    elif os.path.isfile(pname) and (os.path.getmtime(pname) > os.path.getmtime(file)):
        try:
            f = open(pname, 'r')
            data = pickle.load(f)
            f.close()
            return data
        except:
            if not HELPER:
                print 'Error: unable to read cachefile %s' % pname
            return []

    else:
        from tv import xmltv
        input = open(file, 'r')
        tmp   = open('/tmp/xmltv_parser', 'w')
        while(1):
            line =input.readline()
            if not line:
                break
            if line.find('<programme') > 0:
                tmp.write('</tv>\n')
                break
            tmp.write(line)

        input.close()
        tmp.close()

        tmp   = open('/tmp/xmltv_parser', 'r')
        xmltv_channels = xmltv.read_channels(tmp)
        tmp.close()

        xmltv_channels = sortchannels(xmltv_channels, 'display-name')
        chanlist = []

        for a in xmltv_channels:
            if (a['display-name'][1][0][0].isdigit()):
                display_name = a['display-name'][0][0].encode(LOCALE, 'ignore')
                tunerid = string.split(a['display-name'][1][0].encode(LOCALE, 'ignore'))[0]
            else:
                display_name = a['display-name'][1][0].encode(LOCALE, 'ignore')
                tunerid = string.split(a['display-name'][0][0].encode(LOCALE, 'ignore'))[0]
            id = a['id'].encode(LOCALE, 'ignore')

            chanlist += [(id, display_name, tunerid)]

        f = TV_CHANNELS_COMPARE
        chanlist.sort(f)

        try:
            if os.path.isfile(pname):
                os.unlink(pname)
            f = open(pname, 'w')
            pickle.dump(chanlist, f, 1)
            f.close()
        except IOError:
            if not HELPER:
                print 'Error: unable to save to cachefile %s' % pname

        for c in chanlist:
            if c[2] == 0:
                print_list = 1
                if not HELPER:
                    print
                    print 'Error: XMLTV auto detection failed'
                    print 'Some channels in the channel list have no station id. Please add'
                    print 'it by putting the list in your local_conf.py. Start '
                    print '\'freevo tv_grab --help\' for more information'
                    print
                break
        else:
            if not HELPER:
                print 'XMTV: Auto-detected channel list'

        return chanlist


if TV_CHANNELS == None and plugin.is_active('tv'):
    # auto detect them
    try:
        TV_CHANNELS = detect_channels()
    except Exception, e:
        print
        print 'Error in TV.xml file, unable to set TV_CHANNELS'
        print e
        print
        TV_CHANNELS = []

#
# compile the regexp
#
VIDEO_SHOW_REGEXP_MATCH = re.compile("^.*" + VIDEO_SHOW_REGEXP).match
VIDEO_SHOW_REGEXP_SPLIT = re.compile("[\.\- ]*" + VIDEO_SHOW_REGEXP + "[\.\- ]*").split


#
# create cache subdirs
#
if not OVERLAY_DIR or OVERLAY_DIR == '/':
    print
    print 'ERROR: bad OVERLAY_DIR.'
    print 'Set OVERLAY_DIR it to a directory on the local filesystem where Freevo'
    print 'can store the metadata. Make sure this filesystem has about 100 MB free space'
    sys.exit(0)

if not os.path.isdir(OVERLAY_DIR):
    os.makedirs(OVERLAY_DIR)

# Make sure OVERLAY_DIR doesn't ends with a slash
# With that, we don't need to use os.path.join, normal string
# concat is much faster
if OVERLAY_DIR and OVERLAY_DIR.endswith('/'):
    OVERLAY_DIR = OVERLAY_DIR[:-1]
_debug_('overlaydir: %s' % (OVERLAY_DIR), DINFO)

if not os.path.isdir(OVERLAY_DIR + '/disc'):
    os.makedirs(OVERLAY_DIR + '/disc')

if not os.path.isdir(OVERLAY_DIR + '/disc/metadata'):
    os.makedirs(OVERLAY_DIR + '/disc/metadata')

if not os.path.isdir(OVERLAY_DIR + '/disc-set'):
    os.makedirs(OVERLAY_DIR + '/disc-set')


#
# delete LD_PRELOAD for all helpers, main.py does it after
# starting the display
#
if HELPER:
    os.environ['LD_PRELOAD'] = ''

encoding = None
try:
    encoding = os.environ['LANG'].split('.')[1]
    ''.encode(encoding)
except:
    try:
        encoding = os.environ['LC_ALL'].split('.')[1]
        ''.encode(encoding)
    except:
        encoding = LOCALE

if not encoding:
    encoding = LOCALE

if not HELPER:
    _debug_("Using '%s' encoding" % encoding)

for k, v in CONF.__dict__.items():
    _debug_('%r: %r' % (k, v))

# make sure USER and HOME are set
os.environ['USER'] = pwd.getpwuid(os.getuid())[0]
os.environ['HOME'] = pwd.getpwuid(os.getuid())[5]
