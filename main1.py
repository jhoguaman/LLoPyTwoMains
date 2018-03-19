'''
import pycom
import time
pycom.heartbeat(False)
for cycles in range(1): # stop after 10 cycles
    pycom.rgbled(0x007f00) # green
    time.sleep(2)
    pycom.rgbled(0x7f7f00) # yellow
    time.sleep(1.5)
    pycom.rgbled(0x7f0000) # red
    time.sleep(1)
'''

dato=0x80 #19
dato2=0x40 #40

dato=chr(dato)
dato2=chr(dato2)



dato=int(ord(dato))
#dato=int(dato,0)



dato2=int(ord(dato2))
#dato2=int(dato2,0)
#print('dato2',bin(dato2)[2:].zfill(10) )
#msb=bin(dato << 2)
#lsb=bin(dato2 >> 6)

msb=(dato << 2)
lsb=(dato2 >> 6)



#print(dato,bin(dato << 2),bin(dato2>>6))
print(msb,lsb)

#tempe=int(msb,2) | int(lsb,2)
tempe=(msb) | (lsb)

print('tempe',bin(tempe),tempe*0.25)

sig=tempe >> 9

print ('sig',(sig))

if tempe >> 9:
    x=9
    print(bin(x),~x,bin(x),bin(~x))
    print('negativo',(tempe & 0x1ff))
    print((bin(~(tempe & 0x1ff))))
    print(bin(~(tempe)),-tempe-1)

else:
    print('positivo')

a = []

a.append('sdf')
a.append(18)

a[1]=a[1]+2000

#a[1]='sdfff'
print(a[1])
#print('hello')
#print(bin(int(msb,2)) or bin(int(lsb,2)))
#print(100 or 1)
#print(101*.25)

#Returns False
#for i in range(8):
#    print((b'a'[0] >> i) & 1)
