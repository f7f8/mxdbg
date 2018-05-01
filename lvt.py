#!/usr/bin/env python
# -*- coding: utf-8 -*-

import lldb
import re
import sys
import struct
import time
import dbghelper

_IMAGE_NAME = 'MxBrowser-iPhone'

_INS_RET = 0xd65f03c0
_INS_NOP = 0xd503201f
_INS_MOV_X0_1 = 0xd2800020

def cmd_attach_remote(debugger, command, result, internal_dict):
    print("[%s] wait for remote target process: %s" % (__name__, _IMAGE_NAME))
    dbghelper.waitForRemoteTarget(_IMAGE_NAME, debugger, 12345)


def cmd_app_info(debugger, command, result, internal_dict):
    offset = dbghelper.getImageOffset(_IMAGE_NAME)
    print("[%s] %s's base is 0x%x" % (__name__, _IMAGE_NAME, offset))


def cmd_anti_anti_debug(debugger, command, result, internal_dict):
    offset = dbghelper.getImageOffset(_IMAGE_NAME)
    proc = debugger.GetSelectedTarget().GetProcess()
    patch_ptrace_entry(offset, proc)
    patch_isDebuggerPresent(offset, proc)

    patch_police_isLegalEnvironmentAndUnLVTLimit(offset, proc)

    patch_UeipSetDataDirectRequest(offset, proc)
    patch_setupFlurryAnalytics(offset, proc)
    patch_sendOnLineStatistics(offset, proc)


def patch_ptrace_entry(base, proc):
    va = base + 0x10000c3fc
    proc.WriteMemory(va, struct.pack('I', _INS_NOP), lldb.SBError())
    print '[%s] patch_ptrace_entry applied.' % __name__


def patch_isDebuggerPresent(base, proc):
    va = base + 0x100459828
    proc.WriteMemory(va, struct.pack('I', _INS_NOP), lldb.SBError())
    va = base + 0x10045982c
    proc.WriteMemory(va, struct.pack('I', _INS_NOP), lldb.SBError())
    print '[%s] patch_isDebuggerPresent applied.' % __name__


def patch_police_isLegalEnvironmentAndUnLVTLimit(base, proc):
    va = base + 0x1004755e8
    proc.WriteMemory(va, struct.pack('I', _INS_MOV_X0_1), lldb.SBError())
    va = base + 0x1004755ec
    proc.WriteMemory(va, struct.pack('I', _INS_RET), lldb.SBError())
    print '[%s] patch_police_isLegalEnvironmentAndUnLVTLimit applied.' % __name__


def patch_UeipSetDataDirectRequest(base, proc):
    va = base + 0x100545650
    proc.WriteMemory(va, struct.pack('I', _INS_RET), lldb.SBError())
    print '[%s] patch_UeipSetDataDirectRequest applied.' % __name__


def patch_setupFlurryAnalytics(base, proc):
    va = base + 0x1000ce664
    proc.WriteMemory(va, struct.pack('I', _INS_RET), lldb.SBError())
    print '[%s] patch_setupFlurryAnalytics applied.' % __name__


def patch_sendOnLineStatistics(base, proc):
    va = base + 0x1000cde90
    proc.WriteMemory(va, struct.pack('I', _INS_RET), lldb.SBError())
    print '[%s] patch_sendOnLineStatistics applied.' % __name__


def installCommands(debugger):
    cmds = [
        {
            'fn': 'cmd_attach_remote',
            'op': 'ar',
            'desc': 'attach remote debug process'
        },
        {
            'fn': 'cmd_app_info',
            'op': 'ai',
            'desc': 'show target application information'
        },
        {
            'fn': 'cmd_anti_anti_debug',
            'op': 'aad',
            'desc': 'apply anti-anti-debugging patchings'
        }
    ]

    print("[%s] all available commands:" % (__name__))
    for cmd in cmds:
        print("[%s] %s: %s" % (__name__, cmd['op'], cmd['desc']))
        dbghelper.addFunctionCmd(debugger, __name__, cmd['fn'], cmd['op'])


def __lldb_init_module(debugger, internal_dict):
    print("[%s] debugging helper has loaded!" % (__name__))
    installCommands(debugger)
    debugger.GetSelectedTarget().DeleteAllBreakpoints()
