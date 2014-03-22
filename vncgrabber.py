#!/usr/bin/env python2

import sys
import pyvnc
import multiprocessing
from PIL import Image
import socket
import time

def check(ip):
    hostname = 'Unknown'
    try:
        hostname = socket.gethostbyaddr(ip)[0]
    except:
        pass
    print 'Trying %s (%s) ' % (ip, hostname)
    c = pyvnc.pyvncclient()
    cret = c.connect(ip, 0, '')
    print 'Connect returned %d' % cret
    if(cret == -1):
        return
    print 'CONNECTED to: %s' % c.servername
    print 'State is %d geometry is %dx%d' % (c.state, c.width, c.height)
    # Try to interrupt screensaver
    c.sendmouseevent(10,10,0)
    c.sendkeyevent(pyvnc.Control_L, 1)
    c.sendmouseevent(1,1,0)
    c.sendkeyevent(pyvnc.Control_L, 0)
    time.sleep(1)

    c.checkforupdates(1.0)
    print 'updatedarea =', c.updatedarea()

    im = Image.fromstring('RGBX', (c.width, c.height), c.getbuffer())
    im = im.convert('RGB')
    im.save(ip+'.png')
    print 'IMAGE %s.png saved' % ip
    c.clearupdates

    return


line = sys.stdin.readline()
while line:
    ip = line.strip()
    p = multiprocessing.Process(target=check, args=(ip,))
    p.start()
    p.join(10)
    if p.is_alive():
        print 'Timeout from %s' % ip
        p.terminate()
    line = sys.stdin.readline()
