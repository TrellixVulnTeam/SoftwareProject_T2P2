# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# cd_burn.py - Plugin for copying files to a cd
# -----------------------------------------------------------------------
# $Id: cd_burn.py 11523 2009-05-16 18:10:55Z duncan $
#
# Notes:
#
# And to activate:
# plugin.activate('cd_burn')
#
# CDBURN_AUDIO_DAO = 1
# CDBURN_MKISOFS_PATH = '/usr/bin/mkisofs'
# CDBURN_CDRECORD_PATH = '/usr/bin/cdrecord'
# CDBURN_TEMP_DIR='/tmp'
# CDBURN_DEV = '/dev/hdc'
# CDBURN_SPEED = 32
#
#    - You can now burn DVD Video from your rips
#    - BurnCD is now a sub menu
#    - Directory burning
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

import sys
import threading
import re
import shutil

import util.fileops
import plugin
import rc

import os

import string
import menu
import plugin
import time
import item
import re
import glob
import config
import popen2
import signal

import select
import fcntl

from gui.PopupBox import PopupBox
from gui.Button import Button
from gui.ProgressBox import ProgressBox
from gui.ConfirmBox import ConfirmBox
from gui.AlertBox import AlertBox
#from gui.YesNoBox import YesNoBox
from popen2 import Popen3, Popen4
#from os import *
from stat import *
#from os.path import *
from event import *


class MyProgressBox(ProgressBox):
    """
    """
    def __init__(self, text, x=None, y=None, width=0, height=0, icon=None,
        vertical_expansion=1, text_prop=None, full=0, parent='osd',
        handler=None, initial_progress=0):

        ProgressBox.__init__(self, text, x, y, width, height,
                 icon, vertical_expansion, text_prop, full, parent);

        b1 = Button(_('OK'))
        b1.toggle_selected()

        self.add_child(b1)

        self.progressbar.position = initial_progress


    def set_progress(self, progress):
        _debug_('set_progress(progress=%r)' % (progress,))
        while self.progressbar.position < progress:
            self.tick()


    def eventhandler(self, event):
        _debug_('eventhandler(event=%s)' % (event,))
        if event in (INPUT_ENTER, INPUT_EXIT):
            self.destroy()
            if self.handler:
                self.handler()
        else:
            return self.parent.eventhandler(event)



class Logger:
    """
    """
    def __init__(self):
        _debug_('cd_burn.Logger.__init__()')
        self.filename = '%s/%s-%s.log' % (config.FREEVO_LOGDIR, 'burn_cd-helpers', os.getuid())
        self.file     = file(self.filename, "a")


    def log(self, line=None):
        _debug_('log(line=%s)' % (line,), 2)
        self.file.write(line + "\n")
        self.file.flush()



class BurnCDItem:
    """
    """
    def __init__(self, item, filename=None, plugin=None, menu=None, burn_mode="data_cd"):
        _debug_('cd_burn.BurnCDItem.__init__(item, filename=None, plugin=None, menu=None, burn_mode="data_cd")')
        self.item        = item
        self.menuw       = menu
        self.plugin      = plugin
        self.files       = []
        self.volume_name = None
        self.burn_mode   = burn_mode
        self.burn_list   = os.path.join(config.CDBURN_TEMP_DIR, 'burnlist')


    def menu_back(self):
        """
        go back in menustack
        """
        _debug_('menu_back()')
        #for i in range(2):
        for i in range(1):
            self.menuw.back_one_menu(arg='reload')
        self.menuw.refresh


    def burn(self, arg=None, menuw=None):
        """
        starts de decision process of burning the CD
        """
        _debug_('burn(arg=%r, menuw=%r)' % (arg, menuw))
        if self.burn_mode == "data_cd":
            self.burn_data_cd()
        elif self.burn_mode == "dvd_video":
            self.burn_dvd_video()
        elif self.burn_mode == "audio_cd":
            self.burn_audio_cd()
        else:
            AlertBox(text=_('Not Yet implemented :)')).show()
            return


    def check_program(self, program=None, program_name=None):
        """
        checks if the file "program" with the program name exists and is
        executable if not displays a alert box and returns 0
        """
        _debug_('check_program(program=%r, program_name=%r)' % (program, program_name))
        if not (os.path.exists(program) and os.path.isfile(program) and os.access(program, os.X_OK)):
            _debug_("Program Error")
            AlertBox(text=_('Cannot find %(program_name)s (%(program)s). '+\
                'Please configure the right path in your config file and make sure it has the right permissions.' % ({
                    'program_name': program_name, 'program': program})), handler=self.menu_back).show()
            return 0
        else:
            return 1


    def burn_audio_cd(self):
        """
        Checks for burn list clean-up, mplayer availability
        """
        _debug_('burn_audio_cd()')
        if not self.check_program(program=config.MPLAYER_CMD, program_name="mplayer"):
            return

        if not self.clean_up_burndir():
            return

        ConfirmBox(text=_('Start burning %s audio files?') % len(self.files),
            handler=self.start_burning, default_choice=0).show()


    def burn_dvd_video(self):
        """
        Copy this file/DIR to DVD as DVD VIDEO, NB: MUST BE DVD VIDEO
        ALREADY!!!!!!! (i.e. ripped with dvdcopy.py)
        """
        _debug_('burn_dvd_video()')

        self.file_to_burn=None
        name  = self.files[0].split("/")
        self.name  = name[len(name) -1]
        _debug_('self.name = %s' % self.name)
        self.dir = self.files[0]
        _debug_('self.dir = %s ' % self.dir)
        if self.name.endswith('.iso'):
            self.file_to_burn=self.dir
        else:
            self.subdirs = util.getdirnames(self.dir, softlinks=False)
            for dir in self.subdirs:
                pathname = os.path.join(self.dir, dir)
                _debug_('%s ' % pathname[-3:])
                if pathname[-3:].lower() == '_ts':
                    _debug_('OK TO BURN, folder DVD compliant %s' %pathname)
                    self.file_to_burn = pathname
                else:
                    _debug_('NOT OK to BURN, folder NOT DVD compliant: %s' % pathname)
                    self.file_to_burn = None

        if self.file_to_burn:
            ConfirmBox(text=_('Insert media then click OK'),
                             handler=self.start_burning, default_choice=0
                             ).show()
        return

        self.burn()


    def burn_data_cd(self):
        """
        Asks confirmation for the burning of a data CD if confirmation given it
        calls start_burning
        """
        _debug_('burn_data_cd()')
        #lets check if we have all we need
        if not self.check_program(program=config.CDBURN_CDRECORD_PATH, program_name="cdrecord"):
            _debug_("Unable to find %s" %config.CDBURN_CDRECORD_PATH)
            return
        if not self.check_program(program=config.CDBURN_MKISOFS_PATH,  program_name="mkisofs"):
            _debug_("Unable to find %s" %config.CDBURN_MKISOFS_PATH)
            return

        if not self.clean_up_burndir():
            return

        #if list of files not to big just display it
        if len(self.files) <= 4:
            ConfirmBox(text=_('Start burning %s ?') % self.files,
                       handler=self.start_burning, default_choice=0).show()
        #else display the size of the burning
        else:
            t_sum = 0
            t_files = len(self.files)
            for a in self.files:
                c = os.stat(a)[ST_SIZE]
                t_sum = t_sum + (int(c)/1024/1024)

            ConfirmBox(text=_('Start burning %(num)s entries? ( %(size)d Mb )') % ({
                'num': t_files, 'size': t_sum}), handler=self.start_burning, default_choice=0).show()


    def clean_up_burndir(self):
        """
        Tries to clean-up /tmp/burndir, if it not exists then try to create it
        the final result of this function must a be a existing and empty
        /tmp/burnlist
        """
        _debug_('clean_up_burndir()')
        try:
            _debug_('in Try 2');
            if not os.stat(self.burn_list):
                _debug_('in if 2');
                os.makedirs(self.burn_list, 0777)
            else:
                _debug_('in else 2');
                if os.listdir(self.burn_list):
                    os.system('rm -rf %s' % os.path.join(self.burn_list, '*'))
        except:
            _debug_('in except 2');
            os.makedirs(self.burn_list, 0777)
            os.system('rm -rf %s' % os.path.join(self.burn_list, '*'))

        try:
            _debug_('in Try 1');
            if os.stat(self.burn_list):
                _debug_('in if 1');
                for a in os.listdir(self.burn_list):
                    os.unlink(os.path.join(self.burn_list, a))
        except:
            _debug_('in except 1');
            AlertBox(text='Aborted, could not empty %s' % self.burn_list)
            _debug_('clean_up_burndir end1');
            return 0

        _debug_('clean_up_burndir end');
        return 1


    def start_burning(self, arg=None, menuw=None):
        """
        Starts the burning thread
        """
        _debug_('start_burning(arg=%r, menuw=%r)' % (arg, menuw))
        self.thread_burn = MainBurnThread(token=self)
        self.thread_burn.start()
        self.plugin.thread_burn = self.thread_burn
        self.menu_back()


    #
    # Routines to find files for burning
    #
    def findFileFromItem(self):
        """Finds the file of a single file item"""
        _debug_('findFileFromItem()')
        if self.item.filename:
            _debug_('findFileFromItem() found item %s' % (self.item.filename,))
            self.volume_name = self.item.name
            self.files.append(self.item.filename)


    def findFromDir(self):
        """Finds all the files in a directory item"""
        _debug_('findFromDir()')
        for f in os.listdir(self.item.dir) :
            self.files.append(self.item.dir+'/'+f)


    def findFromPlaylist(self) :
        """Adds all files in a play-list to self's list of files to burn"""
        _debug_('findFromPlaylist(): %s' % (self.item.filename,))
        f = open(self.item.filename)
        try:
            for line in f:
                self.files.append(line.rstrip("\n"))
        finally:
            f.close()


    def findRelated(self, mode=0):
        """
        Finds files from item and related. Related files have the same file name
        that the item file name but different extensions
        """
        _debug_('findRelated(mode=%r)' % (mode,))
        self.files.append(self.item.filename)
        file = self.item.filename
        self.volume_name = self.item.name

        rexp = re.compile('(.*)/(.*)\.(.*)')
        result = rexp.search(file)
        name = result.group(2)
        dir = result.group(1)
        _debug_('File: %s, Name: %s, Dir: %s' % (file, name, dir))
        files = glob.glob( dir + '/' + name + '.*' )
        for k in files:
            if k == file:
                continue
            result = rexp.search(k)
            ext = result.group(3)

            if mode==0 and (ext == 'fxd' or ext == 'jpg'):
                continue

            _debug_('related file: ' + k)
            _debug_('extension ' + ext)
            self.files.append(k)


    def findFromDirMatches(self, suffix=None):
        """finds all files in a dir matching suffix"""
        _debug_('findFromDirMatches(suffix=%r)' % (suffix,))
        if not suffix:
            return
        matches = util.match_files(dirname=self.item.dir, suffix_list=suffix)
        self.files = matches



class MainBurnThread(threading.Thread):
    """
    Thread that really burns the CD
    """
    def __init__(self, token=None):
        _debug_('cd_burn.MainBurnThread.__init__(token=%r)' % (token,))
        threading.Thread.__init__(self)
        self.token  = token
        self.childs = []

        #process progress and status
        self.running  = 0
        self.progress = 0
        self.status   = ""
        self.stopping = False

        self.logger   = Logger()

        #widget to display the status
        self.widget = False


    def stop(self):
        _debug_('stop()')
        self.stopping = True
        starttime = time.time()

        while self.stopping and (time.time() - starttime < 15):
            _debug_('Waiting for the thread to terminate...')
            time.sleep(1)


    def cleanup(self):
        _debug_('cleanup()')
        for child in self.childs:
            if child.poll() == 0:
                continue
            try:
                _debug_('killing process group %d with signal 15' % (child.pid))
                os.kill(-child.pid, signal.SIGTERM)
            except OSError:
                print 'killing process group %d FAILED' % (child.pid)
                pass

            for i in range(20):
                #_debug_('Waiting for process group %d to terminate...' % (child.pid))
                try:
                    p,s = os.waitpid((-child.pid), os.WNOHANG)
                except OSError:
                    _debug_('Process group %d exited' % (child.pid))
                    break
                if p == child.pid:
                    _debug_('Process group %d terminated with signal 15' % child.pid)
                    break
                time.sleep(0.1)
            else:
                try:
                    _debug_('killing process group %d with signal 9' % (child.pid))
                    os.kill(-child.pid, signal.SIGKILL)
                except OSError:
                    _debug_('killing process group %d FAILED' % (child.pid))
                    pass
                for i in range(20):
                    #_debug_('Waiting for process group %d to terminate...' % (child.pid))
                    try:
                        p,s = os.waitpid(-child.pid, os.WNOHANG)
                    except OSError:
                        _debug_('Process group %d exited' % (child.pid))
                        break
                    if p == child.pid:
                        _debug_('Process group %d terminated with signal 9' % child.pid)
                        break
                    time.sleep(0.1)

            self.update_status(status='error', description='Aborted by user')


    def run_child(self, cmd=None, cwd=None, wait=0, task_weight=False):
        """
        Spawns a child using command cmd.

        If cwd is filled the os will change to that dir before the spawning

        If wait is 1 (or True), this function will wait for child "death"
        before returning

        This function returns the child object, if it does not return any
        value, the process was aborted.

        If task_weight is passed, when the child exits the progress is
        incremented by the task_wight
        """
        _debug_('run_child(cmd=%r, cwd=%r, wait=%r, task_weight=%r)' % (cmd, cwd, wait, task_weight))
        if cwd:
            _debug_("Changing working dir to %s" % cwd)
            os.chdir(cwd)

        cmd = cmd + " 2>&1"

        child_app = util.popen3.Popen4(cmd)

        self.logger.log(cmd)
        self.childs.append(child_app)

        if wait:
            _debug_('Waiting for %s' % child_app.pid)

            self.makeNonBlocking(child_app.fromchild.fileno())

            while child_app.poll() < 0:
                #_debug_("Polled %s (pid : %s), status is %s" % (cmd, child_app.pid, child_app.poll()))
                if self.stopping:
                    self.cleanup()
                    self.stopping = False
                    return

                try:
                    """
                    This allow us to parse the output of the commands,
                    its a approach to the status bar
                    """
                    while 1:
                        line = child_app.fromchild.readline()
                        if line:
                            pass
                            self.logger.log(line[0:-1])
                            #TODO, call the parser to get the progress
                        else:
                            break
                except IOError:
                    #the fd was not ready to read
                    pass

                #_debug_('string = %s' % last_string )

                time.sleep(1)

            _debug_('%s exited with code %s' % (cmd, child_app.poll()))
            if task_weight:
                self.progress = self.progress + task_weight
                self.update_progress(self.progress)
            if self.stopping:
                self.cleanup()
                self.stopping = False
                return
        return child_app


    def makeNonBlocking(self, fd):
        _debug_('makeNonBlocking(fd=%s)' % (fd,))
        fl = fcntl.fcntl(fd, fcntl.F_GETFL)
        try:
            fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NDELAY)
        except AttributeError:
            fcntl.fcntl(fd, fcntl.F_SETFL, fl | fcntl.FNDELAY)


    def show_status(self, arg=None, menuw=None):
        """
        The thread has is own status widget
        """
        _debug_('show_status(arg=%r, menuw=%r)' % (arg, menuw))
        self.widget = MyProgressBox(text=_('Burning status: %s' % Unicode(self.status)),
            handler=self.hide_status, full=100, initial_progress=self.progress)
        self.widget.show()


    def hide_status(self, arg=None, menuw=None):
        _debug_('hide_status(arg=%r, menuw=%r)' % (arg, menuw))
        w = self.widget;
        self.widget = False;
        if w:
            w.destroy


    def update_progress(self, progress=0):
        _debug_('update_progress(progress=%r)' % (progress,))
        self.progress=progress
        if self.widget:
            self.widget.set_progress(progress)
            self.widget.draw(update=True)


    def update_status(self, status='running', description=None):
        """
        Is used to change the status of the process.
        The status can be: running, error, done
        The description should be a string describing the status of the process.
        """
        _debug_('update_status(status=%r, description=%r)' % (status, description))
        if status == 'error':
            self.status  = "Error : " + description
            self.running = 0
            self.elapsed = (time.time() - self.starttime)
            self.progress=100
        elif status == 'running':
            if self.running == 0:
                #first time running is called
                self.running = 1
                self.starttime = time.time()
            self.status  = description
        elif status == 'done':
            self.running = 0
            self.elapsed = (time.time() - self.starttime)
            self.status = description or "Burn successful (in %s sec)" % self.elapsed
            _debug_("CD_BURN : " + self.status)
            self.progress=100

        if self.widget:
            _debug_("Updating")
            self.widget.set_progress(self.progress)
            self.widget.label.set_text(self.status)
            self.widget.draw(update=True)


    def run(self, arg=None, menuw=None, token=None):
        """
        Starts the burning process and helpers
        """
        _debug_('run(arg=%r, menuw=%r, token=%r)' % (arg, menuw, token))

        _debug_('running burning thread with token.burn_mode = %s' % self.token.burn_mode)
        image_file = os.path.join(config.CDBURN_TEMP_DIR, 'image.iso')

        if self.token.burn_mode == "data_cd":
            self.update_status(status="running", description="Creating disc image")
            # Links the files to Burn in burn_list directory

            for a in self.token.files:
                path = re.split("\\/", a)
                os.symlink(a, os.path.join(self.token.burn_list, path[-1]))

            _debug_("start burning")

            # copy files into a CD
            if not self.token.volume_name:
                self.token.volume_name = self.token.item.type

            mkisofs_cmd = '%s -f -U -V "%s" -o %s %s' % \
                (config.CDBURN_MKISOFS_PATH, self.token.volume_name[:16], image_file, self.token.burn_list)
            child = self.run_child(cmd=mkisofs_cmd, wait=1, task_weight=50)
            if not child:
                return

            if child.poll() != 0:
                self.update_status(status="error", description="Could not create the image file")
                return

            _debug_('Mkisofs done')
            self.status = "Burning files to CD"

            cdrecord_cmd = '%s -eject -v -driveropts=burnfree speed=%s dev=%s %s' % \
                (config.CDBURN_CDRECORD_PATH, config.CDBURN_SPEED, config.CDBURN_DEV, image_file)

            rec_child = self.run_child(cmd=cdrecord_cmd, wait=1, task_weight=50)

            if not rec_child:
                return

            if rec_child.poll() != 0:
                self.update_status(status='error', description='Could not burn image file to CD');
                return

            os.unlink(image_file)

        elif self.token.burn_mode == "dvd_video":
            #set command for VITEO_TS type DVD's
            growisofs_cmd = '%s -use-the-force-luke -dvd-compat -Z /dev/dvd -V "%s" -dvd-video "%s"' \
                % (config.CDBURN_GROWISOFS_PATH, self.token.name[:16], self.token.dir)

            if self.token.name.endswith('.iso'):
                if config.CDBURN_DVDISO_USE_GROWISOFS:
                    growisofs_cmd = '%s -use-the-force-luke -dvd-compat -Z /dev/dvd="%s"' \
                     % (config.CDBURN_GROWISOFS_PATH, self.token.dir)
                else:
                    growisofs_cmd = '%s -s -eject -v -driveropts=burnfree speed=%s dev=%s "%s"' \
                    % (config.CDBURN_CDRECORD_PATH, config.CDBURN_DVD_BURN_SPEED, config.CDBURN_DEV, self.token.dir)

            _debug_('growisofs command = %r' % growisofs_cmd)

            self.update_status(status='running', description='Burning DVD Video');
            burn_child = self.run_child(cmd=growisofs_cmd, wait=1, task_weight=100)
            if (not burn_child):
                return

            if burn_child.poll() != 0:
                self.update_status(status="error", description="Could not burn DVD")
                return

                #rc.register(self.burn_status, False, 2000)

        elif self.token.burn_mode == "audio_cd":
            #All tracks are about 70% of the total process percentage
            track_percent = 70/len(self.token.files);
            for a in self.token.files:
                status_line = "Converting %s" % os.path.basename(a)
                self.update_status(status='running', description=status_line)

                _debug_("Converting %s" % os.path.basename(a))
                convert_cmd = 'mplayer -ao pcm:waveheader -vc null -vo null "%s"' % a

                conv_child = self.run_child(cmd=convert_cmd, cwd=self.token.burn_list, wait=1,
                    task_weight=track_percent)
                if not conv_child:
                    return

                if conv_child.poll() != 0:
                    self.update_status(status="error",
                        description=_("Error : Could not convert %s" % os.path.basename(a)))
                    return

                _debug_("Conversion done")
                rename_wav = '%s.wav' % (config.os.path.basename(a))
                os.rename(os.path.join(self.token.burn_list, 'audiodump.wav'),
                    os.path.join(self.token.burn_list, Unicode(rename_wav)))

            self.update_status(status='running', description="Burning Audio to CD")
            audio_mode = config.CDBURN_AUDIO_DAO;
            if audio_mode == 1:
                audio_mode = "-dao"
            else:
                audio_mode = ""
            cdrec_cmd = '%s -audio -s -eject -v -driveropts=burnfree speed=%s dev=%s %s -pad -useinfo %s' % (
                config.CDBURN_CDRECORD_PATH, config.CDBURN_SPEED, config.CDBURN_DEV, audio_mode,
                os.path.join(self.token.burn_list, '*'))
            _debug_('%s' % cdrec_cmd)

            rec_child = self.run_child(cmd=cdrec_cmd, wait=1)
            if not rec_child:
                return

            if rec_child.poll() != 0:
                self.update_status(status="error", description='Could burn audio tracks to CD')
                return

        #lets wait for all childs to stop
        for child in self.childs:
            while child.poll() < 0:
                child.fromchild.readlines()
                _debug_('Waiting for process %d...' % child.pid)
                time.sleep(1)

        self.update_status(status='done');
        return


class PluginInterface(plugin.ItemPlugin):
    """
    Enables writing selected item to compatable device.  So far we can burn
    files to cd, DVD (VIDEO_TS) to video dvd, and files (mp3 and Ogg) to
    Audio cd.

    Place cd_burn.py in:
    freevo/plugins/.

    Activate in local_conf.py by:
    | plugin.activate(cd_burn)
    """
    def __init__(self):
        _debug_('cd_burn.PluginInterface.__init__()')
        plugin.ItemPlugin.__init__(self)
        self.device = ''
        self.item   = None
        self.thread_burn = None
        self.dev_list = []


    def config(self):
        """
        time for some auto stuff...
        """
        _debug_('config()', 1)
        record_dev = 'ATAPI:0,0,0'
        try:
            self.dev_list = []
            child = popen2.Popen4('cdrecord -scanbus')
            try:
                while child.poll() < 0:
                    line = child.fromchild.readline()
                    if line and line.find('RW') >= 0:
                        burn_dev = line.split()[0]
                        self.dev_list.append(burn_dev)
            except IOError:
                _debug_("no line")
            time.sleep(0.1)

            if len(self.dev_list) and self.dev_list[0]:
                record_dev = self.dev_list[0]
            else:
                record_dev = 'ATAPI:0,0,0'
        except Exception, e:
            print e

        return [
            ('CDBURN_CDRECORD_PATH', '/usr/bin/cdrecord', 'Path to cdrecord'),
            ('CDBURN_MKISOFS_PATH', '/usr/bin/mkisofs', 'Path to mkisofs'),
            ('CDBURN_GROWISOFS_PATH', '/usr/bin/growisofs', 'Path to growisofs'),
            ('CDBURN_DVDISO_USE_GROWISOFS', 1, 'Set to 1 to use growisofs instead of cdrecord for DVDs'),
            # in tao (track at once mode, empty value) cd record will leave 2 sec gaps between tracks
            # in dao (disk at once) no gaps at all, but not all drives support it
            ('CDBURN_AUDIO_DAO', 0, 'CDRecord canburn audio cds in DAO mode'),
            ('CDBURN_SPEED', '8', 'Speed to burn with cdrecord'),
            ('CDBURN_DVD_BURN_SPEED', '4', 'Speed to burn with cdrecord for DVDs'),
            ('CDBURN_TEMP_DIR', '/tmp', 'Temp file name used by cdrecord'),
            ('CDBURN_DEV', record_dev, 'Device for cdrecord to burn with (not auto detected)')
        ]


    def stop_burning(self, arg, menuw=None):
        _debug_('stop_burning(arg=%r, menuw=%r)' % (arg, menuw))
        pop = PopupBox(text=_('Interrupting burning process...'))
        pop.show()

        self.thread_burn.stop()
        pop.destroy()

        if menuw:
            menuw.back_one_menu(arg='reload')
            menuw.refresh

        AlertBox(text=_('Backup interrupted')).show()


    def actions(self, item):
        _debug_('actions(item=%r)' % (item,), 2)
        self.item = item
        show_burn_menu = 0;

        _debug_(_('Item type is %s' % item.type), 2)

        if self.thread_burn and self.thread_burn.running == 1:
            show_burn_menu = 1;

        if ( item.type == 'audio' or item.type == 'image' or item.type == 'video' or item.type == 'dir' or item.type == 'playlist'):
            show_burn_menu = 1;

        _debug_(_('Should show the menu? %i' % show_burn_menu), 2)

        if show_burn_menu:
            return [ (self.fill_menu, _('Burn CD')) ]
        else:
            return []


    def draw_menu(self, menuw=None, items=None):
        """
        draws the menu with the options on the screen
        """
        _debug_('draw_menu(menuw=%r, items=%r)' % (menuw, items))
        menu_items = []
        if items:
            for a in items:
                menu_items.append(menu.MenuItem(a[1], a[0]))
            moviemenu = menu.Menu(_('CD Burn Menu'), menu_items)
            menuw.pushmenu(moviemenu)


    def fill_menu(self, arg=None, menuw=None):
        """
        chooses the options available for this type of item
        """
        _debug_('fill_menu(arg=%r, menuw=%r)' % (arg, menuw))
        to_return = []
        item = self.item
        if self.thread_burn and self.thread_burn.running == 1:
            to_return.append( (self.thread_burn.show_status, 'Show burning status' ));
            to_return.append( (self.stop_burning, 'Stop the burn process' ));
            return self.draw_menu(menuw=menuw, items=to_return)


        _debug_('filling menu, item type = %s' % item.type)
        if item.type == 'dir':
            #dirs
            _debug_('Dir has media : %s ' % item.media)
            try:
                cur = BurnCDItem(item=item, plugin=self, menu=menuw)
                cur.findFromDir()
                cur2 = BurnCDItem(item=item, plugin=self, menu=menuw, burn_mode="audio_cd")
                cur2.findFromDirMatches(suffix=['mp3', 'flac', 'ogg', 'wav'])
                if cur.files:
                    to_return.append(( cur.burn, _('Copy dir to CD')) )
                if len(cur2.files)>0:
                    to_return.append(( cur2.burn, _('Burn audio files (MP3, Wav and Ogg) as Audio CD')))
            except Exception, e:
                print 'fill_menu:', e
                pass

        if item.type == 'playlist':
            #playlist burn
            _debug_('Playlist item has media : %s ' % item.media)
            try:
                cur = BurnCDItem(item=item, plugin=self, menu=menuw, burn_mode="audio_cd")
                cur.findFromPlaylist()
                if cur.files:
                    to_return.append(( cur.burn, _('Burn audio playlist to CD, %d files' % len(cur.files))) )
            except Exception, e:
                print 'fill_menu:', e
                pass

        try:
            #any item except dirs
            if (not item.subitems) and (not item.type == 'dir' and not item.type == 'playlist') :
                cur = BurnCDItem(item=item, plugin=self, menu=menuw)
                cur.findFileFromItem()
                #cur.addFilesFromItem()
                if cur.files:
                    to_return.append( ( cur.burn, _('Copy this file to CD')) )

            #any joined item except dirs
            elif (not item.type == 'dir' and not item.type == 'playlist') and item.subitems:
                for a in item.subitems:
                    cur = BurnCDItem(item=a, plugin=self, menu=menuw)
                    cur.findFileFromItem()
                    if cur.files:
                        to_return.append( ( cur.burn, _('Copy %s to CD' % a.name )) )
        except:
            pass


        #single video file
        try:
            if item.filename and item.type == 'video' and ( not item.subitems):
                cur = BurnCDItem(item=item, plugin=self, menu=menuw)
                cur.findRelated()
                #cur2 = BurnCDItem(ite=item, plugin=self, menu=menuw)
                #cur2.findRelated(mode=1)

            if len(cur.files) > 1:
                to_return.append(( cur.burn, _('Copy %s, and related, to CD' % item.name)) )
        except:
            pass

        #joined video files
        try:
            if item.subitems:
                if item.type == 'video':
                    for a in item.subitems:
                        if a.filename:
                            cur = BurnCDItem(item=a, plugin=self, menu=menuw)
                        cur.findRelated()

                        if len(cur.files) > 1:
                            to_return.append(( cur.burn, _('Copy %s, and related, file to CD' % a.name)) )
        except:
            pass

        #DVD movie on file system (ir DIR containing VIDEO_TS and/or AUDIO_TS)
        #Not sure how freevo works this about but bellow if seems to be fairly
        #accurate..
        try:
            if item.type == 'video' and item.mode == 'dvd' and item.media == None:
                cur = BurnCDItem(item=item, plugin=self, menu=menuw, burn_mode="dvd_video")
                cur.findFileFromItem()

                if cur.files and len(cur.files) == 1:
                    _debug_("Adding DVD-VIDEO Item to menu")
                    to_return.append(( cur.burn, _('Burn as DVD-VIDEO disc')) )
                elif len(self.files) > 1:
                    _debug_("To many objects to burn into a DVD Video")

        except:
            _debug_("Not possible to findFileFromItem for DVD Movie")

        if self.thread_burn and self.thread_burn.running == 0:
            to_return.append( (self.thread_burn.show_status, 'Show last burn status/result' ));

        return self.draw_menu(menuw=menuw, items=to_return)
