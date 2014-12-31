#!/usr/bin/env python2

import sys
import signal
import pyvnc
import multiprocessing
from PIL import Image
import socket
import time

MAXPROCS = 30


def signal_cleanup(signal, frame):
    print 'SIGINT received. Cleaning up'
    for p in ps:
        p.join(0)
        if p.is_alive():
            p.terminate()
    sys.exit()

# Setting up signal handling
signal.signal(signal.SIGINT, signal_cleanup)

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

# List of running child processes
# The Pool module isn't used, because it isn't easy
# to kill a single child-processes
ps = []

line = sys.stdin.readline()
while line:
    if len(ps) >= MAXPROCS:
        # Too many running processes, we are stopping the
        # oldest one.
        print "Stopping old process"
        print len(ps)
        ps[0].join(10)
        if ps[0].is_alive():
            print 'Timeout for check'
            ps[0].terminate()
        del(ps[0])
    ip = line.strip()
    p = multiprocessing.Process(target=check, args=(ip,))
    p.start()
    ps.append(p)
    line = sys.stdin.readline()
