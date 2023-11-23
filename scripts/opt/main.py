# -*- coding: utf-8 -*-
"""
Created on Wed Nov 22 16:37:01 2023

@author: kelvin
"""

import json 
import requests
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import time
from telnetlib import Telnet
import re

#from gnuplot import plot
#%matplotlib tk
t_mxc=[] ## mxc temperature
data_p=[]
t = [] ## time
time2=[]
atten=[]

fig, ax = plt.subplots(2,2,figsize=(8,14))
line, = ax[0,0].plot(t, t_mxc, '-o')
line1, = ax[0,1].plot(t,data_p, '-o')
line2, = ax[1,0].plot(t_mxc,data_p, '-o')
line3, = ax[1,1].plot(t,atten, '-o')
ax[0,0].set_ylabel('Temperature (K)', fontsize=14)
ax[0,0].set_xlabel('Time (s)', fontsize=14)
ax[0,1].set_ylabel('Power (dBm)', fontsize=14)
ax[0,1].set_xlabel('Time (s)', fontsize=14)
ax[1,0].set_ylabel('Power(dBm)', fontsize=14)
ax[1,0].set_xlabel('Temperature(K)', fontsize=14)
ax[1,1].set_ylabel('Attenuation(dB)', fontsize=14)
ax[1,1].set_xlabel('Time(s)', fontsize=14)
plt.suptitle("Temperature and Power", fontsize=18)
ip = '192.168.1.3'
port = 5024
something='LS-9dBm'
today=time.strftime("%m_%d")+'_'+time.strftime("%H_%M")+something

t0=time.time() 
nn=np.linspace(6,0,3)## valores de atenuacion

#plt.show()
tt=0
j=0
step=600 #3600 ## temperarute saturation
#plt.show()
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
        if (tt%step==0):
            print(bytes('LINStrument12:INPut:ATTenuation {} dB\r\n'.format(nn[j+1]),encoding='utf8'))
            tn.write(bytes('LINStrument12:INPut:ATTenuation {} dB\r\n'.format(nn[j+1]),encoding='utf8'))
            j=j+1
        match=re.search(r'READY> (-\d+\.\d+E[+-]?\d+)',power)
        req= requests.get("http://192.168.1.1:5001/channel/measurement/latest", timeout=10)
        data = req.json()    
        print(power)
        if match:
            if data.get('channel_nr')==6:
                power_db=float(match.group(1))
                data_p.append(power_db)
                t_mxc.append(data.get('temperature'))
                time2.append(time.strftime("%H:%M:%S"))
                atten.append(nn[j])
                t.append(time.time()-t0)
            
                line.set_ydata(t_mxc)
                line.set_xdata(t)
                line1.set_ydata(data_p)
                line1.set_xdata(t)
                line2.set_ydata(data_p)
                line2.set_xdata(t_mxc)
                line3.set_ydata(atten)
                line3.set_xdata(t)
                ax[0,0].relim()
                ax[0,0].autoscale_view()
                ax[0,1].relim()
                ax[0,1].autoscale_view()
                ax[1,0].relim()
                ax[1,0].autoscale_view()
                ax[1,1].relim()
                ax[1,1].autoscale_view()
            else:
                power_db=float(match.group(1))
                data_p.append(power_db)
                t_mxc=t_mxc+[t_mxc[-1]]
                atten.append(nn[j])
                t.append(time.time()-t0)
                time2.append(time.strftime("%H:%M:%S"))
                
                line.set_ydata(t_mxc)
                line.set_xdata(t)
                line1.set_ydata(data_p)
                line1.set_xdata(t)
                line2.set_ydata(data_p)
                line2.set_xdata(t_mxc)
                line3.set_ydata(atten)
                line3.set_xdata(t)
                ax[0,0].relim()
                ax[0,0].autoscale_view()
                ax[0,1].relim()
                ax[0,1].autoscale_view()
                ax[1,0].relim()
                ax[1,0].autoscale_view()
                ax[1,1].relim()
                ax[1,1].autoscale_view()
            #plt.show()
            #print(power_db)
            df=pd.DataFrame({'Date':time2,'Time(s)':t,'Power(dB)':data_p, 'Temp(K)':t_mxc,'atennuation(dB)':atten})
            filename='Data/'+'power_'+today
            df.to_csv(filename+'.csv',index=False)
            
        else:
            print('Wait')
        tt=tt+1
        plt.pause(1)
        # ax.relim()
       # ax.autoscale_view()
        
                          