#!/usr/bin/env python

"""Setup script for the freevo distribution."""


__revision__ = "$Id: setup.py 10565 2008-03-22 22:35:24Z duncan $"

# Python distutils stuff
import os
import sys

# Freevo distutils stuff
sys.path.append('./src')
import version
from util.distribution import setup, Extension, check_libs, docbook_finder
from distutils import core


libs_to_check = [
    ('xml.utils.qp_xml', 'http://pyxml.sourceforge.net/'),
    ('pygame', 'http://www.pygame.org'),
    ('twisted', 'http://www.twistedmatrix.com/'),
    ('twisted.web.microdom', 'http://www.twistedmatrix.com/'),
]

if sys.hexversion < 0x2050000:
    libs_to_check.append(('elementtree', 'http://effbot.org/zone/elementtree.htm'))

check_libs(libs_to_check)


class Runtime(core.Command):

    description     = "download and install runtime"
    user_options    = []
    boolean_options = []
    help_options    = []
    negative_opt    = {}

    def initialize_options (self):
        pass

    def finalize_options (self):
        pass

    def download(self, package):
        """
        download a package from sourceforge
        """
        url  = 'http://osdn.dl.sourceforge.net/sourceforge/' + package
        file = package[package.rfind('/')+1:]
        ddir = os.path.join(os.environ['HOME'], '.freevo/dist')
        if not os.path.isdir(ddir):
            os.makedirs(ddir)
        full = os.path.join(ddir, file)
        if not os.path.isfile(full):
            print 'Downloading %s' % file
            os.system('wget %s -O %s' % (url, full))
        if not os.path.isfile(full):
            print
            print 'Failed to download %s' % file
            print
            print 'Please download %s from http://www.sf.net/projects/%s' % \
                  (file, package[:package.find('/')])
            print 'and store it as %s' % full
            print
            sys.exit(0)
        return full


    def mmpython_install(self, result, dirname, names):
        """
        install mmpython into the runtime
        """
        for n in names:
            source = os.path.join(dirname, n)
            if dirname.find('/') > 0:
                destdir = dirname[dirname.find('/')+1:]
            else:
                destdir = ''
            dest   = os.path.join('runtime/lib/python2.3/site-packages',
                                  'mmpython', destdir, n)
            if os.path.isdir(source) and not os.path.isdir(dest):
                os.mkdir(dest)
            if n.endswith('.py') or n == 'mminfo':
                if n == 'dvdinfo.py':
                    # runtime contains a bad hack version of dvdinfo
                    # the normal one doesn't work
                    continue
                os.system('mv "%s" "%s"' % (source, dest))

    def run (self):
        """
        download and install the runtime + current mmpython
        """
        mmpython = self.download('mmpython/mmpython-%s.tar.gz' % version.mmpython)
        runtime  = self.download('freevo/freevo-runtime-%s.tar.gz' % version.runtime)
        print 'Removing runtime directory'
        os.system('rm -rf runtime')
        print 'Unpacking runtime'
        os.system('tar -zxf %s' % runtime)
        print 'Unpacking mmpython'
        os.system('tar -zxf %s' % mmpython)
        print 'Installing mmpython into runtime'
        os.path.walk('mmpython-%s' % version.mmpython, self.mmpython_install, None)
        os.system('rm -rf mmpython-%s' % version.mmpython)


# check if everything is in place
if (len(sys.argv) < 2 or sys.argv[1].lower() not in ('i18n', '--help', '--help-commands')):
    if os.path.isdir('.svn'):
        try:
            from subprocess import Popen, PIPE
            os.environ['LC_ALL']='C'
            p1 = Popen(["svn", "info", "--revision=BASE"], stdout=PIPE, env=os.environ)
            p2 = Popen(["sed", "-n", "/Revision:/s/Revision: *\([0-9]*\)/\\1/p"], stdin=p1.stdout, stdout=PIPE)
            revision = p2.communicate()[0]
            fh = open('src/revision.py', 'w')
            try:
                fh.write('__revision__ = \'%s\'\n' % revision.strip('\n'))
            finally:
                fh.close()
        except Exception, e:
            print e

    if (not os.path.isdir('./Docs/installation/html')):
        print 'Docs/howto not found. Please run ./autogen.sh'
        sys.exit(0)

import revision
# only add files not in share and src

data_files = []
# add some files to Docs
for f in ('COPYING', 'RELEASE_NOTES', 'ChangeLog', 'INSTALL', 'README'):
    data_files.append(('share/doc/freevo-%s' % version.__version__, ['%s' % f ]))
data_files.append(('share/doc/freevo-%s' % version.__version__, ['Docs/CREDITS' ]))
#data_files.append(('share/fxd', ['share/fxd/webradio.fxd']))

# copy freevo_config.py to share/freevo. It's the best place to put it
# for now, but the location should be changed
data_files.append(('share/freevo', [ 'freevo_config.py' ]))

# add docbook style howtos
os.path.walk('./Docs/installation', docbook_finder, data_files)
os.path.walk('./Docs/plugin_writing', docbook_finder, data_files)

# start script
scripts = ['freevo']

# now start the python magic
setup (name         = "freevo",
       version      = version.__version__,
       description  = "Freevo",
       author       = "Krister Lagerstrom, et al.",
       author_email = "freevo-devel@lists.sourceforge.net",
       url          = "http://www.freevo.org",
       license      = "GPL",

       i18n         = 'freevo',
       scripts      = scripts,
       data_files   = data_files,
       cmdclass     = { 'runtime': Runtime }
       )
