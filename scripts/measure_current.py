import labrad
import numpy as np
import time
import matplotlib.pyplot as plt
from labrad.units import WithUnit as U

#---parameters---#
iterations = 600*60*15
wait_time = .1

#---script---#
cxn = labrad.connect('192.168.169.30')
dmm = cxn.keithley_2100_dmm
dmm.select_device('GPIB Bus - USB0::0x05E6::0x2100::1243106')
cxnlocal = labrad.connect()
dv = cxnlocal.data_vault

localtime = time.localtime()
dirappend = [ time.strftime("%Y%b%d",localtime) ,time.strftime("%H%M_%S", localtime)]
direc = ['', 'Experiments', 'CoilCurrentStability', 'Keithley']
direc.extend(dirappend)
dv.cd(direc, True)
dv.new('Coil current', [('Time', '100 ms')], [('Current', 'A', 'A')] )
dv.add_parameter('Window', 'Coil current')
#dv.add_parameter('plotLive', True)
for i in range(iterations):
    v = dmm.get_dc_amps()
    cur = U(v, 'A')
    t = U(i * 0.1, 's')
    dv.add((t, cur))
    time.sleep(wait_time)

#print y
