#!/usr/bin/python
# python 3.1.3
# subnets resolver.
# This program calculates ip range addresses, subnet net masks,
# subnets broadcasts ips 
# Written by Doctor G (Dr@G)
# 
import os
import sys
from math import *

#---------------general functions--------------

#---------------clear screen function----------

def gcls(nl=100):
    if os.name =='posix':
        os.system("clear")
    elif os.name in ("nt", "dos", "ce"):
        os.system("cls")
    else:
        print('\n' * nl)

#--------------restart program function--------

def restart():
    python = sys.executable
    os.execl(python, python, * sys.argv)


#-----------------constant values--------------

Bit_List=[128,64,32,16,8,4,2,1]
gcls()

try:
    

    #------------------input-----------------------
    print('-----------------------------------')
    print('Subnet Resolver By Doctor G (Dr@G)')
    print('-----------------------------------')
    NIP=input('IP Number         : ')
    print('-----------------------------------')
    NumSubnets=int(input('Number of Subnets : '))
    print('-----------------------------------')
    NumHosts=int(input('Number of Hosts   : '))
    NIP_List=NIP.split('.')
    
        
    #----------specific program functions----------

    def Number_Of_Subnets(NumSub):
        for i in range(1,200):
            cur_i=2**i-2
            if cur_i<NumSubnets:
                pass
            else:
                return cur_i,i

    def Subnet_Bits():
        return Number_Of_Subnets(NumSubnets)[1]

    def Hosts_Bits():
        return 8-Subnet_Bits()

    def Number_Of_Hosts():
        return 2**(Hosts_Bits())-2

    def Class_Estimation():
        if int(NIP_List[0])>=1 and int(NIP_List[0])<=126:
            return 'A'
        if int(NIP_List[0])>=128 and int(NIP_List[0])<=191:
            return 'B'
        if int(NIP_List[0])>=192 and int(NIP_List[0])<=223:
            return 'C'

    def General_Netmask():
        if Class_Estimation()=='A':
            return '255.0.0.0'
        if Class_Estimation()=='B':
            return '255.255.0.0'
        if Class_Estimation()=='C':
            return '255.255.255.0'

    def General_Network_Mask():
        if Subnet_Bits()==1:
            return 128
        if Subnet_Bits()==2:
            return 192
        if Subnet_Bits()==3:
            return 224
        if Subnet_Bits()==4:
            return 240
        if Subnet_Bits()==5:
            return 248
        if Subnet_Bits()==6:
            return 252
        if Subnet_Bits()==7:
            return 254
        if Subnet_Bits()==8:
            return 255

    def Special_Network_Mask():
        Temp_List=General_Netmask().split('.')
        Temp_List[3]=str(General_Network_Mask())
        netmask=Temp_List[0]+'.'+Temp_List[1]+'.'+Temp_List[2]+'.'+Temp_List[3]
        return netmask

    def perms(n):
        if not n:
            return

        for i in range(2**n):
            s = bin(i)[2:]
            s = "0" * (n-len(s)) + s
            yield s
        
    Binary_List=list(perms(Subnet_Bits()))

    def make_list():
        newlist=[]
        for i in range(0,len(Binary_List)-1):
            newlist.append(list(Binary_List[i]))
        newlist.pop(0)
        return newlist

    def IPs():
        ip=0
        bit=[]
        iptable=[]
        for i in range(0,Subnet_Bits()):
            bit.append(Bit_List[i])
        for j in range(0,len(make_list())):
            ip=0
            for k in range(0,Subnet_Bits()):
                ip=ip+int(make_list()[j][k])*bit[k]
            iptable.append(ip)
        return iptable

    def Subnets_IPs():
        newipslist=[]
        for i in range(0,len(IPs())):
            newipslist.append(str(i+1)+') '+ NIP_List[0]+'.'+NIP_List[1]+'.'+NIP_List[2]+'.'+str(IPs()[i]))
        return newipslist

    def Resolve_Networks_Broadcast_Addresses():
        newlist=[]
        if Hosts_Bits()==8:
            for i in range(0,len(IPs())):
                newlist.append(IPs()[i]+255)
            return newlist
        if Hosts_Bits()==7:
            for i in range(0,len(IPs())):
                newlist.append(IPs()[i]+127)
            return newlist
        if Hosts_Bits()==6:
            for i in range(0,len(IPs())):
                newlist.append(IPs()[i]+63)
            return newlist
        if Hosts_Bits()==5:
            for i in range(0,len(IPs())):
                newlist.append(IPs()[i]+31)
            return newlist
        if Hosts_Bits()==4:
            for i in range(0,len(IPs())):
                newlist.append(IPs()[i]+15)
            return newlist
        if Hosts_Bits()==3:
            for i in range(0,len(IPs())):
                newlist.append(IPs()[i]+7)
            return newlist
        if Hosts_Bits()==2:
            for i in range(0,len(IPs())):
                newlist.append(IPs()[i]+3)
            return newlist
        if Hosts_Bits()==1:
            for i in range(0,len(IPs())):
                newlist.append(IPs()[i]+1)
            return newlist

    def Broadcast_IPs():
        newbroadcastipslist=[]
        for i in range(0,len(Resolve_Networks_Broadcast_Addresses())):
            newbroadcastipslist.append(str(i+1)+') '+ NIP_List[0]+'.'+NIP_List[1]+'.'+NIP_List[2]+'.'+str(Resolve_Networks_Broadcast_Addresses()[i]))
        return newbroadcastipslist

    def Print_IP_Range():
        list=[]
        for i in range(0,len(IPs())):
            list.append(str(i+1)+') '+ NIP_List[0]+'.'+NIP_List[1]+'.'+NIP_List[2]+'.'+str(IPs()[i]+1)+' - '+NIP_List[0]+'.'+NIP_List[1]+'.'+NIP_List[2]+'.'+str(Resolve_Networks_Broadcast_Addresses()[i]-1))
            print(list[i])

    def Valid_IP_Address_Ranges():
        newlowrangeiplist=[]
        newhighrangeiplist=[]
        for i in range(0,len(IPs())):
            newlowrangeiplist.append(IPs()[i]+1)
        for j in range(0,len(Resolve_Networks_Broadcast_Addresses())):
            newhighrangeiplist.append(Resolve_Networks_Broadcast_Addresses()[j]-1)
        return newlowrangeiplist,newhighrangeiplist

    def LowRangeIP():
        newlowlist=[]
        for i in range(0,len(Resolve_Networks_Broadcast_Addresses())):
            newlowlist.append(str(i+1)+') '+ NIP_List[0]+'.'+NIP_List[1]+'.'+NIP_List[2]+'.'+str(Valid_IP_Address_Ranges()[0][i]))
        return newlowlist

    def HighRangeIP():
        newhighlist=[]
        for i in range(0,len(Resolve_Networks_Broadcast_Addresses())):
            newhighlist.append(str(i+1)+') '+ NIP_List[0]+'.'+NIP_List[1]+'.'+NIP_List[2]+'.'+str(Valid_IP_Address_Ranges()[1][i]))
        return newhighlist

    def AllRangeIPs():
        newlist=[]
        for i in range(0,len(Resolve_Networks_Broadcast_Addresses())):
            newlist.append(LowRangeIP()[i]+' - '+HighRangeIP()[i])
        return newlist

    def Print_Subnets_IPs():
        for i in range(0,len(Subnets_IPs())):
            print(Subnets_IPs()[i])

    def Print_Broadcast_IPs():
        for i in range(0,len(Broadcast_IPs())):
            print(Broadcast_IPs()[i])

    def Print_Valid_IP_Ranges():
        for i in range(0,len(AllRangeIPs())):
            print(AllRangeIPs()[i])
            
    #--------------Valid IP checker------------
    
    def ValidIP():
        for i in range(0,3):
            if int(NIP_List[i])>=255:
                restart()
            if int(NIP_List[i])<0:
                restart()

    ValidIP()

    #---------------Results--------------------
            
    print('-----------------------------------')
    print('Subnets           :',Number_Of_Subnets(NumSubnets)[0])
    print('-----------------------------------')
    print('Hosts             :',Number_Of_Hosts())
    print('-----------------------------------')
    print('Class             :',Class_Estimation())
    print('-----------------------------------')
    print('Network Mask      :',Special_Network_Mask())
    print('-----------------------------------')
    print('Subnetwork Addresses')
    print('-----------------------------------')
    Print_Subnets_IPs()
    print('-----------------------------------')
    print('Subnetwork Broadcast Addresses')
    print('-----------------------------------')
    Print_Broadcast_IPs()
    print('-----------------------------------')
    print('Valid Host IP Ranges')
    print('-----------------------------------')
    Print_IP_Range()
    print('-----------------------------------')

except:
    if KeyboardInterrupt:
        gcls()
        sys.exit(0)
    else:
        gcls()
        restart()
    

