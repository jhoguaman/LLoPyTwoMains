import pycom
import time
from machine import I2C, RTC
#from multimain import MiClase

'''
pycom.heartbeat(False)
for cycles in range(0): # stop after 10 cycles
    pycom.rgbled(0x007f00) # green
    time.sleep(2)
    pycom.rgbled(0x7f7f00) # yellow
    time.sleep(1.5)
    pycom.rgbled(0x7f0000) # red
    time.sleep(1)
'''

i2c = I2C(0)                         # create on bus 0
i2c = I2C(0, I2C.MASTER)             # create and init as a master
i2c.init(I2C.MASTER, baudrate=100000) # init as a master

_SLAVE_ADDR=const(0x68)
_READ_DS3231=const(0x01)
_WRITE_DS3231=const(0x00)
_REG_CONTROL=const(0x0E)
_REG_STATUS=const(0x0F)

_REG_TEMP_LSB=const(0x11)
_REG_TEMP_MSB=const(0x12)




#################################--RTC-DS1307--#################################
def ds1307init_sinc():
    reloj_rtc_int=rtc.now()

    i2c.init()
    i2c.writeto(0x68,chr(0xD0))
    i2c.writeto(0x68,chr(0))
    i2c.writeto_mem(0x68,0,chr(int(decode_ds1307(str(reloj_rtc_int[5])))))
    i2c.writeto_mem(0x68,1,chr(int(decode_ds1307(str(reloj_rtc_int[4])))))
    i2c.writeto_mem(0x68,2,chr(int(decode_ds1307(str(reloj_rtc_int[3])))))
    i2c.writeto_mem(0x68,4,chr(int(decode_ds1307(str(reloj_rtc_int[2])))))
    i2c.writeto_mem(0x68,5,chr(int(decode_ds1307(str(reloj_rtc_int[1])))))
    i2c.writeto_mem(0x68,6,chr(int(decode_ds1307(str(reloj_rtc_int[0])[2:4]))))
    i2c.writeto_mem(0x68,_REG_CONTROL,0x00)
    i2c.deinit()

def decode_ds1307(valor_rtc_int):
    binstring = ''
    x=int(valor_rtc_int)
    while True:
        q, r = divmod(x, 10)
        nibble = bin(r).replace('0b', "")
        while len(nibble) < 4:
            nibble = '0' + nibble
        binstring = nibble + binstring
        if q == 0:
            break
        else:
            x = q
    valorhex = int(binstring, 2)
    return valorhex

def code_ds1307(valor_ds1307):
    valor=hex(ord(valor_ds1307))
    valor1= int(valor) & 15
    valor2= int(valor)>>4
    valorint= int(str(valor2)+str(valor1))
    return valorint

def obtener_ds1307():
    i2c.init()
    #data = ustruct.pack('>BBB', 0x01,channel,0x83)
    i2c.writeto(_SLAVE_ADDR,_READ_DS3231)

    segundos=i2c.readfrom_mem(0x68,0,1)
    minutos=i2c.readfrom_mem(0x68,1,1)
    horas=i2c.readfrom_mem(0x68,2,1)
    dia=i2c.readfrom_mem(0x68,4,1)
    mes=i2c.readfrom_mem(0x68,5,1)
    ann=i2c.readfrom_mem(0x68,6,1)

    segundosint= code_ds1307(segundos)
    minutosint=code_ds1307(minutos)
    horasint=code_ds1307(horas)
    diaint=code_ds1307(dia)
    mesint=code_ds1307(mes)
    annint=code_ds1307(ann)

    print(annint,mesint,diaint,horasint,minutosint,segundosint)
    i2c.deinit()

def temperature_DS3231():
    i2c.init()
    i2c.writeto(_SLAVE_ADDR,_READ_DS3231)

    TEM1=i2c.readfrom_mem(_SLAVE_ADDR,_REG_TEMP_LSB,1)
    TEM2=i2c.readfrom_mem(_SLAVE_ADDR,_REG_TEMP_MSB,1)
    print('temperature_DS3231:',bin(ord(TEM1)),bin(ord(TEM2)))

    i2c.deinit()

def sinc_RTC_ds1307():
    i2c.init()
    i2c.writeto(0x68,chr(0xD0))
    i2c.writeto(0x68,chr(0))
    i2c.writeto(0x68,chr(0xD1))
    segundos=i2c.readfrom_mem(0x68,0,1)
    segundosint= code_ds1307(segundos)
    minutos=i2c.readfrom_mem(0x68,1,1)
    minutosint=code_ds1307(minutos)
    horas=i2c.readfrom_mem(0x68,2,1)
    horasint=code_ds1307(horas)
    dia=i2c.readfrom_mem(0x68,4,1)
    diaint=code_ds1307(dia)
    mes=i2c.readfrom_mem(0x68,5,1)
    mesint=code_ds1307(mes)
    ann=i2c.readfrom_mem(0x68,6,1)
    annint=code_ds1307(ann)+2000
    rtc.init((annint, mesint, diaint, horasint, minutosint, segundosint, 0, 0),source=RTC.INTERNAL_RC)
    i2c.deinit()
    print('RTC-->LoPy',rtc.now())
##############################################################################

def clockSynchronization(dateTime):
    rtc.init(dateTime,source=RTC.INTERNAL_RC)
    print(rtc.now())

'''
rtc = RTC()
date='a1529668546'
dateTime=time.gmtime(int(date[1:]))
clockSynchronization(dateTime)
ds1307init_sinc()
'''


while True:
    #print(rtc.now())
    print(_SLAVE_ADDR)
    obtener_ds1307()
    temperature_DS3231()
    time.sleep(2)
