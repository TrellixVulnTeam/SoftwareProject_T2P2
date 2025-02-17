# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# videothumb - create a thumbnail for video files
# -----------------------------------------------------------------------
# $Id: videothumb.py 9238 2007-02-18 12:56:21Z duncan $
#
# Notes: This is a bad hack. It creates a new process to make the
#        images with mplayer and than copy it to the location
#
#        Based on videothumb.py commited to the freevo wiki
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


import sys, os, glob, shutil
import kaa.metadata as mmpython
from stat import *

def snapshot(videofile, imagefile=None, pos=None, update=True, popup=None):
    """
    make a snapshot of the videofile at position pos to imagefile
    """
    import config
    import popen3
    import kaa.imlib2 as Image
    import util
    import vfs
    import gui.PopupBox
    import osd
    
    if not imagefile:
        imagefile = vfs.getoverlay(videofile + '.raw')

    if not update and os.path.isfile(imagefile) and \
           os.stat(videofile)[ST_MTIME] <= os.stat(imagefile)[ST_MTIME]:
        return

    if imagefile.endswith('.raw'):
        imagefile += '.tmp'
        
    if popup:
        pop = gui.PopupBox(text='Creating thumbnail for \'%s\'...' % \
            Unicode(os.path.basename(videofile)),
            width=osd.get_singleton().width-config.OSD_OVERSCAN_X*2-80)
        pop.show()
        
    args = [ config.MPLAYER_CMD, videofile, imagefile ]

    if pos != None:
        args.append(str(pos))

    out = popen3.stdout([os.environ['FREEVO_SCRIPT'], 'execute',
                         os.path.abspath(__file__) ] + args)
    if out:
        for line in out:
            print line
    if vfs.isfile(imagefile):
        try:
            image = Image.open(imagefile)
            if image.width > 255 or image.height > 255:
                image.thumbnail((255,255))

            if image.mode == 'P':
                image.mode = 'RGB'

            if image.width * 3 > image.height * 4:
                # fix image with blank bars to be 4:3
                nh = (image.width*3)/4
                ni = Image.new((image.width, nh), from_format = image.mode)
                ni.draw_rectangle((0,0), (image.width, nh), (0,0,0,255), True)
                ni.blend(image, dst_pos=(0,(nh- image.height) / 2))
                image = ni
            elif image.width * 3 < image.height * 4:
                # strange aspect, let's guess it's 4:3
                new_size = (image.width, (image.width*3)/4)
                image = image.scale((new_size))

            # crop some pixels, looks better that way
            image = image.crop((4, 3), (image.width-8, image.height-6))
            # Pygame can't handle BGRA images
            if image.mode == 'BGRA':
                image.mode = 'RGBA'
            if imagefile.endswith('.raw.tmp'):
                f = vfs.open(imagefile[:-4], 'w')
                data = (str(image.get_raw_data(format=image.mode)), image.size, image.mode)
                f.write('FRI%s%s%5s' % (chr(image.width), chr(image.height), image.mode))
                f.write(data[0])
                f.close()
                os.unlink(imagefile)
            else:
                image.save(imagefile)
        except (OSError, IOError), e:
            print 'snapshot:', e
    else:
        print 'no imagefile found'
        print imagefile
        
    if popup:
        pop.destroy()
        
#
# main function, will be called when this file is executed, not imported
# args: mplayer, videofile, imagefile, [ pos ]
#

if __name__ == "__main__":
    import popen2
    
    mplayer   = os.path.abspath(sys.argv[1])
    filename  = os.path.abspath(sys.argv[2])
    imagefile = os.path.abspath(sys.argv[3])

    try:
        position = sys.argv[4]
    except IndexError:
        try:
            mminfo = mmpython.parse(filename)
            position = str(int(mminfo.video[0].length / 2.0))
            if hasattr(mminfo, 'type'):
                if mminfo.type in ('MPEG-TS', 'MPEG-PES'):
                    position = str(int(mminfo.video[0].length / 20.0))
        except:
            # else arbitrary consider that file is 1Mbps and grab position at 10%
            position = os.stat(filename)[ST_SIZE]/1024/1024/10.0
            if position < 360:
                position = '360'
            else:
                position = str(int(position))

    # chdir to tmp so we have write access
    os.chdir('/tmp')

    # call mplayer to get the image
    child = popen2.Popen3((mplayer, '-nosound', '-vo', 'png', '-frames', '8',
                           '-ss', position, '-zoom', filename), 1, 100)
    while(1):
        data = child.fromchild.readline()
        if not data:
            break
    child.wait()
    child.fromchild.close()
    child.childerr.close()
    child.tochild.close()
    # store the correct thumbnail
    captures = glob.glob('000000??.png')
    if captures:
        capture = captures[-1]
        try:
            shutil.copy(capture, imagefile)
        except:
            try:
                import config
                import vfs
                shutil.copy(capture, vfs.getoverlay(imagefile[1:]))
            except:
                print 'unable to write file'
    else:
        print "error creating capture for %s" % Unicode(filename)

    for capture in captures:
        try:
            os.remove(capture)
        except:
            print "error removing temporary captures for %s" % Unicode(filename)
