###!/usr/bin/env python3

from telnetlib import Telnet
import time
import pandas as pd
import matplotlib.pyplot as plt
import re
import numpy as np

#ip = '10.73.97.65'
ip = '192.168.1.3'
port = 5024
something='LS-9dBm'
today=time.strftime("%m_%d")+'_'+time.strftime("%H_%M")+something
t=[] ## segundos
t0=time.time() 
time2=[]
data=[]

fig, ax=plt.subplots()
line, = ax.plot(t,data,'-o')
ax.set_ylabel('Power (dBm)', fontsize=14)
ax.set_xlabel('Time (s)', fontsize=14)
nn=np.arange(5.0,10.0,1)## valores de atenuacion
atten=[]
#plt.show()
tt=0
j=0
with Telnet(ip, port) as tn:
    ##unidad de medida
    tn.write(b'LINStrument13:UNIT1:POWer WATT nm\r\n')
    time.sleep(1)
    ## longitud de onda de medida : e1 - canal 1
    tn.write(b'LINStrument13:SENSe1:POWer:WAVelength 1550.00 nm\r\n')
    time.sleep(1)
    ##configuracion del promediado
    tn.write(b'LINStrument13:SENSe1:AVERage:STATe ON  nm\r\n')
    time.sleep(1)
    ##cantidad de muestras
    tn.write(b'LINStrument13:SENSe1:AVERage:COUNt 10  nm\r\n')
    time.sleep(1)
    ##lectura
    while True:
        tn.write(b'LINStrument13:READ1:SCALar:POWer:DC?\r\n')
        #tn.write(b'LINStrument13:SENSe1:POWer:WAVelength?\r\n')
        power=tn.read_until(b'\r\n').decode('utf-8').strip()
        match=re.search(r'READY> (-\d+\.\d+E[+-]?\d+)',power)
        print(power,time.time()-t0)
            
        if (tt%10==0):
            print(bytes('LINStrument12:INPut:ATTenuation {} dB\r\n'.format(nn[j]),encoding='utf8'))
            tn.write(bytes('LINStrument12:INPut:ATTenuation {} dB\r\n'.format(nn[j]),encoding='utf8'))
            j=j+1
        if match:
            power_db=float(match.group(1))
            data.append(power_db)
            time2.append(time.strftime("%H:%M:%S"))
            t.append(time.time()-t0)
            atten.append(nn[j])
            
            line.set_ydata(data)
            line.set_xdata(t)
            ax.relim()
            ax.autoscale_view()
                #plt.show()
                #print(power_db)
            df=pd.DataFrame({'Date':time2,'Time(s)':t,'Power(dB)':data,'atennuation(dB)':atten})
            filename='Data/'+'power_'+today
            df.to_csv(filename+'.csv',index=False)
            
        else:
            print('Wait')
           # ax.relim()
            #ax.autoscale_view()
        tt=tt+1
        plt.pause(1)
        