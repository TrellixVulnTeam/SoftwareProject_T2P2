# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# tvtime.py - implementation of a TV function using tvtime
# -----------------------------------------------------------------------
# $Id: tvtime.py 8441 2006-10-21 11:15:52Z duncan $
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


# Configuration file. Determines where to look for AVI/MP3 files, etc
import config

import time, os
import string
import threading
import signal
import cgi
import re
import popen2
from xml.dom.ext.reader import Sax2
from xml.dom.ext import PrettyPrint
from cStringIO import StringIO

import util    # Various utilities
import osd
import rc      # The RemoteControl class.
import childapp # Handle child applications
import tv.epg_xmltv as epg # The Electronic Program Guide
import event as em
from tv.channels import FreevoChannels

import plugin

# Set to 1 for debug output
DEBUG = config.DEBUG

# Create the OSD object
osd = osd.get_singleton()

class PluginInterface(plugin.Plugin):
    """
    Plugin to watch tv with tvtime.
    """
    def __init__(self):
        plugin.Plugin.__init__(self)

        # get config locations and mod times so we can check if we need
        # to regen xml config files (because they changed)
        self.mylocalconf = self.findLocalConf()
        self.myfconfig = os.environ['FREEVO_CONFIG']
        self.tvtimecache = os.path.join(config.FREEVO_CACHEDIR, 'tvtimecache')
        self.mylocalconf_t = os.path.getmtime(self.mylocalconf)
        self.myfconfig_t = os.path.getmtime(self.myfconfig)
        self.major = 0
        self.minor = 0
        self.minorversion = 0

        self.getTvtimeVersion()
        self.xmltv_supported = self.isXmltvSupported()
        self.optionD_supported = self.isOptionDSupported()

        #check/create the stationlist.xml and tvtime.xml
        self.createTVTimeConfig()

        # create the tvtime object and register it
        plugin.register(TVTime(), plugin.TV)
        plugin.getbyname(plugin.TV).optionD_supported = self.optionD_supported
        plugin.getbyname(plugin.TV).xmltv_supported = self.xmltv_supported

    def getTvtimeVersion(self):
        helpcmd = '%s --help' %  config.TVTIME_CMD
        child = popen2.Popen3( helpcmd, 1, 100)
        data = child.childerr.readline() # Just need the first line
        if data:
            data = re.search( "^(tvtime: )?Running tvtime (?P<major>\d+).(?P<minor>\d+).(?P<version>\d+).", data )
            if data:
                _debug_("major is: %s" % data.group( "major" ))
                _debug_("minor is: %s" % data.group( "minor" ))
                _debug_("version is: %s" % data.group( "version" ))
                self.major = int(data.group( "major" ))
                self.minor = int(data.group( "minor" ))
                self.minorversion = int(data.group( "version" ))
        child.wait()

    def isXmltvSupported(self):
        has_xmltv=False
        if self.major > 0:
            has_xmltv=True
        elif self.major == 0 and self.minor == 9 and self.minorversion >= 10:
            has_xmltv=True
        return has_xmltv
 
    def isOptionDSupported(self):
        has_D=False
        if self.major == 0 and self.minor == 9 and self.minorversion < 13:
            has_D=True
        return has_D

    def findLocalConf(self):
        cfgfilepath = [ '.', os.path.expanduser('~/.freevo'), '/etc/freevo' ]
        mylocalconf = ''
        for dir in cfgfilepath:
            mylocalconf = os.path.join(dir,'local_conf.py')
            if os.path.isfile(mylocalconf):
                break
        return mylocalconf

    def createTVTimeConfig(self):
        tvtimedir = os.path.join(os.environ['HOME'], '.tvtime')
        if not os.path.isdir(tvtimedir):
            os.mkdir(tvtimedir)
        if self.needNewConfigs():
            self.writeStationListXML()
            self.writeTvtimeXML()
            self.writeMtimeCache()

    def needNewConfigs(self):
        tvtimedir = os.path.join(os.environ['HOME'], '.tvtime')
        if not os.path.isfile(os.path.join(tvtimedir, 'stationlist.xml')):
            return 1

        if not os.path.isfile(os.path.join(tvtimedir, 'tvtime.xml')):
            return 1

        if not os.path.isfile(self.tvtimecache):
            _debug_('no cache file')
            return 1

        (cachelconf, cachelconf_t, cachefconf_t) = self.readMtimeCache()

        cachelconf = cachelconf.rstrip()
        cachelconf_t = cachelconf_t.rstrip()
        cachefconf_t = cachefconf_t.rstrip()

        if not (cachelconf == self.mylocalconf): 
            _debug_('local_conf changed places')
            return 1

        if (long(self.mylocalconf_t) > long(cachelconf_t)):
            _debug_('local_conf modified')
            return 1

        if (long(self.myfconfig_t) > long(cachefconf_t)):
            _debug_('fconfig modified')
            return 1
        return 0

    def readMtimeCache(self):
        return file(self.tvtimecache, 'rb').readlines()

    def writeMtimeCache(self):
        fp = open(self.tvtimecache, 'wb')
        fp.write(self.mylocalconf)
        fp.write('\n')
        fp.write(str(self.mylocalconf_t))
        fp.write('\n')
        fp.write(str(self.myfconfig_t))
        fp.write('\n')
        fp.close()

    def writeTvtimeXML(self):
        tvtimexml = os.path.join(os.environ['HOME'], '.tvtime', 'tvtime.xml')
        configcmd = os.path.join(os.path.dirname(config.TVTIME_CMD), "tvtime-configure")
        #cf_norm, cf_input, cf_clist, cf_device = config.TV_SETTINGS.split()
        fc = FreevoChannels()
        vg = fc.getVideoGroup(config.TV_CHANNELS[0][2], True)
        cf_norm = vg.tuner_norm
        cf_input = vg.input_num
        cf_device = vg.vdev
        s_norm = cf_norm.upper()
        daoptions = ''
        if os.path.isfile(tvtimexml):
            daoptions = ' -F ' + tvtimexml
        if self.xmltv_supported:
            daoptions += ' -d %s -n %s -t %s' % (cf_device, s_norm, config.XMLTV_FILE)
        else:
            daoptions += ' -d %s -n %s' % (cf_device, s_norm)
        if hasattr(config, "TV_TVTIME_SETUP_OPTS") and config.TV_TVTIME_SETUP_OPTS:
            daoptions += ' %s' % config.TV_TVTIME_SETUP_OPTS
        os.system(configcmd+daoptions)

    def writeStationListXML(self):
        self.createChannelsLookupTables()
        norm='freevo'
        tvnorm = config.CONF.tv
        tvnorm = tvnorm.upper()
        tvtimefile = os.path.join(os.environ['HOME'], '.tvtime', 'stationlist.xml')
        if os.path.isfile(tvtimefile):
            self.mergeStationListXML(tvtimefile, tvnorm, norm)
        else:
            self.writeNewStationListXML(tvtimefile, tvnorm, norm)

    def mergeStationListXML(self, tvtimefile, tvnorm, norm):
        _debug_("merging stationlist.xml")
        try:
            os.rename(tvtimefile,tvtimefile+'.bak')
        except OSError:
            return

        reader = Sax2.Reader()
        doc = reader.fromStream(tvtimefile+'.bak')
        mystations = doc.getElementsByTagName('station')
        gotlist = 0
        freevonode = None
        for station in mystations:
            myparent = station.parentNode
            if myparent.getAttribute('norm') == tvnorm and myparent.getAttribute('frequencies') == 'freevo':
                myparent.removeChild(station)
                freevonode = myparent
                gotlist=1
        if not gotlist:
            child = doc.createElement('list')
            freevonode = child
            child.setAttribute('norm', tvnorm)
            child.setAttribute('frequencies', 'freevo')
            doc.documentElement.appendChild(child)
        #put in the new children
        c = 0
        for m in config.TV_CHANNELS:
            mychan = m[2]
            myband = self.lookupChannelBand(mychan)
            if myband == "Custom":
                mychan = config.FREQUENCY_TABLE.get(mychan)
                mychan = float(mychan)
                mychan = mychan / 1000.0
                mychan = "%.2fMHz" % mychan
            if (hasattr(config, 'TV_PAD_CHAN_NUMBERS') and config.TV_PAD_CHAN_NUMBERS and re.search('^\d+$', mychan)):
                for i in range(c,int(mychan)):
                    fchild =  doc.createElement('station')
                    fchild.setAttribute('channel',str(i))
                    fchild.setAttribute('band',myband)
                    fchild.setAttribute('name',str(i))
                    fchild.setAttribute('active','0')
                    fchild.setAttribute('position',str(i))
                    freevonode.appendChild(fchild)
                    c = c + 1
            fchild =  doc.createElement('station')
            fchild.setAttribute('channel',mychan)
            fchild.setAttribute('band',myband)
            fchild.setAttribute('name',cgi.escape(m[1]))
            fchild.setAttribute('active','1')
            fchild.setAttribute('position',str(c))
            if self.xmltv_supported:
                fchild.setAttribute('xmltvid',m[0])
            freevonode.appendChild(fchild)
            c = c + 1
        # YUCK:
        # PrettyPrint the results to stationlistxml unfortuneately it
        # adds a bunch of stuff in comments at the end of the file
        # that causes the document not to load if we merge again later
        # so I print to a string buffer and then remove the offending
        # comments by truncating the output.
        strIO = StringIO()
        PrettyPrint(doc, strIO)
        mystr = strIO.getvalue()
        myindex = mystr.find('</stationlist>')
        mystr = mystr[:myindex+15]
        # how can 4suite be so stupid and still survive?
        mystr = mystr.replace('<!DOCTYPE stationlist PUBLIC "http://tvtime.sourceforge.net/DTD/stationlist1.dtd" "-//tvtime//DTD stationlist 1.0//EN">','<!DOCTYPE stationlist PUBLIC "-//tvtime//DTD stationlist 1.0//EN" "http://tvtime.sourceforge.net/DTD/stationlist1.dtd">')
        fp = open(tvtimefile,'wb')
        fp.write(mystr)
        fp.close()


    def writeNewStationListXML(self, tvtimefile, tvnorm, norm):
        _debug_("writing new stationlist.xml")
        fp = open(tvtimefile,'wb')
        fp.write('<?xml version="1.0"?>\n')
        fp.write('<!DOCTYPE stationlist PUBLIC "-//tvtime//DTD stationlist 1.0//EN" "http://tvtime.sourceforge.net/DTD/stationlist1.dtd">\n')
        fp.write('<stationlist xmlns="http://tvtime.sourceforge.net/DTD/">\n')
        fp.write('  <list norm="%s" frequencies="%s">\n' % (tvnorm, norm))

        c = 0
        for m in config.TV_CHANNELS:
            mychan = str(m[2])
            myband = self.lookupChannelBand(mychan)
            if myband == "Custom":
                mychan = config.FREQUENCY_TABLE.get(mychan)
                mychan = float(mychan)
                mychan = mychan / 1000.0
                mychan = "%.2fMHz" % mychan
            if (hasattr(config, 'TV_PAD_CHAN_NUMBERS') and config.TV_PAD_CHAN_NUMBERS and re.search('^\d+$', mychan)):
                for i in range(c,int(mychan)):
                    fp.write('    <station name="%s" active="0" position="%s" band="%s" channel="%s"/>\n' % (i,i,myband,i))
                    c = c + 1
            if self.xmltv_supported:
                fp.write('    <station name="%s" xmltvid="%s" active="1" position="%s" band="%s" channel="%s"/>\n' % (cgi.escape(m[1]), m[0], c, myband, mychan))
            else:
                fp.write('    <station name="%s" active="1" position="%s" band="%s" channel="%s"/>\n' % (cgi.escape(m[1]),c,myband,mychan))
            c = c + 1

        fp.write('  </list>\n')
        fp.write('</stationlist>\n')
        fp.close()

    def lookupChannelBand(self, channel):
        # check if we have custom
       
        #Aubin's auto detection code works only for numeric channels and
        #forces them to int.
        channel = str(channel)
       
        if config.FREQUENCY_TABLE.has_key(channel):
            _debug_("have a custom")
            return "Custom"
        elif (re.search('^\d+$', channel)):
            _debug_("have number")
        if self.chanlists.has_key(config.CONF.chanlist):
            _debug_("found chanlist in our list")
            return self.chanlists[config.CONF.chanlist]
        elif self.chans2band.has_key(channel):
            _debug_("We know this channels band.")
            return self.chans2band[channel]
        _debug_("defaulting to USCABLE")
        return "US Cable"

    def createChannelsLookupTables(self):
        chanlisttmp = [ ('us-bcast', 'US Broadcast'), ('us-cable', 'US Cable'), ('us-cable-hrc', 'US Cable'), ('japan-cable', 'Japan Cable'), ('japan-bcast', 'Japan Broadcast'), ('china-bcast', 'China Broadcast') ]
        self.chanlists = dict(chanlisttmp)
        chans_list = [('T' + str(x), 'US Two-Way') for x in range(7, 15)]
        chans_list += [('A' + str(x), 'China Broadcast') for x in range(1, 8)]
        chans_list += [('B' + str(x), 'China Broadcast') for x in range(1, 32)]
        chans_list += [('C' + str(x), 'China Broadcast') for x in range(1, 6)]
        chans_list += [('E' + str(x), 'VHF E2-E12') for x in range(1, 13)]
        chans_list += [('S' + str(x), 'VHF S1-S41') for x in range(1, 42)]
        chans_list += [('Z+1', 'VHF Misc'), ('Z+2', 'VHF Misc')]
        chans_list += [(chr(x), 'VHF Misc') for x in range(88, 91)]
        chans_list += [('K%0.2i' % x, 'VHF France') for x in range(1, 11)]
        chans_list += [('H%0.2i' % x, 'VHF France') for x in range(1, 20)]
        chans_list += [('K' + chr(x), 'VHF France') for x in range(66, 82)]
        chans_list += [('SR' + str(x), 'VHF Russia') for x in range(1, 20)]
        chans_list += [('R' + str(x), 'VHF Russia') for x in range(1, 13)]
        chans_list += [('AS5A', 'VHF Australia'), ('AS9A', 'VHF Australia')]
        chans_list += [('AS' + str(x), 'VHF Australia') for x in range(1, 13)]
        chans_list += [('H1', 'VHF Italy'), ('H2', 'VHF Italy')]
        chans_list += [(chr(x), 'VHF Italy') for x in range(65, 73)]
        chans_list += [('I' + str(x), 'VHF Ireland') for x in range(1, 10)]
        chans_list += [('U' + str(x), 'UHF') for x in range(21, 70)]
        chans_list += [('AU' + str(x), 'UHF Australia') for x in range(28, 70)]
        chans_list += [('O' + str(x), 'Australia Optus') for x in range(1, 58)]
        self.chans2band=dict(chans_list)


class TVTime:

    __muted    = 0
    __igainvol = 0
    
    def __init__(self):
        self.app_mode = 'tv'
        self.fc = FreevoChannels()
        self.current_vg = None
        self.optionD_supported = False
        self.xmltv_supported = False

    def TunerSetChannel(self, tuner_channel):
        for pos in range(len(config.TV_CHANNELS)):
            channel = config.TV_CHANNELS[pos]
            if channel[2] == tuner_channel:
                return pos
        print 'ERROR: Cannot find tuner channel "%s" in the TV channel listing' % tuner_channel
        return 0

    def TunerGetChannelInfo(self):
        return self.fc.getChannelInfo()

    def TunerGetChannel(self):
        return self.fc.getChannel()

    def Play(self, mode, tuner_channel=None, channel_change=0):

        if not tuner_channel:
            tuner_channel = self.fc.getChannel()
        vg = self.current_vg = self.fc.getVideoGroup(tuner_channel, True)

        if not vg.group_type == 'normal':
            print 'Tvtime only supports normal. "%s" is not implemented' % vg.group_type
            return

        if mode == 'tv' or mode == 'vcr':
            
            w, h = config.TV_VIEW_SIZE
            cf_norm = vg.tuner_norm
            cf_input = vg.input_num
            cf_device = vg.vdev

            s_norm = cf_norm.upper()

            outputplugin = ''
            if plugin.getbyname(plugin.TV).optionD_supported:
                if config.CONF.display == 'x11':
                    outputplugin = 'Xv'
                elif config.CONF.display == 'mga':
                    outputplugin = 'mga'
                elif config.CONF.display in ( 'directfb', 'dfbmga' ):
                    outputplugin = 'directfb'
                else:
                    outputplugin = config.CONF.display
                outputplugin = '-D %s' % outputplugin

            if mode == 'vcr':
                cf_input = '1'
            if hasattr(config, "TV_VCR_INPUT_NUM") and config.TV_VCR_INPUT_NUM:
                cf_input = config.TV_VCR_INPUT_NUM

            self.fc.chan_index = self.TunerSetChannel(tuner_channel)

            if hasattr(config, 'TV_PAD_CHAN_NUMBERS') and config.TV_PAD_CHAN_NUMBERS:
                mychan = tuner_channel
            else:
                mychan = self.fc.chan_index

            _debug_('starting channel is %s' % mychan)

            command = '%s %s -k -I %s -n %s -d %s -f %s -c %s -i %s' % (config.TVTIME_CMD,
                                                                   outputplugin,
                                                                   w,
                                                                   s_norm,
                                                                   cf_device,
                                                                   'freevo',
                                                                   mychan,
                                   cf_input)

            if osd.get_fullscreen() == 1:
                command += ' -m'
            else:
                command += ' -M'


        else:
            print 'Mode "%s" is not implemented' % mode  # BUG ui.message()
            return

        self.mode = mode

        mixer = plugin.getbyname('MIXER')

        # BUG Mixer manipulation code.
        # TV is on line in
        # VCR is mic in
        # btaudio (different dsp device) will be added later
        if mixer and config.MAJOR_AUDIO_CTRL == 'VOL':
            mixer_vol = mixer.getMainVolume()
            mixer.setMainVolume(0)
        elif mixer and config.MAJOR_AUDIO_CTRL == 'PCM':
            mixer_vol = mixer.getPcmVolume()
            mixer.setPcmVolume(0)

        # Start up the TV task
        self.app=TVTimeApp(command)        

        self.prev_app = rc.app() # ???
        rc.app(self)

        # Suppress annoying audio clicks
        time.sleep(0.4)
        # BUG Hm.. This is hardcoded and very unflexible.
        if mixer and mode == 'vcr':
            mixer.setMicVolume(config.VCR_IN_VOLUME)
        elif mixer:
            mixer.setLineinVolume(config.TV_IN_VOLUME)
            mixer.setIgainVolume(config.TV_IN_VOLUME)
            
        if mixer and config.MAJOR_AUDIO_CTRL == 'VOL':
            mixer.setMainVolume(mixer_vol)
        elif mixer and config.MAJOR_AUDIO_CTRL == 'PCM':
            mixer.setPcmVolume(mixer_vol)

        if DEBUG: print '%s: started %s app' % (time.time(), self.mode)
        
        
    def Stop(self, channel_change=0):
        mixer = plugin.getbyname('MIXER')
        if mixer and not channel_change:
            mixer.setLineinVolume(0)
            mixer.setMicVolume(0)
            mixer.setIgainVolume(0) # Input on emu10k cards.

        self.app.stop('quit\n')
        rc.app(self.prev_app)

    def eventhandler(self, event, menuw=None):
        _debug_('%s: %s app got %s event' % (time.time(), self.mode, event))
        if event == em.STOP or event == em.PLAY_END:
            self.Stop()
            rc.post_event(em.PLAY_END)
            return True
        
        elif event == em.TV_CHANNEL_UP or event == em.TV_CHANNEL_DOWN:
            if self.mode == 'vcr':
                return
             
            if event == em.TV_CHANNEL_UP:
                nextchan = self.fc.getNextChannel()
            elif event == em.TV_CHANNEL_DOWN:
                nextchan = self.fc.getPrevChannel()
            nextvg = self.fc.getVideoGroup(nextchan, True)
            _debug_("nextchan is %s" % nextchan)

            # XXX hazardous to your health. don't use tvtime with anything
            # other than one normal video_group.
            # we lose track of the channel index at some points and
            # chaos ensues
            #if self.current_vg != nextvg:
            #    self.Stop(channel_change=1)
            #    self.Play('tv', nextchan)
            #    return TRUE

            self.fc.chanSet(nextchan, True, app=self.app)
            #self.current_vg = self.fc.getVideoGroup(self.fc.getChannel(), True)

            # Go to the prev/next channel in the list
            if event == em.TV_CHANNEL_UP:
                self.app.write('CHANNEL_UP\n')
            else:
                self.app.write('CHANNEL_DOWN\n')

            return True
            
        elif event == em.TOGGLE_OSD:
            self.app.write('DISPLAY_INFO\n')
            return True
        
        elif event == em.OSD_MESSAGE:
            # XXX this doesn't work
            #self.app.write('display_message %s\n' % event.arg)
            #this does
            os.system('tvtime-command display_message \'%s\'' % event.arg)
            return True
       
        elif event == em.TV_SEND_TVTIME_CMD:
            os.system('tvtime-command %s' % event.arg)
            return True

        elif event in em.INPUT_ALL_NUMBERS:
            self.app.write('CHANNEL_%s\n' % event.arg)
        
        elif event == em.BUTTON:
            if event.arg == 'PREV_CH':
                self.app.write('CHANNEL_PREV\n')
                return True
            

        return False
        
            

# ======================================================================
class TVTimeApp(childapp.ChildApp2):
    """
    class controlling the in and output from the tvtime process
    """

    def __init__(self, (app)):
        childapp.ChildApp2.__init__(self, app, stop_osd=1)

    def stdout_cb(self, line):
        if not len(line) > 0: return
        # XXX Needed because tvtime grabs focus unless used with freevo -fs
        events = { 'n' : em.MIXER_VOLDOWN,
                   'm' : em.MIXER_VOLUP,
                   'c' : em.TV_CHANNEL_UP,
                   'v' : em.TV_CHANNEL_DOWN,
                   'Escape' : em.STOP,
                   'd' : em.TOGGLE_OSD,
                   '_' : em.Event(em.BUTTON, arg='PREV_CHAN'),
                   '0' : em.INPUT_0,
                   '1' : em.INPUT_1,
                   '2' : em.INPUT_2,
                   '3' : em.INPUT_3,
                   '4' : em.INPUT_4,
                   '5' : em.INPUT_5,
                   '6' : em.INPUT_6,
                   '7' : em.INPUT_7,
                   '8' : em.INPUT_8,
                   '9' : em.INPUT_9,
                   'F3' : em.MIXER_MUTE,
                   's' : em.STOP }

        if DEBUG: print 'TVTIME 1 KEY EVENT: "%s"' % str(list(line))
        if line == 'F10':
            if DEBUG: print 'TVTIME screenshot!'
            self.write('screenshot\n')
        elif line == 'z':
            if DEBUG: print 'TVTIME fullscreen toggle!'
            self.write('toggle_fullscreen\n')
            osd.toggle_fullscreen()
        else:
            event = events.get(line, None)
            if event is not None:
                rc.post_event(event)
                if DEBUG: print 'posted translated tvtime event "%s"' % event
            else:
                if DEBUG: print 'tvtime cmd "%s" not found!' % line
   
