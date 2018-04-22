#!/usr/bin/env python
# -*- coding: utf-8 -*-

import lldb
import re


def getImageOffset(image):
    cmd = 'image list -o -S %s' % image
    interpreter = lldb.debugger.GetCommandInterpreter()
    returnObject = lldb.SBCommandReturnObject()
    interpreter.HandleCommand(cmd, returnObject)
    output = returnObject.GetOutput();
    match = re.match(r'^\[.+\]\s(0x[0-9a-fA-F]+)', output)
    return int(match.group(1), 16) if match else None


def waitForRemoteTarget(image, debugger, port):
    debugger.HandleCommand('process connect connect://localhost:%d' % port)
    debugger.HandleCommand('process attach --waitfor --name %s' % image)


def addFunctionCmd(debugger, module, function, cmd):
    debugger.HandleCommand('command script add -f %s.%s %s' % (
        module, function, cmd
    ))
