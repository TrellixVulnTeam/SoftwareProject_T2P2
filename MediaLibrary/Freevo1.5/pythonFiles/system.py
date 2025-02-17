# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# idlebar/system - IdleBar plugins for monitoring the system
# -----------------------------------------------------------------------
# $Id: system.py,v 1.11 2004/07/11 11:06:56 dischi Exp $
#
# Documentation moved to the corresponding classes, so that the help
# interface returns something usefull.
# Available plugins:
#       idlebar.system.procstats
#       idlebar.system.sensors
#
# -----------------------------------------------------------------------
# $Log: system.py,v $
# Revision 1.11  2004/07/11 11:06:56  dischi
# 2.6.x kernel fixes
#
# Revision 1.10  2004/07/10 12:33:41  dischi
# header cleanup
#
# Revision 1.9  2004/05/13 12:30:53  dischi
# 2.6 fix from Viggo Fredriksen
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


import time
import os
import string
import types
import re

import config

from plugins.idlebar import IdleBarPlugin

class procstats(IdleBarPlugin):
    """
    Retrieves information from /proc/stat and shows them in the idlebar.
    This plugin can show semi-accurate cpu usage stats and free memory
    in megabytes (calculated approx. as MemFree+Cached?)

    Activate with 
       plugin.activate('idlebar.system.procstats',level=20) for defaults or
       plugin.activate('idlebar.system.procstats',level=20,args=(Mem,Cpu,Prec))
      where
       Mem:  Draw memfree  (default=1, -1 to disable)
       Cpu:  Draw cpuusage (default=1, -1 to disable)
       Prec: Precision used when drawing cpu usage (default=1)
    """
    def __init__(self,Mem=1,Cpu=1,Prec=1):
        IdleBarPlugin.__init__(self)
        self.drawCpu = Cpu
        self.drawMem = Mem
        self.precision = Prec
        self.time = 0
        self.lastused = 0
        self.lastuptime = 0

    def getStats(self):
        """
        Don't get the stats for each update
        as it gets annoying while navigating
        Update maximum every 10 seconds
        """
        if (time.time()-self.time)>10:
            self.time = time.time()

            if self.drawMem == 1:
                self.getMemUsage()

            if self.drawCpu == 1:
                self.getCpuUsage()

    def getMemUsage(self):
        """
        May not be correct, but i like to see
        total free mem as freemem+cached
        """
        free    = 0
        meminfo = None
        try:
            f = file('/proc/meminfo', 'r')
            meminfo = f.read()
            f.close()
        except OSError:
            _debug_('[procstats]: The file /proc/meminfo is not available')

        if meminfo:
            i = 0
            meminfo = meminfo.split()
            for l in meminfo:
                if l in ['MemFree:', 'Buffers:', 'Cached:']:
                    free += int(meminfo[i+1])
                i += 1

        self.currentMem = _('%iM') % (free/1024)

    def getCpuUsage(self):
        """
        This could/should maybe be an even more
        advanced algorithm, but it will suffice 
        for normal use.

        Note:
        cpu defined as 'cpu <user> <nice> <system> <idle>'
        at first line in /proc/stat
        """
        uptime = 0
        used = 0
        f = open('/proc/stat')

        if f:
            stat = string.split(f.readline())
            used = long(stat[1])+long(stat[2])+long(stat[3])
            uptime = used + long(stat[4])

        f.close()
        usage = (float(used-self.lastused)/float(uptime-self.lastuptime))*100
        self.lastuptime = uptime
        self.lastused = used
        self.currentCpu = _('%s%%') % round(usage,self.precision)
 
    def draw(self, (type, object), x, osd):
        try:
            self.getStats()
        except:
            _debug_('[procstats]: Not working, this plugin is only tested with 2.4 and 2.6 kernels')

        font = osd.get_font('small0')
        widthmem = 0
        widthcpu = 0

        if self.drawCpu == 1:
            widthcpu = font.stringsize(self.currentCpu)
            osd.draw_image(os.path.join(config.ICON_DIR, 'misc/cpu.png'),
                          (x, osd.y + 7, -1, -1))    
            osd.write_text(self.currentCpu, font, None, x + 15, osd.y + 55 - font.h,
                           widthcpu, font.h, 'left', 'top')

        if self.drawMem == 1:
            widthmem = font.stringsize(self.currentMem)

            osd.draw_image(os.path.join(config.ICON_DIR, 'misc/memory.png'),
                          (x + 15 + widthcpu, osd.y + 7, -1, -1))
            osd.write_text(self.currentMem, font, None, x + 40 + widthcpu, 
                           osd.y + 55 - font.h, widthmem, font.h, 'left', 'top')

        return widthmem + widthcpu + 15


#----------------------------------- SENSOR --------------------------------

class sensors(IdleBarPlugin):
    """
    Displays sensor temperature information (cpu,case) and memory-stats.

    Activate with:
       plugin.activate('idlebar.system.sensors', level=40,
              args=('cpusensor', 'casesensor', 'meminfo'))
       plugin.activate('idlebar.system.sensors', level=40,
              args=(('cpusensor','compute expression'), 
                    ('casesensor','compute_expression'), 'meminfo'))
                    
    cpu and case sensor are the corresponding lm_sensors : this should be
    temp1, temp2 or temp3. defaults to temp3 for cpu and temp2 for case
    meminfo is the memory info u want, types ar the same as in /proc/meminfo :
    MemTotal -> SwapFree.
    casesensor and meminfo can be set to None if u don't want them
    This requires a properly configure lm_sensors! If the standard sensors frontend
    delivered with lm_sensors works your OK.
    Some sensors return raw-values, which have to be computed in order 
    to get correct values. This is normally stored in your /etc/sensors.conf.
    Search in the corresponding section for your chipset, and search the 
    compute statement, e.g. "compute temp3 @*2, @/2". Only the third
    argument is of interest. Insert this into the plugin activation line, e.g.: 
    "[...] args=(('temp3','@*2'),[...]". The @ stands for the raw value.
    The compute expression  works for the cpu- and casesensor.
    """
    class sensor:
        """
        small class defining a temperature sensor
        """
        def __init__(self, sensor, compute_expression, hotstack):
            self.initpath = "/proc/sys/dev/sensors/"
            self.k6path = '/sys/bus/i2c/devices'
            self.k6 = 0
            self.senspath = self.getSensorPath()
            self.sensor = sensor
            self.compute_expression = compute_expression
            self.hotstack = hotstack
            self.washot = False
            
        def temp(self):
            def temp_compute (rawvalue):
                try:
                    temperature = eval(self.compute_expression.replace ("@",str(rawvalue)))
                except:
                    print "ERROR in idlebar.sensors: Compute expression does not evaluate"
                    temperature = rawvalue
                return int(temperature)

            if self.senspath == -1 or not self.senspath:
                return "?"        
            
            if self.k6 :
                file = os.path.join( self.senspath, 'temp_input' + self.sensor[-1] )
                fhot = os.path.join( self.senspath, 'temp_max' + self.sensor[-1] )
                if not os.path.exists(file):
                    file = os.path.join( self.senspath, 'temp' + self.sensor[-1] + '_input')
                    fhot = os.path.join( self.senspath, 'temp' + self.sensor[-1] + '_max')
                f = open(fhot)
                hotdata = f.read()
                f.close()
            
            else:
                file = os.path.join( self.senspath, self.sensor )
            
            f = open(file)
            data = f.read()
            f.close()
            
            if self.k6:
                temp = int(temp_compute(float(data[0:2])))
                hot = int(temp_compute(float(hotdata[0:2])))
                
            else:
                temp = int(temp_compute (float(string.split(data)[2])))
                hot = int(temp_compute (float(string.split(data)[0])))
            
            if temp > hot:
                if self.washot == False:
                    self.hotstack = self.hotstack + 1
                    self.washot == True
            else:
                if self.washot == True:
                    self.hotstack = self.hotstack - 1
                    self.washot = False
                
            return "%s�" % temp
            
        def getSensorPath(self):
            #let's try if we find a sys filesystem (and kernel2.6 style sensors)
            if os.path.exists(self.k6path):
                self.k6 = 1
                #print "Detected kernel 2.6 sys fs"
                for senspath in os.listdir(self.k6path):
                    testpath = os.path.join(self.k6path , senspath)
                    for pos_sensors in os.listdir(testpath):
                        if pos_sensors == "temp_input1":
                            return testpath
                        if pos_sensors == "temp1_input":
                            return testpath
                            
            if not os.path.exists(self.initpath):
                if self.k6:
                    print "Kernel 2.5/2.6 detected, but no i2c sensors found"
                    print "Did u load (or compile) the necessary bus driver"
                    print "and sensor chip modules"
                else:
                    print "LM_Sensors proc data not available? Did you load i2c-proc"
                    print "and configured lm_sensors?"
                    print "temperatures will be bogus"
                return -1 #failure
                
            for senspath in os.listdir(self.initpath):
                testpath = os.path.join(self.initpath , senspath)
                if os.path.isdir(testpath): 
                    return testpath
                    
    
    
    def __init__(self, cpu='temp3', case='temp2' , ram='MemTotal'):
        IdleBarPlugin.__init__(self)
        
        
        self.hotstack = 0
        self.case = None
    
        if isinstance (cpu,types.StringType):
            self.cpu = self.sensor(cpu, '@', self.hotstack)
        else:
            self.cpu = self.sensor(cpu[0], cpu[1], self.hotstack)
    
        if case: 
            if isinstance (case,types.StringType):
                self.case = self.sensor(case, '@', self.hotstack)
            else:
                self.case = self.sensor(case[0], case[1], self.hotstack)


        self.ram = ram
        self.retwidth = 0

        
    def getRamStat(self):

        f = open('/proc/meminfo')
        data = f.read()
        f.close()
        rxp_ram = re.compile('^%s' % self.ram)
        
        for line in data.split("\n"):
            m = rxp_ram.match(line)
            if m :
                return "%sM" % (int(string.split(line)[1])/1024)
        
    
    def draw(self, (type, object), x, osd):
        casetemp = None
        widthcase = 0
        widthram  = 0

        font  = osd.get_font('small0')
        if self.hotstack != 0:
            font.color = 0xff0000
        elif font.color == 0xff0000 and self.hotstack == 0:
            font.color = 0xffffff
        
        cputemp = self.cpu.temp()        
        widthcpu = font.stringsize(cputemp)
        osd.draw_image(os.path.join(config.ICON_DIR, 'misc/cpu.png'),
                       (x, osd.y + 8, -1, -1))
        osd.write_text(cputemp, font, None, x + 15, osd.y + 55 - font.h, widthcpu, font.h,
                       'left', 'top')
        widthcpu = max(widthcpu, 32) + 10

        if self.case:
            casetemp = self.case.temp()
            
            widthcase = font.stringsize(casetemp)
            osd.draw_image(os.path.join(config.ICON_DIR, 'misc/case.png'),
                                        (x + 15 + widthcpu, osd.y + 7, -1, -1))
            osd.write_text(casetemp, font, None, x + 40 + widthcpu,
                           osd.y + 55 - font.h, widthcase, font.h,
                           'left', 'top')
            widthcase = max(widthcase, 32) + 10

        if self.ram:
            text = self.getRamStat()
            widthram = font.stringsize(text)
            if casetemp:
                img_width = x + 15 + widthcpu + widthcase + 15
            else:
                img_width = x + 15 + widthcpu
            osd.draw_image(os.path.join(config.ICON_DIR, 'misc/memory.png'),
                           (img_width, osd.y + 7, -1, -1))
            osd.write_text(text, font, None, img_width + 15, osd.y + 55 - font.h,
                           widthram, font.h, 'left', 'top')
                       
        if self.retwidth == 0:
            self.retwidth = widthcpu + 15
            if self.case: 
                self.retwidth = self.retwidth + widthcase + 12
            if self.ram:
                self.retwidth = self.retwidth + 15 + widthram
                
        return self.retwidth
