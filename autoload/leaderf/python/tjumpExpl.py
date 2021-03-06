#!/usr/bin/env python
# -*- coding: utf-8 -*-

import vim
import re
import time
from leaderf.utils import *
from leaderf.tagExpl import TagExplorer, TagExplManager

#*****************************************************
# TjumpExplorer
#*****************************************************
class TjumpExplorer(TagExplorer):
    def getContent(self, *args, **kwargs):
        tagname = args[0]
        taglist = lfEval('taglist("^%s$", @%%)' % (tagname,))
        
        for tag in taglist:
            tag['filename'] = tag['filename'].replace('\\\\', '\\')

        content = ['%s\t%s\t%s;"\t%s' % (tag['filename'], tag['name'], tag['cmd'], tag['kind']) for tag in taglist]
        return content

    def getStlCategory(self):
        return 'Tjump'

#*****************************************************
# TjumpExplManager
#*****************************************************
class TjumpExplManager(TagExplManager):
    def _getExplClass(self):
        return TjumpExplorer

    def _defineMaps(self):
        lfCmd("call leaderf#Tjump#Maps()")

    def _acceptSelection(self, *args, **kwargs):
        if len(args) == 0:
            return
        line = args[0]
        # {tagfile}<Tab>{tagname}<Tab>{tagaddress}[;"<Tab>{tagfield}..]
        tagfile, tagname, right = line.split('\t', 2)
        res = right.split(';"\t', 1)
        tagaddress = res[0]
        currentname = lfEval('@%')
        if currentname != tagfile:
            try:
                lfCmd("hide edit %s" % escSpecial(tagfile))
            except vim.error as e: # E37
                lfPrintError(e)
        else:
            lfCmd("normal! %sgg" % lfEval("line('.')"))

        if tagaddress[0] not in '/?':
            lfCmd(tagaddress)
        else:
            pattern = "\M" + tagaddress[1:-1]
            lfCmd("call search('%s', 'w')" % escQuote(pattern))

        if lfEval("search('\V%s', 'wc')" % escQuote(tagname)) == '0':
            lfCmd("norm! ^")

    def _getDigest(self, line, mode):
        """
        specify what part in the line to be processed and highlighted
        Args:
            mode: 0, return the full path
                  1, return the name only
                  2, return the directory name
        """
        if not line:
            return ''
        return line.split('\t', 1)[0]

#*****************************************************
# tjumpExplManager is a singleton
#*****************************************************
tjumpExplManager = TjumpExplManager()

__all__ = ['tjumpExplManager']
