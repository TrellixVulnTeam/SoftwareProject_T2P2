# -----------------------------------------------------------------------
# local_conf.py - System configuration
# -----------------------------------------------------------------------
# $Id: local_conf.py 9266 2007-02-24 13:53:49Z duncan $
#
# Notes:
#    This file contains the freevo settings. To change the settings
#    you can edit this file, or better, put a file named local_conf.py
#    # in the same directory and add your changes there.  E.g.: when
#    you # want a alsa as mplayer audio out, just put
#    "MPLAYER_AO_DEV = # 'alsa9'" in local_conf.py
#
#    This is no normal config file, it's Python code. Because of that, you 
#    need to follow some rules to avoid crashes. The examples should explain
#    the settings, but make sure a line starting with a variable has 
#    NO SPACES OR TABS at the beginning.
#
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




CONFIG_VERSION = 5.17

# ======================================================================
# General freevo settings:
# ======================================================================

AUDIO_DEVICE       = '/dev/alsa'       # e.g.: /dev/dsp0, /dev/audio, /dev/alsa/?
# AUDIO_INPUT_DEVICE = '/dev/dsp1'     # e.g.: /dev/dsp0, /dev/audio, /dev/alsa/
MAJOR_AUDIO_CTRL   = 'PCM'             # Freevo takes control over one audio ctrl
                                       # 'VOL', 'PCM' 'OGAIN' etc.
CONTROL_ALL_AUDIO  = 1                 # Should Freevo take complete control of audio
MAX_VOLUME         = 100               # Set what you want maximum volume level to be.
DEFAULT_VOLUME     = 80                # Set default volume level.
# TV_IN_VOLUME       = 60              # Set this to your preferred level 0-100.
# VCR_IN_VOLUME      = 90              # If you use different input from TV
# RADIO_IN_VOLUME    = 80              # Set this to your preferred level 0-100.
# DEV_MIXER          = '/dev/mixer'    # mixer device 

# START_FULLSCREEN_X = 0               # Start in fullscreen mode if using x11 or xv.

CONFIRM_SHUTDOWN   = 0                 # ask before shutdown

#
# Physical ROM drives, multiple ones can be specified
# by adding comma-seperated and quoted entries.
#
# Format [ ('mountdir1', 'devicename1', 'displayed name1'),
#          ('mountdir2', 'devicename2', 'displayed name2'), ...]
#
# Set to None to autodetect drives in during startup from /etc/fstab,
# set to [] to disable rom drive support at all
#
# ROM_DRIVES = None
ROM_DRIVES = [ ('/media/','/dev/cdrom','DVD') ]
plugin.remove('video.xine')


#
# Hide discs from the wrong menu (e.g. VCDs in audio menu) and empty discs.
#
HIDE_UNUSABLE_DISCS = 1               

#
# Attempt to set the speed of the ROM drive. A good value for keeping the
# drive silent while playing movies is 8.
#
# ROM_SPEED = 0                

#
# Perform a whole system shutdown at SHUTDOWN! Useful for standalone boxes.
#
# ENABLE_SHUTDOWN_SYS = 0
#
# Command to execute to shutdown the system
#
# SHUTDOWN_SYS_CMD = "sudo shutdown -h now"
# RESTART_SYS_CMD = "sudo shutdown -r now"

# ======================================================================
# AUTOSHUTDOWN CONFIGURATION
# ======================================================================

# replace the default shutdown plugin
#plugin.remove('shutdown')
#plugin.activate('autoshutdown', level=90)

# activate the timer
#plugin.activate('autoshutdown.autoshutdowntimer')


# -- autoshutdown menu item configuration --

# CONFIRM_SHUTDOWN
# Set to True to popup dialog boxes for confirmation.
# this applies to menu items only.
#AUTOSHUTDOWN_CONFIRM = True


# -- autoshutdown timer configuration --

# TIMER_TIMEOUT
# Set the timeout in minutes after which the system
# is shutdown. The allowed idle time and the running
# processes (see below) are evaluated to determine if
# a shutdown is allowed. Menu navigation in freevo will
# reset the timer.
#AUTOSHUTDOWN_TIMER_TIMEOUT=30


# -- autoshutdown behaviour configuration --

# PRETEND
# Set to True to disable the actual shutdown command.
#AUTOSHUTDOWN_PRETEND = False

# PROCESS_LIST
# List the processes that will prevent an automatic
# shutdown. If there are important programs that
# should not be interrupted, then add them to this
# list. Set to None if a shutdown is always allowed.
#AUTOSHUTDOWN_PROCESS_LIST = [
#    'emerge',
#    'tvgids',
#    'transcode',
#    'cdrecord',
#    'mplayer',
#    'top'
#]

# DEFAULT_WAKEUP_TIME
# Set the default time at which to wakeup if there
# are no recordings scheduled. The time is specified
# in localtime 24 hour format. Set to None to disable
# default wakeup time.
#AUTOSHUTDOWN_DEFAULT_WAKEUP_TIME = "13:00"

# FORCE_DEFAULT_WAKEUP
# Set to True to always wakeup at the default wakeup
# time. Set to False to only wakeup at the default
# wakeup time when no recordings are scheduled.
#AUTOSHUTDOWN_FORCE_DEFAULT_WAKEUP = True

# ALLOWED_IDLE_TIME
# The number of minutes that may be spent idle until
# the next scheduled recording or default wakeup. That
# is, if the gap between "now" and the next recording
# or default wakeup is less than the allowed idle time
# then a shutdown is not performed but the system is
# left running. If the period from now to the next
# recording or default wakeup is more than the allowed
# idle time, then the system is shut down and a wakeup
# is scheduled. Use this to minimize the number of
# shutdown/boot sequences when many short programs are
# recorded in a short period of time. Note that this
# variable is used by both the timer and the menu.
#AUTOSHUTDOWN_ALLOWED_IDLE_TIME = 45

# -- Choice of wakeup method
#
# The wakeup can be done via acpi-alarm or nvram-wakeup.
#AUTOSHUTDOWN_METHOD = 'acpi'
#AUTOSHUTDOWN_METHOD = 'nvram'

# -- autoshutdown acpi-alarm configuration

# This method uses the wakeup on alarm function that most BIOSs have.
# The wakeup time is set by a simple 
#
# "echo 2004-08-02 20:15:00 >/proc/acpi/alarm"
#
# On most mainbords you will have to ENABLE "Wake on Timer", "Resume on Alarm", 
# "RTC Alarm Resume" or similar things for the acpi wakeup method to work.
# If you want to use acpi, you need to create a small script:
#
#    !/bin/sh
#    echo "$1" >/proc/acpi/alarm   
#    
# You have to be root or use sudo for this to work.    
#AUTOSHUTDOWN_WAKEUP_CMD = sudo /PATH/TO/set_acpi.sh    


# -- autoshutdown nvram-wakeup configuration --

# The nvram-wakeup utility is used to write the
# wakeup alarm to the RTC in bios. Read the
# nvram-wakeup documentation about this topic,
# a working nvram-wakeup configuration is needed.

# WAKEUP_CMD / NVRAM_OPT
# Path to nvram-wakeup and options. Options can
# be used to specify a config file.
#AUTOSHUTDOWN_WAKEUP_CMD = "/usr/bin/nvram-wakeup"
#AUTOSHUTDOWN_NVRAM_OPT = "--syslog"

# WAKEUP_NEEDS_REBOOT
# Set to True if the bios needs a reboot to catch
# up with the rtc alarm that nvram-wakeup sets. The
# boot loader options should be set too. Read the
# nvram-wakeup documentation about this topic.
#AUTOSHUTDOWN_BIOS_NEEDS_REBOOT = True

# -- if the bios needs a reboot --

# BOOT_LOADER
# Set to "GRUB" or "LILO" Only needed if bios needs
# a reboot to initialize the RTC wakeup call.
#AUTOSHUTDOWN_BOOT_LOADER = "GRUB"

# REMOUNT_BOOT_CMD / REMOUNT_BOOT_OPT
# Grub needs to write to /boot/grub/grub.conf. Set
# the command and options to remount the /boot
# partition writeable. Set to None if this is not
# needed.
#AUTOSHUTDOWN_REMOUNT_BOOT_CMD = "/bin/mount"
#AUTOSHUTDOWN_REMOUNT_BOOT_OPT = "/boot -o remount,rw"

# GRUB_CMD / GRUB_OPT
# Grub-set-default command and options that will
# reboot and poweroff the system.
#AUTOSHUTDOWN_GRUB_CMD = "/sbin/grub-set-default 0"
#AUTOSHUTDOWN_GRUB_OPT = "0"

# LILO_CMD / LILO_OPT
# Lilo command with options that will reboot and
# poweroff the system.
#AUTOSHUTDOWN_LILO_CMD = "/sbin/lilo"
#AUTOSHUTDOWN_LILO_OPT = "-R PowerOff"

# ======================================================================
# Events
# ======================================================================
#
# You can add more keybindings by adding them to the correct hash. 
# e.g. If you want to send 'contrast -100' to mplayer by pressing the '1' key, 
# just add the following line: 
#
# EVENTS['video']['1'] = Event(VIDEO_SEND_MPLAYER_CMD, arg='contrast -100')
#
# See src/event.py for a list of all possible events.

#
# Some events to jump to menus
#
# EVENTS['menu']['GUIDE'] = Event(MENU_GOTO_TVGUIDE) # Not working
# EVENTS['menu']['VIDEOS'] = Event(MENU_GOTO_VIDEOS)
# EVENTS['menu']['MUSIC'] = Event(MENU_GOTO_MUSIC)
# EVENTS['menu']['PICTURES'] = Event(MENU_GOTO_IMAGES)
# EVENTS['menu']['GAMES'] = Event(MENU_GOTO_GAMES)
# EVENTS['menu']['RADIO'] = Event(MENU_GOTO_RADIO) # Not working
# EVENTS['menu']['POWER'] = Event(MENU_GOTO_SHUTDOWN)

#
# Use arrow keys for back and select (alternate way of navigating)
#
# MENU_ARROW_NAVIGATION = 0

#
# Process keyboard events from SDL. You want this unless you use only lirc
# or event devices below.
#
# USE_SDL_KEYBOARD = 1

#
# Keymap to map keyboard keys to event strings. You can also add new keys
# here, e.g. KEYMAP[key.K_x] = 'SUBTITLE'. The K_-names are defined by pygame.
#

#
# List of /dev/input/event# devices to monitor. You can specify either the
# device node (e.g. '/dev/input/event1') or the name of the device (e.g.
# 'ATI Remote Wonder II'). If you monitor your keyboard both here and with
# USE_SDL_KEYBOARD, then you will get duplicate events.
#
EVENT_DEVS = []

# Keymap to map input events to event strings. You can change current mappings
# and add new ones here, e.g. EVENTMAP['KEY_COFFEE'] = 'SUBTITLE'. Key names
# are defined by the Linux input layer (input.h). An axis is described by a
# pair, one for positive and one for negative movement, e.g.
#
# EVENTMAP['REL_Z'] = ('LEFT', 'RIGHT')

# Use Internet resources to fetch information?
# For example, Freevo can use CDDB for album information,
# the IMDB movie database for movie info, and Amazon for cover searches. 
# Set this to 0 if your computer isn't connected to a network.
#
USE_NETWORK = 1

#
# Directory location to save files when the normal filesystem
# doesn't allow saving. This directory can save covers and fxd files
# for read only filesystems like ROM drives. Set this variable to your
# old MOVIE_DATA_DIR if you have one. It needs to be set to a directory
# Freevo can write to.
#
# OVERLAY_DIR = os.path.join(FREEVO_CACHEDIR, 'vfs')

#
# Umask setting for all files.
# 022 means only the user has write access. If you share your Freevo
# installation with different users, set this to 002
#
# UMASK = 022

#
# Suffix for playlist files
#
# PLAYLIST_SUFFIX = [ 'm3u' ]

#
# Use md5 in mmpython to create unique disc ids. Enable this if you have
# problems with different discs having the same id.
#
# MMPYTHON_CREATE_MD5_ID = 0

#
# Keep metadata in memory
# Setting this variable will keep all cache files in memory. Startup will be
# slower, but for large directories, this will speed up the display.
# 0 = Only keep current dir in memory. Use this if you have too much data
#     and not enough RAM
# 1 = Once loaded, keep cachefile for directory in memory
# 2 = Load all cachefiles on startup
#
# WARNING: you should not run 'freevo cache' when freevo is running.
#
# MEDIAINFO_USE_MEMORY = 1

#
# Cache images. This uses a lot of disc space but it's a huge speed
# enhancement. The images will be cached in OVERLAY_DIR
#
#CACHE_IMAGES = 1


# ======================================================================
# Plugins:
# ======================================================================

# Remove undesired plugins by setting plugin.remove(code). 
# You can also use the name to remove a plugin. But if you do that, 
# all instances of this plugin will be removed.
#
# Examples:
# plugin.remove(plugin_tv) or
# plugin.remove('tv') will remove the tv module from the main menu
# plugin.remove(rom_plugins['image']) will remove the rom drives from the
#   image main menu,
# plugin.remove('rom_drives.rom_items') will remove the rom drives from all
#   menus
#
# See freevo_config.py for a list of loaded plugins
#plugin.remove(plugin_tv) 


#
# Use ivtv_record instead if you have an ivtv based card (PVR-250/350)
# and want freevo to do everthing for you. TV_SETTINGS must be set 
# correctly. To use you need to set the following two lines:
#
# plugin.remove('tv.generic_record')
# plugin_record = plugin.activate('tv.ivtv_record')

#
# Enable this for joystick support:
plugin.activate('joy')


# ----------------------------------------------------------------------
# Headlines
#
# You are free to use any rss feeds in the HEADLINES_LOCATIONS below
# These are just working examples for the Freevo feeds.
# To turn off Headlines add plugin.remove('headlines')
# ----------------------------------------------------------------------
#plugin.activate('headlines', level=45)
# HEADLINES_LOCATIONS = [
#    ('Freevo news releases', 'http://sourceforge.net/export/rss2_projnews.php?group_id=46652'),
#    ('Freevo file releases', 'http://sourceforge.net/export/rss2_projfiles.php?group_id=46652'),
#    ('Freevo summary+stats', 'http://sourceforge.net/export/rss2_projsummary.php?group_id=46652')
#    ('Freevo donors', 'http://sourceforge.net/export/rss2_projdonors.php?group_id=46652'),
# ]

# ----------------------------------------------------------------------
# CD Ripping
# ----------------------------------------------------------------------
# CD_RIP_TMP_DIR = '/tmp/'
# CD_RIP_TMP_NAME = 'track_%(track)s_being_ripped'
# CD_RIP_PN_PREF = '%(artist)s/%(album)s/%(track)s - %(song)s'
# CD_RIP_LAME_OPTS = '--vbr-new -b 192 -h'
# CD_RIP_OGG_OPTS = '-m 128'
# CD_RIP_FLAC_OPTS = '-8'
# CD_RIP_CASE = None          # Can be title, upper, lower
# CD_RIP_REPLACE_SPACE = None # Can be '_', '-', etc.

# ----------------------------------------------------------------------
# CD Burning
# ----------------------------------------------------------------------
# CDBURN_AUDIO_DAO = 1
# CDBURN_MKISOFS_PATH = '/usr/bin/mkisofs'
# CDBURN_CDRECORD_PATH = '/usr/bin/cdrecord'
# CDBURN_TEMP_DIR='/tmp/'
# CDBURN_DEV = '/dev/cdrom'
# CDBURN_SPEED = 32

# ----------------------------------------------------------------------
# Freevo Music Player Daemon
# http://www.musicpd.org/
# ----------------------------------------------------------------------
# plugin.activate('mpd')

# ----------------------------------------------------------------------
# Freevo Bluetooth Phone Settings
# ----------------------------------------------------------------------
# This plugin uses The Python bindings for Bluez bluetooth stack.
#
# It can be downloaded from http://org.csail.mit.edu/pybluez/download.html
# or installed with the package manager of your operating system.
#
# To this plugin to work you need the j2me midlet installed in a compatible
# phone.
#
# plugin.activate('freevused')

# if RFCOMM port is already binded wait this seconds to retry binding
# FVUSED_BIND_TIMEOUT = 30

# Translation of commands from j2me client to events of Freevo
# FVUSED_CMDS = {
#       'PREV': 'UP',                # 1st row left
#       'STRT': 'SELECT',            # 1nd row center
#       'NEXT': 'DOWN',              # 1st row right
#       'RWND': 'LEFT',              # 2nd row left
#       'PAUS': 'PAUSE',             # 2nd row center
#       'FFWD': 'RIGHT',             # 2nd row right
#       'VOL-': 'MIXER_VOLDOWN',     # 3rd row left
#       'STOP': 'EXIT',              # 3rd row center
#       'VOL+': 'MIXER_VOLUP',       # 3rd row right
#       'VOLM': 'MIXER_VOLMUTE',     # 4th row left
#       'SLCT': 'ENTER',             # 4th row center
#       'MAIN': 'MENU'               # 4th row right
# }

# ======================================================================
# Freevo directory settings:
# ======================================================================

# You can change all this variables in the folder.fxd on a per folder
# basis
#
# Example:
# <freevo>
#   <folder title="Title of the directory" img-cover="nice-cover.png">
#     <setvar name="directory_autoplay_single_item" val="0"/>
#     <info>
#       <content>A small description of the directory</content>
#     </info>
#   </folder>
# </freevo>

#
# Should directories sorted by date instead of filename?
# 0 = No, always sort by filename.
# 1 = Yes, sort by date
# 2 = No, don't sory by date for normal directories, 
#     but sort by date for TV_RECORD_DIR.
#
# DIRECTORY_SORT_BY_DATE = 2

#
# Should directory items be sorted in reverse order?
#
# DIRECTORY_REVERSE_SORT = 0

#
# Should we use "smart" sorting?
# Smart sorting ignores the word "The" in item names.
#
# DIRECTORY_SMART_SORT = 0

#
# Should files in directories have smart names?
# This removes the first part of the names when identical
#
# DIRECTORY_SMART_NAMES = 1

#
# Should Freevo autoplay an item if only one item is in the directory?
#
# DIRECTORY_AUTOPLAY_SINGLE_ITEM = 1

#
# Force the skin to use a specific layout number. -1 == no force. The layout
# toggle with DISPLAY will be disabled
#
# DIRECTORY_FORCE_SKIN_LAYOUT = -1

#
# Format string for the audio item names. 
#
# Possible strings:
# a=artist, n=tracknumber, t=title, y=year, f=filename
#
# Example:
# This will show the title and the track number:
# DIRECTORY_AUDIO_FORMAT_STRING = '%(n)s - %(t)s'
#
# DIRECTORY_AUDIO_FORMAT_STRING = '%(t)s'

#
# Use media id tags to generate the name of the item. This should be
# enabled all the time. It should only be disabled for directories with 
# broken tags.
#
# DIRECTORY_USE_MEDIAID_TAG_NAMES = 1

#
# The following settings determine which features are available for
# which media types.
#
# If you set this variable in a folder.fxd, the value is 1 (enabled)
# or 0 (disabled).
# 
# Examples:
# To enable autoplay for audio and image files:
# DIRECTORY_AUTOPLAY_ITEMS = [ 'audio', 'image' ]
# To disable autoplay entirely:
# DIRECTORY_AUTOPLAY_ITEMS = []

# Make all items a playlist. So when one is finished, the next one will
# start. It's also possible to browse through the list with UP and DOWN
#
# DIRECTORY_CREATE_PLAYLIST     = [ 'audio', 'image' ]

# Add playlist files ('m3u') to the directory
#
# DIRECTORY_ADD_PLAYLIST_FILES  = [ 'audio', 'image' ]

# Add the item 'Random Playlist' to the directory
#
# DIRECTORY_ADD_RANDOM_PLAYLIST = [ 'audio' ]

# Make 'Play' not 'Browse' the default action when only items and not
# subdirectories are in the directory
#
# DIRECTORY_AUTOPLAY_ITEMS      = [ ]


# ======================================================================
# Freevo movie settings:
# ======================================================================

#
# Where the movie files can be found.
# This is a list of items (e.g. directories, fxd files). The items themselves
# can also be a list of (title, file)
#
# VIDEO_ITEMS = [ ('action movies', '/files/movies/action'),
#                 ('funny stuff', '/files/movies/comedy') ]
#
# Some people access movies on a different machine using an automounter.
# To avoid timeouts, you can specify the machine name in the directory
# to check if the machine is alive first
# Directory myserver:/files/server-stuff will show the item for the
# directory /files/server-stuff if the computer myserver is alive.

VIDEO_ITEMS = [ ('Local Videos', '/root/videos'), ('Torrents', '192.168.2.3:/torrents') ]

VIDEO_SHOW_DATA_DIR = '/root/videos'

#
# The list of filename suffixes that are used to match the files that
# are played wih MPlayer.
# 
# VIDEO_MPLAYER_SUFFIX = [ 'avi', 'mpg', 'mpeg', 'wmv', 'bin', 'rm',
#                          'divx', 'ogm', 'vob', 'asf', 'm2v', 'm2p',
#                          'mp4', 'viv', 'nuv', 'mov', 'iso',
#                          'nsv', 'mkv' ]

#
# The list of filename suffixes that are used to match the files that
# are played wih Xine.
# 
# VIDEO_XINE_SUFFIX = [ 'avi', 'mpg', 'mpeg', 'rm', 'divx', 'ogm',
#                       'asf', 'm2v', 'm2p', 'mp4', 'mov', 'cue' ]

#
# Preferred video player
#
# VIDEO_PREFERED_PLAYER = 'mplayer'

#
# Only scan OVERLAY_DIR and VIDEO_SHOW_DATA_DIR for fxd files containing
# information about a disc. If you only have the fxd files for discs in
# one of this directories (and subdirectories), set this to 1, it will
# speed up startup, 0 may be needed if you have fxd files with disc links
# in your normal movie tree.
#
# VIDEO_ONLY_SCAN_DATADIR = 1

# PRE and POST playing commands.  Set these to a runnable command if
# you wish to do something before and after playing a video, like
# dimming the lights
# VIDEO_PRE_PLAY  = None
# VIDEO_POST_PLAY = None

# ======================================================================
# Freevo audio settings:
# ======================================================================

#
# Where the Audio (mp3, ogg) files can be found.
# This is a list of items (e.g. directories, fxd files). The items themselves
# can also be a list of (title, file)
#
# To add webradio support, add fxd/webradio.fxd to this list
#
# AUDIO_ITEMS = [ ('Music Collection', '/local/mp3/'),
#                 'fxd/webradio.fxd' ]

#
# The list of filename suffixes that are used to match the files that
# are played as audio.
# 
# AUDIO_SUFFIX = [ 'mp3', 'ogg', 'wav','m4a', 'wma', 'aac', 'flac', 'mka' ]

#
# Regular expression used to recognize filenames which are likely to be 
# covers for an album 
#
# This will match front.jpg and cover-f.jpg, but not back.jpg nor cover-b.jpg:
# AUDIO_COVER_REGEXP = 'front|-f'

#
# Preferred audio player
#
# AUDIO_PREFERED_PLAYER = 'mplayer'

#
# Show video files in the audio menu (for music-videos)
#
# AUDIO_SHOW_VIDEOFILES = False

# ======================================================================
# Freevo image viewer settings:
# ======================================================================

#
# Where image files can be found.
# This is a list of items (e.g. directories, fxd files). The items itself
# can also be a list of (title, file)
#
# IMAGE_ITEMS = None

#
# The list of filename suffixes that are used to match the files that
# are used for the image viewer.
# 
# IMAGE_SUFFIX = [ 'jpg','gif','png','jpeg','bmp','tiff','psd' ]

#
# The viewer now supports a new type of menu entry, a slideshow file.
# It also has the slideshow alarm signal handler for automated shows.
# It uses a new configuration option:
#
# IMAGE_SSHOW_SUFFIX = [ 'ssr' ]

#
# Mode of the blending effect in the image viewer between two images
# Possible values are:
#
# None: no blending
# -1    random effect
#  0    alpha blending
#  1    wipe effect
#
IMAGEVIEWER_BLEND_MODE = -1
    


# ======================================================================
# Freevo games settings:
# ======================================================================

#
# MAME is an emulator for old arcade video games. It supports almost
# 2000 different games! The actual emulator is not included in Freevo,
# you'll need to download and install it separately. The main MAME
# website is at http://www.mame.net, but the version that is used here
# is at http://x.mame.net since the regular MAME is for Windows.
#
# SNES stands for Super Nintendo Entertainment System. Freevo relies
# on other programs that are not included in Freevo to play these games.
# 
# NEW GAMES SYSTEM :
# =================
# The GAMES_ITEMS structure is now build as follows :
# <NAME>, <FOLDER>, (<TYPE>, <COMMAND_PATH>, <COMMAND_ARGS>, <IMAGE_PATH>, \
# [<FILE_SUFFIX_FOR_GENERIC>])
# where :
#              - <TYPE> : Internal game types (MAME or SNES) or
#                         generic one (GENERIC)
#              - <COMMAND_PATH> : Emulator command
#              - <COMMAND_ARGS> : Arguments for the emulator
#              - <IMAGE_PATH>   : Optionnal path to the picture
#              - <FILE_SUFFIX_FOR_GENERIC> : If the folder use the GENERIC
#                                            type, then you must specify here
#                                        the file suffix used by the emulator
# GAMES_ITEMS = [
#     ('MAME', '/home/media/games/xmame/roms',     
#         ('MAME', '/usr/local/bin/xmame.SDL', '-fullscreen -modenumber 6', 
#             '/home/media/games/xmame/shots', None)),
#     ('SUPER NINTENDO', '/home/media/games/snes/roms', 
#         ('SNES', '/usr/local/bin/zsnes', '-m -r 3 -k 100 -cs -u', '', None )),
#     ('Visual Boy Advance', '/home/media/games/vba/roms/',
#         ('GENERIC', '/usr/local/vba/VisualBoyAdvance', ' ', '', [ 'gba' ] )),
#     ('MEGADRIVE', '/home/media/games/megadrive/roms', 
#         ('GENESIS', '/usr/local/bin/generator-svgalib', '', '', '' ))
# ]
#
# GAMES_ITEMS = None

#
# These settings are used for the MAME arcade emulator:
#

# Priority of the game process
# 0 = Don't change the priority
# >0 - Lower priority
# <0 - Higher priority
#
# GAMES_NICE = -20

# 
# MAME cache directory
#
# GAMES_MAME_CACHE = '%s/romlist-%s.pickled' % (FREEVO_CACHEDIR, os.getuid())

# ======================================================================
# Freevo SKIN settings:
# ======================================================================

#
# XML file for the skin. If SKIN_XML_FILE is set, this skin will be
# used, otherwise the skin will rememeber the last choosen skin.
#
# SKIN_XML_FILE = 'blurr'
#
#
# Select a way when to switch to text view even if a image menu is there
# 
# 1 = Force text view when all items have the same image and there are no
#     directories
# 2 = Ignore the directories, always switch to text view when all images
#     are the same
#
# SKIN_FORCE_TEXTVIEW_STYLE = 1

#
# Force text view for the media menu
# (The media menu is the first menu displayed for video, audio, images 
# and games). 
#
# SKIN_MEDIAMENU_FORCE_TEXTVIEW = 0


# ======================================================================
# Freevo OSD settings:
# ======================================================================

#
# System Path to search for fonts not included in the Freevo distribution
#
# OSD_EXTRA_FONT_PATH = [ '/usr/X11R6/lib/X11/fonts/truetype/' ]

#
# Font aliases 
# All names must be lowercase! All alternate fonts must be in './share/fonts/'
#
# OSD_FONT_ALIASES = { 'arial_bold.ttf' : 'VeraBd.ttf' }

# For non-european character sets the OSD_FORCE_FONTNAME and 
# OSD_FORCE_FONTSIZE can be set. The size is a scaling ratio, ie 1.2.
# Setting OSD_FORCE_FONTNAME='batang.ttf' and OSD_FORCE_FONTSIZE=1.0
# allows Korean characters.
# OSD_FORCE_FONTNAME = None
# OSD_FORCE_FONTSIZE = None
#
# Number of seconds to wait until the busy icon is shown in the menu.
# Busy icon can also be shown right away when there is more than a certain
# number of files in a directory.
# 
# Set this to None to disable this.
# (seconds, files)
#
# OSD_BUSYICON_TIMER = (0.7, 200)

# OSD_OVERSCAN_X = 0
# OSD_OVERSCAN_Y = 0

#
# Execute a script on OSD startup.
#
# OSD_SDL_EXEC_AFTER_STARTUP = ""

#
# Execute a script on OSD close.
#
# OSD_SDL_EXEC_AFTER_CLOSE = ""

#
# Stop the osd before playing a movie with xine or mplayer. Some output
# devices need this. After playback, the osd will be restored
#
# OSD_STOP_WHEN_PLAYING = 0

#
# Dim text that doesn't fit instead of using ellipses. 
# OSD_DIM_TEXT = 1
    
# ======================================================================
# Freevo remote control settings:
# ======================================================================

#
# Location of the lircrc file
#
# For remote control support, Freevo needs a lircrc file, like this:
#
# begin
#       prog = freevo
#       button = select
#       config = SELECT
# end
#
# Check contrib/lirc for examples and helpers/freevo2lirc.pl for a converter
# script.
#
# LIRCRC = '/etc/freevo/lircrc'

#
# Joystick support
# 0 = Disable joystick support 
# 1 = Use js0, 
# 2 = Use js1, 
#  ... etc
#
JOY_DEV = 1
#JOY_SENS = 16384
JOY_SENS = 32000

# Freevo can support as many buttons as your controller has
# as long as there is a corresponding entry in JOY_CMDS.
# You will also need to plugin.activate('joy').
# FYI: new kernels use /dev/input/jsX, but joy.py will fall back on /dev/jsX
#
# JOY_CMDS = {
#     'up'             : 'UP',
#     'down'           : 'DOWN',
#     'left'           : 'LEFT',
#     'right'          : 'RIGHT',
#     'button 1'       : 'PLAY',
#     'button 2'       : 'PAUSE',
#     'button 3'       : 'STOP',
#     'button 4'       : 'ENTER',
# }


# Buttons for the PS3 controller
# ( as reported by jtest):
# UP            btn 4
# RIGHT         btn 5
# DOWN          btn 6
# LEFT          btn 7
# L1            btn 10
# L2            btn 8
# L3 (analog)   btn 1
# R1            btn 11
# R2            btn 9
# R3 (analog)   btn 2
# <triangle>    btn 12
# <circle>      btn 13
# <x>           btn 14
# <square>      btn 15
# <select>      btn 0
# <start>       btn 3
# Note: buttons for freevo need to be button-value +1 
# so above <btn 0> = freevo <button 1>

# all button-values for JOY_CMDS need to be there: 
# Optional commands that can be mapped can be found in: /src/event.py

JOY_CMDS = {     
     'button 5'       : 'UP',
     'button 7'       : 'DOWN',
     'button 8'       : 'LEFT',
     'button 6'       : 'RIGHT',
     'up'             : 'UP',
     'down'           : 'DOWN',
     'left'           : 'LEFT',
     'right'          : 'RIGHT',
     'button 14'      : 'SELECT',         # <circle>
     'button 16'      : 'EXIT',           # <square>
     'button 15'      : 'STOP',           # <x>
     'button 1'       : 'ENTER',          # <select>

     'button 11'      : 'VOL+',           # <L1>
     'button 9'       : 'VOL-',           # <L2>
     'button 2'       : 'MUTE',           # <L3>      
     
     'button 10'      : 'MUTE',           # <R2>
     'button 4'       : 'PLAY',           # <start>
     'button 13'      : 'PLAY',           # <start>
     'button 17'      : 'MENU',           # <ps> 
}

EVENTS['global']['VOL+'] = Event('MIXER_VOLUP', arg=10)
EVENTS['global']['VOL-'] = Event('MIXER_VOLDOWN', arg=10)

#JOY_LOCKFILE = '/tmp/.joy_lockfile'


# ======================================================================
# TVtime settings:
# ======================================================================

#
# Location of the TV time program
# Default: Use the value in freevo.conf
# 
# TVTIME_CMD = CONF.tvtime


# ======================================================================
# MPlayer settings:
# ======================================================================

# MPLAYER_AO_DEV      = 'oss:/dev/dsp'  # e.g.: oss,sdl,alsa, see mplayer docs

# MPLAYER_VO_DEV_OPTS = ''              # e.g.: ':some_var=vcal'

# DVD_LANG_PREF       = 'en,se,no'      # Order of preferred languages on DVD.
# DVD_SUBTITLE_PREF   = ''              # Order of preferred subtitles on DVD.

# Priority of mplayer process. 0 is unchanged, <0 is higher prio, >0 lower prio.
# prio <0 has no effect unless run as root.
# MPLAYER_NICE        = -20             

#
# Mplayer options to use the software scaler. If your CPU is fast enough, you
# might try a software scaler. You can disable it later for some larger files
# with the mplayer option '-nosws'. If you have -framedrop or -hardframedrop
# as mplayer option, the software scaler will also not be used.
# A good value for this variable is:
#MPLAYER_SOFTWARE_SCALER = "-subfont-text-scale 5 -fs -sws 2 -vf scale=%s:-3,"\
#                           "expand=%s:%s " % ( CONF.width, CONF.width, CONF.height )
# older versions of mplayer may need
# MPLAYER_SOFTWARE_SCALER = '-xy %s -sws 2 -vop scale:-1:-1:-1:100' % CONF.width
#
MPLAYER_SOFTWARE_SCALER = ''

#
# Mplayer arguments for different media formats. (eg DVDs, CDs, AVI files, etc)
# Uses a default value if nothing else matches.
#
# MPLAYER_ARGS = { 'dvd'    : '-cache 8192',
#                  'vcd'    : '-cache 4096',
#                  'cd'     : '-cache 1024 -cdda speed=2',
#                  'tv'     : '-nocache',
#                  'ivtv'   : '-cache 8192',
#                  'avi'    : '-cache 5000 -idx',
#                  'rm'     : '-cache 5000 -forceidx',
#                  'rmvb'   : '-cache 5000 -forceidx',
#                  'webcam' : 'tv:// -tv driver=v4l:width=352:height=288:outfmt=yuy2:device=/dev/video2',
#                  'default': '-cache 5000'
#                  }

#
# Number of seconds before seek value times out. This is used when
# seeking a specified number of minutes into a movie. If you make
# a mistake or change your mind, the seek value will timeout after
# this many seconds.
#
# MPLAYER_SEEK_TIMEOUT = 8

#
# Autocrop files when playing. This is useful for files in 4:3 with black
# bars on a 16:9 tv
#
# MPLAYER_AUTOCROP = 0

#
# Try to set correct 'delay' and 'mc' values for mplayer based on the delay
# from mmpython. 
#
# This should correct av sync problems with mplayer for some files, but 
# may also break things. (I don't know, that's why it's disabled by default). 
# WARNING: When seeking, the playback is out of sync for some seconds! 
#
# MPLAYER_SET_AUDIO_DELAY = 0

#
# Mplayer video filter for interlaced or progressive videos. If you have
# a slow pc, do not use post processing
# MPLAYER_VF_INTERLACED  = ''
# MPLAYER_VF_PROGRESSIVE = 'pp=fd'
# For pal and dvb-t recordings, the following looks good
# MPLAYER_VF_INTERLACED  = 'pp=md/de,phase=U'
#
# MPLAYER_VF_INTERLACED  = 'pp=de/fd'
# MPLAYER_VF_PROGRESSIVE = 'pp=de'

# ======================================================================
# Xine settings:
# ======================================================================

# You need xine-ui version greater 0.9.21 to use the all the features
# of the xine plugin

# XINE_VO_DEV  = 'xv'
# XINE_COMMAND = '%s --hide-gui -pq -g -B --geometry %sx%s+0+0 --no-splash' % \
#                  (CONF.xine, CONF.width, CONF.height)

# XINE_ARGS_DEF = '--no-lirc --post=pp:quality=10,expand'

# XINE_AO_DEV = 'oss'                     # alsa or oss

# Set to False if xine doesn't have '--no-lirc' option
# XINE_HAS_NO_LIRC = True


# ======================================================================
# IVTV Xine TV settings:
# ======================================================================

# -- plugin configuration --

#plugin.remove('tv.mplayer')
#plugin.activate('tv.ivtv_xine_tv')

# Note: TV_IVTV_OPTIONS must be configured properly
# Note: FREQUENCY_TABLE must be configured properly
# Note: XINE_COMMAND must be configured properly
# Note: XINE_ARGS_DEF must be configured properly

# -- TV/XINE configuration --

# Video output device for TV. For Hauppage PVR x50,
# use "xxmc" if you have hardware acceleration enabled.
# Otherwise, see XINE_VO_DEV
#XINE_TV_VO_DEV = "xxmc"

# Audio output device to use for TV. See XINE_AO_DEV.
#XINE_TV_AO_DEV = "alsa"

# This specifies the path and filemask that
# xine uses for timeshifting. File can get
# quite big (several gigabytes)
#XINE_TV_TIMESHIFT_FILEMASK = "/tmp/xine-buf-"

# ======================================================================
# Freevo TV settings:
# ======================================================================

#
# This is where recorded video is written.
#
# XXX the path doesn't work from the www cgi scripts!
# TV_RECORD_DIR = None

#
# Watching TV
#
# XXX You must change this to fit your local conditions!
#
# NORM: ntsc, pal, secam
# INPUT: television, composite1
# CHANLIST: One of the following:
#
# us-bcast, us-cable, us-cable-hrc, japan-bcast, japan-cable, europe-west,
# europe-east, italy, newzealand, australia, ireland, france, china-bcast,
# southafrica, argentina, canada-cable, russia
#
# TV_SETTINGS = 'NORM INPUT CHANLIST DEVICE'

TV_CHANNELS = [] 
plugin.remove('tv')

#
# Video input device
#
# Usually /dev/video0, but might be /dev/video1 instead for multiple boards.
#
# FreeBSD uses the Brooktree TV-card driver, not V4L.
#
# TV_DRIVER = 'v4l'
# TV_DEVICE = '/dev/video0'
# TV_INPUT = 0
# 
# Radio device default is None, /dev/video24 for ivtv
# RADIO_DEVICE = '/dev/radio'

# Radio commands:
# plugin.activate('audio.radioplayer')
# plugin.activate('audio.radio')
#
# for fmtools
# RADIO_CMD = 'fm'
# RADIO_CMD_START = (RADIO_CMD + ' ' + '-q %s 65535')
# RADIO_CMD_STOP = (RADIO_CMD + ' ' + '-q off')
#
# for ivtv-radio
# RADIO_CMD = '/usr/bin/ivtv-radio -d /dev/radio0 -i /dev/video24'
# RADIO_STATIONS = [
#     ('DRS 1', '94.80'),
#     ('VIRUS', '104.30'),
#     (u'Radio Zürisee', '90.20'),
# ]

#
# Additional options to pass to mplayer in TV mode.
#
# eg. To turn off deinterlacing:
# TV_OPTS = '-vop pp=ci'
#
# TV_OPTS = ''

# TV_SETTINGS = '%s television %s %s' % (CONF.tv, CONF.chanlist, TV_DEVICE)

#
# Size (in MB) of the timeshift buffer. (ie: how long you can pause tv for.)  
# This is set to a low default because the default buffer location is 
# under FREEVO_CACHEDIR and we don't want to blow /var or /tmp.
# TIMESHIFT_BUFFER_SIZE = 128

# TIMESHIFT_ENCODE_CMD = 'mp1e -m3 -c%s -p%s -r14,100' % \
#                        (TV_SETTINGS.split()[3], AUDIO_INPUT_DEVICE) 

# TIMESHIFT_BUFFER = '%s/timeshift.mpeg' % FREEVO_CACHEDIR

# TV_DATEFORMAT = '%e-%b' # Day-Month: 11-Jun
# TV_TIMEFORMAT = '%H:%M' # Hour-Minute 14:05
# TV_DATETIMEFORMAT = '%A %b %d %I:%M %p' # Thursday September 24 8:54 am

# This is the filename format for files recorded using Freevo.
# You can use any of the strftime variables in it, provided you
# put two '%%' at the beginning. 
# 
# Some examples:
# %%A - Full weekday name.
# %%H - Hour (24-hour clock) as a decimal number [00,23].
# %%M - Minute as a decimal number [00,59].
# %%m - Month as a decimal number [01,12].
# %%d - Day of the month as a decimal number [01,31].
# %%p - Locale's equivalent of either AM or PM.
# 
# More can be found at: http://www.python.org/doc/current/lib/module-time.html

# TV_RECORDFILE_MASK = '%%m-%%d %%H:%%M %(progname)s - %(title)s'


# if using the persitant recordserver
# TV_RECORD_SCHEDULE = '%s/record_schedule.xml' % FREEVO_CACHEDIR

# RECORDSERVER_IP = 'localhost'
# RECORDSERVER_PORT = 18001

# Remove old recordings if GB free is less than specified value
# RECORDSERVER_CLEANUP_THRESHOLD = 0

# start every recording X minutes before scheduled,
# and stop X minutes after scheduled - default to zero minutes.
# This must be a value in seconds although at the moment only has
# the percision of one minute.
# TV_RECORD_PADDING = 0 * 60

# VCR_AUDIO = (':adevice=%s' % AUDIO_DEVICE +
#              ':audiorate=32000' +         # 44100 for better sound
#              ':forceaudio:forcechan=1:' + # Forced mono for bug in my driver
#              'buffersize=64')             # 64MB capture buffer, change?

# TV capture size for viewing and recording. Max 768x480 for NTSC,
# 768x576 for PAL. Set lower if you have a slow computer!
#
# For the 'tvtime' TV viewing application, only the horizontal size is used.
# Set the horizontal size to 400 or 480 if you have a slow (~500MHz) computer,
# it still looks OK, and the picture will not be as jerky.
# The vertical size is always either fullscreen or 480/576 (NTSC/PAL)
# for tvtime.
# TV_VIEW_SIZE = (640, 480)
# TV_REC_SIZE = (320, 240)   # Default for slower computers

# Input formats for viewing and recording. The format affect viewing
# and recording performance. It is specific to your hardware, so read
# the MPlayer docs and experiment with mplayer to see which one fits
# your computer best.
# TV_VIEW_OUTFMT = 'yuy2'   # Better quality, slower on pure FB/X11
# TV_REC_OUTFMT = 'yuy2'

# XXX Please see the mencoder docs for more info about the settings
# XXX below. Some stuff must be changed (adevice), others probably
# XXX should be ("Change"), or could be in some cases ("change?")
# VCR_CMD = (CONF.mencoder + ' ' +
#            'tv:// ' +                      # New mplayer requires this.
#            '-tv driver=%s:input=%d' % (TV_DRIVER, TV_INPUT) +
#            ':norm=%s' % CONF.tv +
#            ':channel=%(channel)s' +        # Filled in by Freevo
#            ':chanlist=%s' % CONF.chanlist +
#            ':width=%d:height=%d' % (TV_REC_SIZE[0], TV_REC_SIZE[1]) +
#            ':outfmt=%s' % TV_REC_OUTFMT +
#            ':device=%s' % TV_DEVICE +
#            VCR_AUDIO +                     # set above
#            ' -ovc lavc -lavcopts ' +       # Mencoder lavcodec video codec
#            'vcodec=mpeg4' +                # lavcodec mpeg-4
#            ':vbitrate=1200:' +             # Change lower/higher, bitrate
#            'keyint=30 ' +                  # Keyframe every 10 secs, change?
#            '-oac mp3lame -lameopts ' +     # Use Lame for MP3 encoding, must be enabled in mencoder!
#            'br=128:cbr:mode=3 ' +          # MP3 const. bitrate, 128 kbit/s
#            '-ffourcc divx ' +              # Force 'divx' ident, better compat.
#            '-endpos %(seconds)s ' +        # only mencoder uses this so do it here.
#            '-o %(filename)s')         # Filled in by Freevo


#
# Settings for ivtv based cards such as the WinTV PVR-250/350.
#
# XXX TODO: Add descriptions and valid settings for each option.
# bitrate in bps
# stream type
# Options are: 0 (mpeg2_ps), 1 (mpeg2_ts), 2 (mpeg1), 3 (mpeg2_pes_av),
#              5 (mpeg2_pes_v), 7 (mpeg2_pes_a), 10 (dvd)

# TV_IVTV_OPTIONS = {
#     'input'         : 4,
#     'resolution'    : '720x480',
#     'aspect'        : 2,
#     'audio_bitmask' : 233,
#     'bframes'       : 3,
#     'bitrate_mode'  : 1,
#     'bitrate'       : 4000000,
#     'bitrate_peak'  : 4000000,
#     'dnr_mode'      : 0,
#     'dnr_spatial'   : 0,
#     'dnr_temporal'  : 0,
#     'dnr_type'      : 0,
#     'framerate'     : 0,
#     'framespergop'  : 15,
#     'gop_closure'   : 1,
#     'pulldown'      : 0,
#     'stream_type'   : 10,
# }

#
# FREQUENCY_TABLE - This is only used when Freevo changes the channel natively.
# This is only the case if you are using V4L2 and any of the following plugins:
# timeshift, ivtv_record, ivtv_basic_tv.
# For the standard frequancy tables see src/tv/freq.py.  To add your own just 
# replace tuner_id in the following example with a valid tuner id (ie: '5' or
# 'BBC1') and a frequency in KHz.  You may have as many entries as you like,
# anything here will simply override a corresponding entry in your standard
# frequency table and you can also have entries here that are not present in
# there.

# FREQUENCY_TABLE = {
#     'tuner_id'   :    55250,
# }


# VIDEO_GROUPS is a new setting to handle multiple arbitrary groups of devices
# for viewing or recording.  It will be possible to have different Freevo
# channels use different Video Groups.

# VIDEO_GROUPS = [
#     # Use this group for watching tv
#     VideoGroup(vdev=TV_DEVICE,
#                adev=AUDIO_DEVICE,
#                input_type='tuner',
#                tuner_norm=CONF.tv,
#                tuner_chanlist=CONF.chanlist,
#                desc='Watching Video Group',
#                record_group=1),
#     # Use this group for recording tv
#     VideoGroup(vdev='/dev/video1',
#                adev=AUDIO_DEVICE,
#                input_type='tuner',
#                tuner_norm=CONF.tv,
#                tuner_chanlist=CONF.chanlist,
#                desc='Recording Video Group',
#                record_group=None),
# ]


#
# TV Channels. This list contains a mapping from the displayed channel name
# to the actual channel name as used by the TV watching application.
# The display name must match the names from the XMLTV guide,
# and the TV channel name must be what the tuner expects (usually a number).
#
# The TV menu is supposed to be supported by the XMLTV application for
# up to date listings, but can be used without it to just display
# the available channels.
#
# This list also determines the order in which the channels are displayed!
# N.B.: You must delete the XMLTV cache file (e.g. /var/cache/freevo/TV.xml.pickled)
#       if you make changes here and restart!
#
# Format: [('xmltv channel id', 'freevo display name', 'tv channel name'), ...]
#
# If this variable is set to None (default), Freevo will try to auto-detect
# the channel list based on the xmltv file. This doesn't work for all
# xmltv grabber, e.g. the German list doesn't contain station lists. In this
# case Freevo will output the possible list for you to add them manually.
#
# If auto-detection doesn't work or you want to edit the list, run
# freevo tv_grab -query.
#
# Setting this variable to [] will deactivate the tv guide. If you don't have
# a tv card, you may also want to add plugin.remove('tv') to remove the whole
# tv menu.
#
# All channels listed here will be displayed on the TV menu, even if they're
# not present in the XMLTV listing.
# 
#
# Timedependent channels:
#
# The TV_CHANNELS-list can look like this:
#
# TV_CHANNELS = [('21', 'SVT1',              'E5'),
#                ('22', 'SVT2',              'E3'),
#                ('26', 'TV3',               'E10'),
#                ('27', 'TV4',               'E6'),
#                ('10', 'Kanal 5',           'E7'),
#                ('60', 'Fox Kids',          'E8', ('1234567','0600','1659')),
#                ('16', 'TV6',               'E8', ('1234567','1700','2359'), 
#                                                  ('1234567','0000','0300')),
#                ('14', 'MTV Europe',        'E11') ]
#
# As you can see the list takes optional tuples:
# ( 'DAYS', 'START','END')
#
# 1234567 in days means all days.
# 12345 would mean monday to friday.
#
# It will display "Fox Kids" from 06:00 to 16:59 and "TV6" from 17:00 to 03:00. 
# 03:00 to 06:00 it won't be displayed at all.
#

# TV_CHANNELS = None

#
# Program to grab xmltv listings. To get a grabber, you need to download
# xmltv. A possible value for users in the USA is tv_grab_na
# Use the tv_grab helper to grab the listings and cache them. Start
# 'freevo tv_grab --help' for more informations.

# XMLTV_GRABBER = ''

#
# If you want to run tv_sort on your listings add the path to tv_sort here.
# tv_sort will make sure all your programs have proper stop times, otherwise
# programs might get cut off at midnight.
#
# XMLTV_SORT = ''

#
# Number of days the grabber should get
#
# XMLTV_DAYS = 3


# ======================================================================
# Freevo builtin rss server settings:
# ======================================================================
# RSSSERVER_UID = 0
# RSSSERVER_GID = 0

# RSS_FEEDS = '/etc/freevo/rss.feeds'
# RSS_VIDEO = '/media/video'
# RSS_AUDIO = '/media/podcasts'

# ======================================================================
# Freevo builtin WWW server settings:
# ======================================================================

#
# To activate the built in web server, uncomment the following line
#
# plugin.activate('www')

#
# Web server port number. 80 is the standard port, but is often
# taken already by apache, and cannot be used unless the server
# runs as root. Port 8080 is the default, change to 80 if
# needed.
#
# WEBSERVER_PORT = 8080

#
# Username / Password combinations to login to the web interface.
# 
# WWW_USERS = {
#     "user1" : "changeme", 
#     "optional" : "changeme2"
# }
#

#
# Divide the TV guide into intervals of this length (in minutes)
#
# WWW_GUIDE_INTERVAL = 30

#
# Precision for TV guide (in minutes)
#
# WWW_GUIDE_PRECISION = 5 #

#
# Show this many blocks at once
#
# WWW_GUIDE_COLS = 6

# WWW_STYLESHEET = 'styles/main.css'

# WWW_JAVASCRIPT = 'scripts/display_prog-head.js'


# ======================================================================
# Internal stuff, you shouldn't change anything here unless you know
# what you are doing
# ======================================================================

#
# Config for xml support in the movie browser
# the regexp has to be with ([0-9]|[0-9][0-9]) so we can get the numbers
#
# VIDEO_SHOW_REGEXP = "s?([0-9]|[0-9][0-9])[xe]([0-9]|[0-9][0-9])[^0-9]"


#
# Remote control daemon. The server is in the Freevo main application,
# and the client is a standalone application in rc_client/
#
# ENABLE_NETWORK_REMOTE = 0
# REMOTE_CONTROL_HOST = '127.0.0.1'
# REMOTE_CONTROL_PORT = 16310


#
# XMLTV File
#
# This is the XMLTV file that can be optionally used for TV listings
#
# XMLTV_FILE = '/tmp/TV.xml'

#
# XML TV Logo Location
#
# Use the "makelogos.py" script to download all the
# Station logos into a directory. And then put the path
# to those logos here
# TV_LOGOS = OS_CACHEDIR + '/xmltv/logos'

# LOCALE='latin-1'

# ======================================================================
# Idlebar and plugins
#
# These are the default idlebar settings, there are many more see:
# freevo plugins -l for a complete list
# To turn off use plugin.remove('idlebar.cdstatus')
#
# clock display
# %A - Full weekday name.
# %a - Abbreviated weekday name.
# %B - Full month name
# %b - Abbreviated month name
# %I - Hour (12-hour clock) as a decimal number [01,12].
# %H - Hour (24-hour clock) as a decimal number [00,23].
# %M - Minute as a decimal number [00,59].
# %m - Month as a decimal number [01,12].
# %b - Name of Month
# %d - Day of the month as a decimal number [01,31].
# %p - Locale's equivalent of either AM or PM.
# %y - Year without century as a decimal number [00,99].          
# %Y - Year with century as a decimal number.
# ======================================================================
# plugin.activate('idlebar')
# plugin.activate('idlebar.tv', level = 20)
# plugin.activate('idlebar.cdstatus', level = 25)
# plugin.activate('idlebar.diskfree', level = 30)
# plugin.activate('idlebar.clock', level = 50)
# CLOCK_FORMAT = '%a %d %H:%M'
#
# settings for the idlebar.diskfree plug-in, in Gigabytes
# DISKFREE_VERY_LOW = 8 # less than this shows a red bar
# DISKFREE_LOW = 20     # less than this shows an orange bar
#
# display proc-stats, CPU and RAM usage
plugin.activate('idlebar.system.procstats',level=20)
