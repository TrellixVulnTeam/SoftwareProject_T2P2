# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# A helper to list all plugins and prints help about them
# -----------------------------------------------------------------------
# $Id: plugins.py 11390 2009-04-08 18:37:53Z duncan $
#
# Notes:       This script prints out information aboyt plugins in
#              Freevo. As descriptions the Python class description
#              between two """ after the class name is used.
#
# Todo:        All plugins need to get a nice description
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

import re
import os
import sys
from optparse import Option, OptionValueError, OptionParser, IndentedHelpFormatter

import config
import plugin
import util
import imp


def find_plugin_interface(data):
    """
    Search a source file for the PluginInterface classes
    @return: a list of classes source code as a string
    """

    has_classes = re.compile('\n\s*(class[^\n]*:.*?)((\n\s*class)|($))', re.DOTALL)
    has_plugin = re.compile('\n *class PluginInterface *(.*) *:')
    classes = []
    while 1:
        res = has_classes.search(data)
        if not res:
            break
        begin, end = res.span()
        length = len(res.groups()[1])
        classes.append(data[begin:end-length])
        data = data[end-length:]

    class_srcs = []
    for class_src in classes:
        if has_plugin.search(class_src):
            class_srcs.append(class_src)

    return class_srcs


def parse_plugins2():
    """
    The idea is to extract the PluginInterface class or classes from the source module
    and then to import it and extract the __doc__ string from the Class and the
    config() from the class instance.

    This does't quite work, neither does import PluginInterface from <m> as <a>
    nor do any of the import methods that I've tried. I've left this code in to
    remind any that this techique does work in all cases, it does work in come
    cases and from the freevo prompt.
    """

    import time
    import pygame
    from screensaver import ScreenSaverPlugin
    from idlebar import IdleBarPlugin
    from util import Rendezvous
    import osd
    osd = osd.get_singleton()

    all_plugins = []
    print 'FREEVO_PYTHON', os.environ['FREEVO_PYTHON']
    print 'PYTHONPATH', os.environ['PYTHONPATH']
    for file in util.recursefolders(os.environ['FREEVO_PYTHON'], 1, '*.py', 1):
        if file.find('plugin.py') > 0:
            continue

        data = open(file, 'r').read()
        for plugin_interface in find_plugin_interface(data):
            if not plugin_interface:
                print 'Can\'t find interface in %s' % file
                continue

            try:
                exec plugin_interface
            except Exception, e:
                print 'Error:1:%s: %s' % (file, e)
                break

            print '<<<%s>>>' % file
            print PluginInterface.__bases__
            for base in PluginInterface.__bases__:
                print base.__name__
            print PluginInterface.__doc__

            try:
                interface = PluginInterface()
                print interface.config()
            except Exception, e:
                print 'Error:2:%s: %s' % (file, e)
                continue

            interface = None
            PluginInterface = None

    return ''


def parse_plugins(plugin_name=''):
    start = re.compile('^class *(.*)\((.*Plugin\s*).:')
    stop  = re.compile('^[\t ]*def.*:')
    comment = re.compile('^[\t ]*"""')
    config_start = re.compile('^[ \t]+def +config *\( *self *\) *:')
    config_end   = re.compile(' *(class|def|@)')

    print_line = 0
    ptypes = {}

    all_plugins = []

    active = []
    for p in plugin.__all_plugins__:
        active.append(p[0])

    plugin_shortname = plugin_name.split('.')[-1]+'.py'
    plugin_init_name = os.path.join(plugin_name.split('.')[-1], '__init__.py')
    for file in util.recursefolders(os.environ['FREEVO_PYTHON'], 1, '*.py', 1):
        if file.find('plugin.py') > 0:
            continue
        if plugin_name:
            if file.find(plugin_shortname) < 0 and file.find(plugin_init_name) < 0:
                continue
        parse_status = 0
        whitespaces  = 0
        scan_config  = 0
        for line in util.readfile(file) + [ 'class Foo' ]:
            if config_end.match(line) and scan_config:
                scan_config = 0
                all_plugins[-1][-1] = config

            if scan_config:
                config += line+'\n'

            if config_start.match(line):
                config      = 'def return_config():\n'
                scan_config = line.find('def')

            if (comment.match(line) and parse_status == 2) or (stop.match(line) and parse_status == 1):
                parse_status = 0
                all_plugins[-1][-2] = desc

            if parse_status == 2:
                if desc:
                    desc += '\n'
                if not whitespaces:
                    tmp = line.lstrip()
                    whitespaces = line.find(tmp)
                desc += line[whitespaces:].rstrip()

            if comment.match(line) and parse_status == 1:
                parse_status = 2
                whitespaces  = 0

            if start.match(line):
                fname = re.sub('^src.', '', file)
                fname = re.sub('^%s.' % os.environ['FREEVO_PYTHON'], '', fname)
                fname = re.sub('/', '.', os.path.splitext(fname)[0])
                fname = re.sub('plugins.', '', fname)
                fname = re.sub('.__init__', '', fname)

                type = start.match(line).group(2).strip()
                if re.match('^plugin.(.*)', type):
                    type = re.match('^plugin.(.*)', type).group(1)
                if start.match(line).group(1) == 'PluginInterface':
                    name = fname
                else:
                    name = '%s.%s' % ( fname, start.match(line).group(1))

                if name in active:
                    status = 'active'
                else:
                    status = 'not loaded'

                parse_status = 1
                desc = ''
                if not name in ('idlebar.IdleBarPlugin', ):
                    all_plugins.append([name, file, type, status, '', ''])
    return all_plugins


def print_info(plugin_name, all_plugins):
    for name, file, type, status, desc, config_string in all_plugins:
        if name == plugin_name:
            print 'Name: %s' % name
            print 'Type: %s' % type
            print 'File: %s' % file
            print
            print 'Description:'
            print '------------'
            print desc
            print
            if config_string.find('config') > 0:
                try:
                    exec(config_string)
                    config_list = return_config()
                except SyntaxError, e:
                    config_list = None
                    print '%s in %r' % (e, config_string)

                if config_list:
                    print
                    print 'Plugin configuration variables:'
                    print '-------------------------------'
                    for v in config_list:
                        print '%s: %s' % (v[0], v[2])
                        print 'Default: %r' % (v[1],)
                        print
                    print
            if status == 'active':
                print 'The plugin is loaded with the following settings:'
                for p in plugin.__all_plugins__:
                    if p[0] == name:
                        type = p[1]
                        if not type:
                            type = 'default'
                        print 'type=%s, level=%s, args=%s' % (type, p[2], p[3])
            else:
                print 'The plugin is not activated in the current setting'

def iscode(line):
    """
    Find code lines in the docstring When the line starts with a '|' then is has
    been marked as a code line

    @note: this does not work too well in all cases
    """
    return line.strip().startswith('|')
    return (len(line) > 2 and line[:2].upper() == line[:2] and line.find('=') > 0) or \
        (line and line[0] in ('#', ' ', '[', '(')) or (line.find('plugin.') == 0)


def html_info(plugin_name, all_plugins):
    ret = ''
    for name, file, type, status, desc, config_string in all_plugins:
        if name == plugin_name:
            ret += '<h2>%s</h2>' % name
            ret += '<b>Type: %s</b><br>' % type
            ret += '<b>File: %s</b><br>' % file
            ret += '\n'
            if not desc:
                ret += '<p>The plugin has no description. You can help by ' + \
                       'writing a small description and send it to the Freevo '\
                       'mailinglist.</p>\n'
            else:
                ret += '<br><b>Description</b>:'
                ret += '<p>'
                tmp  = Unicode(desc)
                desc = []
                for block in tmp.split('\n\n'):
                    for line in block.split('\n'):
                        desc.append(line)
                    desc.append('')

                code = 0
                for i in range(len(desc)):
                    line = desc[i]
                    if iscode(line):
                        if not code:
                            ret += '<br><pre class="code">\n'
                        ret += line+'\n'
                        code = 1

                        try:
                            if (desc[i+1] and not iscode(desc[i+1])) or (desc[i+2] and not iscode(desc[i+2])):
                                ret += '</pre>'
                                code = 0
                        except IndexError:
                            ret += '</pre>'
                            code = 0
                    elif line:
                        ret += line + '\n'
                    elif code:
                        ret += '\n'
                    else:
                        ret += '<br>\n'

                if code:
                    ret += '</pre>'
                    code = 0
                ret += '</p>'
                ret += '\n'

            if status == 'active':
                ret += '<p>The plugin is loaded with the following settings:'
                for p in plugin.__all_plugins__:
                    if p[0] == name:
                        type = p[1]
                        if not type:
                            type = 'default'
                        ret += '<br>type=%s, level=%s, args=%s' % (type, p[2], p[3])
                ret += '</p>'
            else:
                ret += '<p>The plugin is not activated in the current setting</p>'
            return ret
    return ret


def wiki_word(s, mode):
    """
    Need to escape mixed case words for the wiki
    """
    if mode == 'moin':
        return s
    needs_pling=re.compile('^([A-Z]+[^.]*[A-Z]+[^.]*)')
    words = []
    for word in s.split('.'):
        if needs_pling.match(word):
            word = '!'+word
        words.append(word)
    return '.'.join(words)


def wiki_info(name, file, type, status, desc, config, mode, names=[]):
    """
    Wiki formatter, formats a single entry for a wiki page
    """
    #print '%s f=%r t=%s s=%r d=%r c=%r' % (name, file, type, status, desc, config_list)
    ret = ""
    ret += "-----\n"
    ret += "== %s ==\n" % (wiki_word(name, mode))
    ret += "----\n"
    ret += "'''File: %s'''\n" % (file)
    ret += "\n"
    if not desc:
        ret += "The plugin has no description. You can help by " + \
               "writing a small description and send it to the Freevo "\
               "mailinglist.\n"
        return ret

    ret += "=== Description ===\n"
    ret += "\n"
    tmp  = desc
    desc = []
    for block in tmp.split("\n\n"):
        for line in block.split("\n"):
            desc.append(line)
        desc.append("")

    code = 0
    for i in range(len(desc)):
        line = desc[i]
        if iscode(line):
            if not code:
                if mode == 'trac':
                    ret += "{{{\n"
                    ret += "#!python\n"
                else:
                    ret += "{{{#!python\n"
            line = line.lstrip(' ')[1:]
            ret += line+"\n"
            code = 1

            try:
                if (desc[i+1] and not iscode(desc[i+1])) or (desc[i+2] and not iscode(desc[i+2])):
                    ret += "}}}\n"
                    code = 0
            except IndexError:
                ret += "}}}\n"
                code = 0
        elif line:
            ret += line+"\n"
        elif code:
            ret += "\n"
        else:
            ret += "\n"

    if code:
        ret += "}}}\n"
        code = 0
    #ret += "\n"

    if config:
        ret += "=== Configuration ===\n"
        ret += "\n"
        if mode == 'trac':
            ret += "{{{\n"
            ret += "#!rst\n"
            ret += "Config Item    Value        Description\n"
            ret += "============== ============ =================================\n"
            for config_item in config:
                ret += "%s %s %s\n" % config_item
            ret += "============== ============ =================================\n"
            ret += "}}}\n"
        else:
            ret += "||<20%>'''Config Item'''||<20%>'''Value'''||<:99%>'''Description'''||\n"
            for config_item in config:
                ret += "||%s||%s||%s||\n" % config_item

    return ret

def compare_types(first, second):
    values = {
        'MainMenuPlugin': 1,
        'Plugin': 2,
        'DaemonPlugin': 3,
        'IdleBarPlugin': 4,
        'ItemPlugin': 5,
        'MimetypePlugin': 6,
        'ScreenSaverPlugin': 7,
    }
    value_first = values.has_key(first) and values[first] or 10
    value_second = values.has_key(second) and values[second] or 10
    return value_first - value_second

def parse_options(defaults):
    """
    Parse command line options
    """
    formatter=IndentedHelpFormatter(indent_increment=2, max_help_position=32, width=100, short_first=0)
    parser = OptionParser(conflict_handler='resolve', formatter=formatter, usage="""
This helper shows the list of all plugins included in Freevo and can
information about them.

A plugin can be activated by adding "plugin.activate(name)" into the
local_conf.py. Optional arguments are type, level and args

type:  specifies the type of this plugin. The default it is all for plugins not
       located in a specific media dir (e.g. rom_drives), some plugins are
       supposed to be insert into the specific dir (e.g. video.imdb) and have
       this as default type. You can override it by setting the type, e.g.  the
       type 'video' for rom_drives.rom_items will only show the rom drives in
       the video main menu.

level: specifies the position of the plugin in the plugin list. This sets the
       position of the items in the menu from this plugin to arrange them

args:  some plugins require some additional arguments

To remove a plugin activated in freevo_config, it's possible to add
"plugin.remove(name)" into the local_conf.py. The activate function also
returns a plugin number, for the plugins loaded by freevo_config, it's also
possible to use this number: plugin.remove(number).

There are five types of plugins:

MainMenuPlugin: show items in the main menu or in the media main menu like video
ItemPlugin:     add actions to items, shown after pressing ENTER on the item
DaemonPlugin:   a plugin that runs in the background
IdlebarPlugin:  subplugin for the idlebar plugin
Plugin:         plugin to add some functions to Freevo, see plugin description.


This helper script has the following options to get information about possible
plugins in Freevo.""", version='%prog 1.0')
    parser.add_option('-v', '--verbose', action='count', default=0,
        help='set the level of verbosity [default:%default]')
    parser.add_option('-l', '--list', action='store_true', default=False,
        help='list all plug-ins [default:%default]')
    parser.add_option('-i', '--info', action='append', default=None, metavar='NAME',
        help='display detailed information about the plug-in [default:%default]')
    parser.add_option('-a', '--all', action='store_true', default=False,
        help='display detailed information about all plug-ins [default:%default]')
    parser.add_option('--html', action='store_true', default=False,
        help='display detailed information about all plug-ins in html format [default:%default]')
    parser.add_option('--wiki', action='store_true', default=False,
        help='display detailed information about all plug-ins in wiki format [default:%default]')
    parser.add_option('--wiki-mode', action='store', metavar='MODE', choices=['moin', 'trac'], default='moin',
        help='display detailed information about all plug-ins in wiki format [default:%default]')
    plugin_types = [ 'MainMenuPlugin', 'ItemPlugin', 'DaemonPlugin', 'IdlebarPlugin', 'Plugin', ]
    parser.add_option('--module-type', action='store', metavar='TYPE', choices=plugin_types, default=[],
        help='display detailed wiki information about a plug-in type')
    return parser


if __name__ == '__main__':
    defaults = { }
    opts_parser = parse_options(defaults)
    (opts, args) = opts_parser.parse_args()
    defaults.update(opts.__dict__)

    # show a list of all plugins
    if opts.list:
        all_plugins = parse_plugins()

        types = []
        for p in all_plugins:
            if not p[2] in types:
                types.append(p[2])
        for t in types:
            print
            print '%ss:' % t
            underline = '--'
            for i in range(len(t)):
                underline += '-'
            print underline
            for name, file, type, status, desc, config in all_plugins:
                if type == t:
                    if desc.find('\n') > 0 and desc.find('\n\n') == desc.find('\n'):
                        smalldesc = desc[:desc.find('\n')]
                    else:
                        smalldesc = desc
                    if len(smalldesc) > 43:
                        smalldesc = smalldesc[:40] + '...'
                    if status == 'active':
                        name = '%s (%s)' % (name, status)
                    print '%-35s %s' % (name, smalldesc)

    # show info about a plugin
    elif opts.info:
        for name in opts.info:
            print_info(name, parse_plugins(name))

    # show info about all plugins (long list)
    elif opts.all:
        all_plugins = parse_plugins()
        for name in all_plugins:
            if name != all_plugins[0] and name != all_plugins[-1]:
                print '\n********************************\n'
            print_info(name[0], [name])

    # show info about all plugins as html
    elif opts.html:
        all_plugins = parse_plugins()

        print """<html>
      <head>
        <meta HTTP-EQUIV="Content-Type" CONTENT="text/html;charset=iso-8859-1">
        <title>Freevo Plugins</title>
        <link rel="stylesheet" type="text/css" href="freevowiki.css">
      </head>
      <body>
        <font class="headline" size="+3">Freevo Plugin List</font>
        <p><b>Index</b><ol>"""

        for p in all_plugins:
            print '<li><a href="#%s">%s</a></li>' % (p[0], p[0])
        print '</ol> '

        for p in all_plugins:
            print '<a name="%s"></a>' % p[0]
            print html_info(p[0], [p])

        print '</body>'

    # show info about all plugins in wiki format
    elif opts.wiki:
        # we should be able to call this in one of several modes
        # freevo plugins -wiki [moin|trac] [<plug-in type>*|<plug-in name>*]
        mode = 'moin'
        types = []
        modules = []
        mode = opts.mode
        all_plugins = parse_plugins()

        # This is a bit horrid, should do this cleaner
        if mode == 'trac':
            print '[[TOC(depth=2)]]'
        else:
            print '[[TableOfContents(2)]]'
        print

        #print 'name=%r file=%r type=%r status=%r desc=%r config=%r' % (name, file, type, status, desc, config)
        list_plugins_by_type = False
        if modules:
            for name, file, type, status, desc, config in all_plugins:
                if type in modules:
                    if type in types:
                        continue
                    list_plugins_by_type = True
                    types.append(type)
                    continue

            if list_plugins_by_type:
                modules = []
            else:
                # specified a list of modules by name
                for name, file, type, status, desc, config in all_plugins:
                    if name in modules:
                        if type in types:
                            continue
                        types.append(type)
                        continue

        else:
            for name, file, type, status, desc, config in all_plugins:
                if type in types:
                    continue
                types.append(type)

        if not list_plugins_by_type:
            types.sort(compare_types)

        for t in types:
            print
            print '= %ss =' % t
            print '------'
            print ''
            for name, file, type, status, desc, config in all_plugins:
                if type == t:
                    if modules and name not in modules:
                        continue

                    if config:
                        try:
                            exec(config)
                            config_list = return_config()
                        except SyntaxError, e:
                            config_list = [('', '', e)]
                        except AttributeError, e:
                            config_list = [('', '', e)]
                        except Exception, e:
                            config_list = [('', '', e)]
                    else:
                        config_list = []

                    if file.startswith(os.environ['FREEVO_PYTHON']):
                        file = file[len(os.environ['FREEVO_PYTHON'])+1:]

                    print wiki_info(name, file, type, status, desc, config_list, mode)

    else:
        opts_parser.print_help()
        print
        opts_parser.print_version()
