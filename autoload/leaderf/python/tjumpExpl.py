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

    def startExplorer(self, win_pos, *args, **kwargs):
        self.setArguments(kwargs.get("arguments", {}))
        self._cli.setNameOnlyFeature(self._getExplorer().supportsNameOnly())
        self._cli.setRefineFeature(self._supportsRefine())

        content = self._getExplorer().getContent(*args, **kwargs)
        if not content:
            return
        if len(content) == 1:
            lfCmd("echo ''")
            self._acceptSelection(content[0])
            return
        lfCmd("echo ' Searching'")

        self._getInstance().setArguments(self._arguments)

        self._getInstance().enterBuffer(win_pos)
        self._initial_count = self._getInstance().getInitialWinHeight()

        self._getInstance().setStlCategory(self._getExplorer().getStlCategory())
        self._setStlMode()
        self._getInstance().setStlCwd(self._getExplorer().getStlCurDir())

        if lfEval("g:Lf_RememberLastSearch") == '1' and self._launched and self._cli.pattern:
            pass
        else:
            lfCmd("normal! gg")
            self._index = 0
            self._pattern = kwargs.get("pattern", "") or kwargs.get("arguments", {}).get("--input", [""])[0]
            self._cli.setPattern(self._pattern)

        self._start_time = time.time()
        self._bang_start_time = self._start_time
        self._status_start_time = self._start_time
        self._bang_count = 0
        self._read_content_exception = None

        if isinstance(content, list):
            self._is_content_list = True

            if len(content[0]) == len(content[0].rstrip("\r\n")):
                self._content = content
            else:
                self._content = [line.rstrip("\r\n") for line in content]

            self._getInstance().setStlTotal(len(self._content)//self._getUnit())
            self._result_content = self._content
            self._getInstance().setStlResultsCount(len(self._content))
            if lfEval("g:Lf_RememberLastSearch") == '1' and self._launched and self._cli.pattern:
                pass
            else:
                self._getInstance().setBuffer(self._content[:self._initial_count])

            self._callback = self._workInIdle
            if not kwargs.get('bang', 0):
                self.input()
            else:
                lfCmd("echo")
                self._getInstance().buffer.options['modifiable'] = False
                self._bangEnter()
        else:
            self._is_content_list = False
            self._result_content = []
            self._callback = partial(self._workInIdle, content)
            if lfEval("g:Lf_CursorBlink") == '0':
                self._content = self._getInstance().initBuffer(content, self._getUnit(), self._getExplorer().setContent)
                self.input()
            else:
                self._content = []
                self._offset_in_content = 0
                self._read_finished = 0
                self.input()

        self._launched = True

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
