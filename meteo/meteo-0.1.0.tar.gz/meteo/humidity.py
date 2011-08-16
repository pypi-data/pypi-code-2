#!/usr/bin/python
# Filename: radiation.py

# Description:
# conversions between different humidity quantities

Mw=18.0160 # molecular weight of water
Md=28.9660 # molecular weight of dry air

#saturation pressure
def esat(T):
    TK = 273.15
    e1 = 1013.250
    logTTK = log10(T/TK)
    esat =  e1*10**(10.79586*(1-TK/T)-5.02808*logTTK+ 1.50474*1e-4*(1.-10**(-8.29692*(T/TK-1)))+ 0.42873*1e-3*(10**(4.76955*(1-TK/T))-1)-2.2195983) 
    return esat

# conversion relative humidity to mixing ratio
def rh2mixr(RH,p,T):
    es = esat(T)
    return Mw/Md*RH/100.*es/(p-RH/100.*es)*1000.

# conversion mixing ratio to specific humidity
def mixr2sh(W):
    return W/(1.+W/1000.)
def ea2mixr(P,ea):
    return 0.622* ea/(P-ea)


