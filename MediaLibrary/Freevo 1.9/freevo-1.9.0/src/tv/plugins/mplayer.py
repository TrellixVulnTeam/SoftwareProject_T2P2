# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# Plug-in to watch tv with mplayer.
# -----------------------------------------------------------------------
# $Id: mplayer.py 11531 2009-05-17 18:59:36Z duncan $
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


import time, os

import config
import util    # Various utilities
import osd     # The OSD class, used to communicate with the OSD daemon
import rc      # The RemoteControl class.
import event as em
import childapp # Handle child applications
import tv.epg_xmltv as epg # The Electronic Program Guide
from tv.channels import FreevoChannels
import tv.ivtv as ivtv
import plugin
import dialog
from dialog.display import AppTextDisplay



# Create the OSD object
osd = osd.get_singleton()

class PluginInterface(plugin.Plugin):
    """
    Plugin to watch tv with mplayer.
    """
    def __init__(self):
        plugin.Plugin.__init__(self)

        # create the mplayer object and register it
        plugin.register(MPlayer(), plugin.TV)


class MPlayer:
    __muted    = 0
    __igainvol = 0

    def __init__(self):
        self.tuner_chidx = 0    # Current channel, index into config.TV_CHANNELS
        self.app_mode = 'tv'
        self.fc = FreevoChannels()
        self.current_vg = None


    def Play(self, mode, tuner_channel=None):
        """ """
        _debug_('MPlayer.Play(mode=%r, tuner_channel=%r)' % (mode, tuner_channel), 2)
        # Try to see if the channel is not tunable
        try:
            channel = int(tuner_channel)
        except ValueError:
            channel = 0

        vg = self.current_vg = self.fc.getVideoGroup(tuner_channel, True)

        if not tuner_channel:
            tuner_channel = self.fc.getChannel()

        # Convert to MPlayer TV setting strings
        device = 'device=%s' % vg.vdev
        input = 'input=%s' % vg.input_num
        norm = 'norm=%s' % vg.tuner_norm

        w, h = config.TV_VIEW_SIZE
        outfmt = 'outfmt=%s' % config.TV_VIEW_OUTFMT

        # Build the MPlayer command line
        args = {
            'nice': config.MPLAYER_NICE,
            'cmd': config.MPLAYER_CMD,
            'vo': '-vo %s' % config.MPLAYER_VO_DEV,
            'vo_opts': config.MPLAYER_VO_DEV_OPTS,
            'vc': '',
            'ao': '-ao %s' % config.MPLAYER_AO_DEV,
            'ao_opts': config.MPLAYER_AO_DEV_OPTS,
            'default_args': config.MPLAYER_ARGS_DEF.split(),
            'mode_args': config.MPLAYER_ARGS.has_key(mode) and config.MPLAYER_ARGS[mode].split() or [],
            'geometry': (config.CONF.x or config.CONF.y) and '-geometry %d:%d' % (config.CONF.x, config.CONF.y) or '',
            'verbose': '',
            'dvd-device': '',
            'cdrom-device': '',
            'alang': '',
            'aid': '',
            'slang': '',
            'sid': '',
            'playlist': '',
            'field-dominance': '',
            'edl': '',
            'mc': '',
            'delay': '',
            'sub': '',
            'audiofile': '',
            'af': [],
            'vf': [],
            'tv': '',
            'url': '',
        }

        if mode == 'tv':
            if vg.group_type == 'ivtv':
                ivtv_dev = ivtv.IVTV(vg.vdev)
                ivtv_dev.init_settings()
                ivtv_dev.setinputbyname(vg.input_type)
                cur_std = ivtv_dev.getstd()
                import tv.v4l2
                try:
                    new_std = tv.v4l2.NORMS.get(vg.tuner_norm)
                    if cur_std != new_std:
                        ivtv_dev.setstd(new_std)
                except:
                    _debug_('Error! Videogroup norm value "%s" not from NORMS: %s' \
                        % (vg.tuner_norm,tv.v4l2.NORMS.keys()), DERROR)
                ivtv_dev.close()

                # Do not set the channel if negative
                if channel >= 0:
                    self.fc.chanSet(tuner_channel, True)

                args['url'] = vg.vdev

                if config.MPLAYER_ARGS.has_key('ivtv'):
                    args['mode_args'] = config.MPLAYER_ARGS['ivtv'].split()

            elif vg.group_type == 'webcam':
                self.fc.chanSet(tuner_channel, True, app='mplayer')
                args['url'] = ''

                if config.MPLAYER_ARGS.has_key('webcam'):
                    args['mode_args'] = config.MPLAYER_ARGS['webcam'].split()

            elif vg.group_type == 'dvb':
                self.fc.chanSet(tuner_channel, True, app='mplayer')
                args['url'] = ('dvb://%s' % (tuner_channel,))
                args['mode_args'] = config.MPLAYER_ARGS['dvb'].split()

            elif vg.group_type == 'tvalsa':
                freq_khz = self.fc.chanSet(tuner_channel, True, app='mplayer')
                tuner_freq = '%1.3f' % (freq_khz / 1000.0)

                args['tv'] = '-tv driver=%s:%s:freq=%s:%s:%s:%s:width=%s:height=%s:%s %s' % \
                    (config.TV_DRIVER, vg.adev, tuner_freq, device, input, norm, w, h, outfmt, config.TV_OPTS)
                args['url'] = 'tv://'

                if config.MPLAYER_ARGS.has_key('tv'):
                    args['mode_args'] = config.MPLAYER_ARGS['tv'].split()

            else: # group_type == 'normal'
                freq_khz = self.fc.chanSet(tuner_channel, True, app='mplayer')
                tuner_freq = '%1.3f' % (freq_khz / 1000.0)

                args['tv'] = '-tv driver=%s:freq=%s:%s:%s:%s:width=%s:height=%s:%s %s' % \
                    (config.TV_DRIVER, tuner_freq, device, input, norm, w, h, outfmt, config.TV_OPTS)
                args['url'] = 'tv://'

                if config.MPLAYER_ARGS.has_key('tv'):
                    args['mode_args'] = config.MPLAYER_ARGS['tv'].split()

        elif mode == 'vcr':
            args['tv'] = '-tv driver=%s:%s:%s:%s:width=%s:height=%s:%s %s' % \
                (config.TV_DRIVER, device, input, norm, w, h, outfmt, config.TV_OPTS)
            args['url'] = 'tv://'

            if config.MPLAYER_ARGS.has_key('tv'):
                args['mode_args'] = config.MPLAYER_ARGS['tv'].split()

        else:
            _debug_('Mode "%s" is not implemented' % mode, DERROR)
            return

        _debug_('mplayer args = %r' % (args,))

        vo = ['%(vo)s' % args, '%(vo_opts)s' % args]
        vo = filter(len, vo)
        vo = ':'.join(vo)

        ao = ['%(ao)s' % args, '%(ao_opts)s' % args]
        ao = filter(len, ao)
        ao = ':'.join(ao)

        command = ['--prio=%(nice)s' % args]
        command += ['%(cmd)s' % args]
        command += ['-slave']
        command += str('%(verbose)s' % args).split()
        command += str('%(geometry)s' % args).split()
        command += vo.split()
        command += str('%(vc)s' % args).split()
        command += ao.split()
        command += args['default_args']
        command += args['mode_args']
        command += str('%(dvd-device)s' % args).split()
        command += str('%(cdrom-device)s' % args).split()
        command += str('%(alang)s' % args).split()
        command += str('%(aid)s' % args).split()
        command += str('%(audiofile)s' % args).split()
        command += str('%(slang)s' % args).split()
        command += str('%(sid)s' % args).split()
        command += str('%(sub)s' % args).split()
        command += str('%(field-dominance)s' % args).split()
        command += str('%(edl)s' % args).split()
        command += str('%(mc)s' % args).split()
        command += str('%(delay)s' % args).split()
        if args['af']:
            command += ['-af', '%s' % ','.join(args['af'])]
        if args['vf']:
            command += ['-vf', '%s' % ','.join(args['vf'])]
        command += str('%(tv)s' % args).split()

        # use software scaler?
        if '-nosws' in command:
            command.remove('-nosws')
        elif '-framedrop' not in command:
            command += config.MPLAYER_SOFTWARE_SCALER.split()

        #if options:
        #    command += options

        command = filter(len, command)

        #command = self.sort_filter(command)

        url = '%(url)s' % args
        command += [url]

        _debug_('%r' % command)

        self.mode = mode


        # XXX Mixer manipulation code.
        # TV is on line in
        # VCR is mic in
        # btaudio (different dsp device) will be added later
        mixer = plugin.getbyname('MIXER')

        if mixer and config.MIXER_MAJOR_CTRL == 'VOL':
            mixer_vol = mixer.getMainVolume()
            mixer.setMainVolume(0)
        elif mixer and config.MIXER_MAJOR_CTRL == 'PCM':
            mixer_vol = mixer.getPcmVolume()
            mixer.setPcmVolume(0)

        # Start up the TV task
        self.app = childapp.ChildApp2(command)

        self.prev_app = rc.app()
        rc.app(self)

        if osd.focused_app():
            osd.focused_app().hide()

        # Suppress annoying audio clicks
        time.sleep(0.4)
        # XXX Hm.. This is hardcoded and very unflexible.
        if mixer and mode == 'vcr':
            mixer.setMicVolume(config.MIXER_VOLUME_VCR_IN)
        elif mixer:
            mixer.setLineinVolume(config.MIXER_VOLUME_TV_IN)
            mixer.setIgainVolume(config.MIXER_VOLUME_TV_IN)

        if mixer and config.MIXER_MAJOR_CTRL == 'VOL':
            mixer.setMainVolume(mixer_vol)
        elif mixer and config.MIXER_MAJOR_CTRL == 'PCM':
            mixer.setPcmVolume(mixer_vol)

        dialog.enable_overlay_display(AppTextDisplay(self.show_message))
        _debug_('%s: started %s app' % (time.time(), self.mode))



    def Stop(self, channel_change=0):
        mixer = plugin.getbyname('MIXER')
        if mixer and not channel_change:
            mixer.setLineinVolume(0)
            mixer.setMicVolume(0)
            mixer.setIgainVolume(0) # Input on emu10k cards.

        self.app.stop('quit\n')

        rc.app(self.prev_app)
        if osd.focused_app() and not channel_change:
            osd.focused_app().show()

        if os.path.exists('/tmp/freevo.wid'): os.unlink('/tmp/freevo.wid')

        if config.MPLAYER_OLDTVCHANNELCHANGE:
            lastchanfile = os.path.join(config.FREEVO_CACHEDIR, 'lastchan')
            lcfp = open(lastchanfile, "w")
            lastchan = self.fc.getChannel()
            lastchannum = self.fc.getChannelNum()
            lcfp.write(str(lastchan))
            lcfp.write('\n')
            lcfp.write(str(lastchannum))
            lcfp.write('\n')
            lcfp.close()

        dialog.disable_overlay_display()


    def eventhandler(self, event, menuw=None):
        s_event = '%s' % event

        if event == em.STOP or event == em.PLAY_END:
            self.Stop()
            rc.post_event(em.PLAY_END)
            return True

        elif event == em.PAUSE or event == em.PLAY:
            self.app.write('pause\n')
            _debug_('%s: sending pause to mplayer' % (time.time()))
            return True

        elif event in [ em.TV_CHANNEL_UP, em.TV_CHANNEL_DOWN, em.TV_CHANNEL_LAST ] or s_event.startswith('INPUT_'):
            chan = None
            if event == em.TV_CHANNEL_UP:
                nextchan = self.fc.getNextChannel()
                nextchannum = self.fc.getNextChannelNum()
            elif event == em.TV_CHANNEL_DOWN:
                nextchan = self.fc.getPrevChannel()
                nextchannum = self.fc.getPrevChannelNum()
            elif event == em.TV_CHANNEL_LAST:
                if config.MPLAYER_OLDTVCHANNELCHANGE:
                    if os.path.isfile(os.path.join(config.FREEVO_CACHEDIR, 'lastchan')):
                        lastchanfile = os.path.join(config.FREEVO_CACHEDIR, 'lastchan')
                        lcfp = open(lastchanfile, "r")
                        nextchan = lcfp.readline()
                        nextchan = nextchan.strip()
                        nextchannum = lcfp.readline()
                        nextchannum = nextchannum.strip()
                        nextchannum = int(nextchannum)
                        lcfp.close()
                    else:
                        nextchan = self.fc.getChannel()
                        nextchannum = self.fc.getChannelNum()
                else:
                    return True
            else:
                chan = int(s_event[6])
                nextchan = self.fc.getManChannel(chan)
                nextchannum = self.fc.getManChannelNum(chan)

            nextvg = self.fc.getVideoGroup(nextchan, True)
            _debug_('chan=%s, nextchannum=%s, nextchan=%s nextvg=%s' % (chan, nextchannum, nextchan, nextvg))

            if self.current_vg != nextvg:
                self.Stop(channel_change=1)
                self.Play('tv', nextchan)
                return True

            if self.mode == 'vcr':
                return

            elif self.current_vg.group_type == 'dvb':
                if not config.MPLAYER_OLDTVCHANNELCHANGE:
                    card = 0 # May be this should come from video groups or TV_CHANNELS
                    if em.TV_CHANNEL_UP:
                        self.app.write('dvb_set_channel %s %s\n' % (nextchannum, card))
                        self.fc.chanSet(nextchan, True)
                    elif em.TV_CHANNEL_DOWN:
                        self.app.write('dvb_set_channel %s %s\n' % (nextchannum, card))
                        self.fc.chanSet(nextchan, True)
                else:
                    self.Stop(channel_change=1)
                    self.Play('tv', nextchan)
                return True

            elif self.current_vg.group_type == 'ivtv':
                self.fc.chanSet(nextchan, True)
                self.app.write('seek 999999 0\n')

            else:
                freq_khz = self.fc.chanSet(nextchan, True, app=self.app)
                new_freq = '%1.3f' % (freq_khz / 1000.0)
                self.app.write('tv_set_freq %s\n' % new_freq)

            self.current_vg = self.fc.getVideoGroup(self.fc.getChannel(), True)

            # Display a channel changed message
            tuner_id, chan_name, prog_info = self.fc.getChannelInfo()
            now = time.strftime(config.TV_TIME_FORMAT)
            msg = '%s %s (%s): %s' % (now, chan_name, tuner_id, prog_info)
            cmd = 'osd_show_text "%s"\n' % msg
            self.app.write(cmd)
            return True

        elif event == em.TOGGLE_OSD:
            # Display the channel info message
            tuner_id, chan_name, prog_info = self.fc.getChannelInfo()
            now = time.strftime(config.TV_TIME_FORMAT)
            msg = '%s %s (%s): %s' % (now, chan_name, tuner_id, prog_info)
            cmd = 'osd_show_text "%s"\n' % msg
            self.app.write(cmd)
            return False

        elif event == em.OSD_MESSAGE:
            self.app.write('osd_show_text "%s"\n' % event.arg);
            return True

        elif event == em.TV_SEND_MPLAYER_CMD:
            self.app.write('%s\n' % event.arg);
            return True

        return False

    def show_message(self, message):
        self.app.write('osd_show_text "%s"\n' % message)
