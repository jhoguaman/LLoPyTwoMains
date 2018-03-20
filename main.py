import pycom
import time
from network import WLAN
from machine import I2C, RTC
import ustruct
import pycom
import socket
import sys

pycom.heartbeat(False)
#from multimain import MiClase
host=''
port=80

#ec.pool.ntp.org (3)
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

_ADDR_DS3231=const(0x68)
_READ_DS3231=const(0x01)
_WRITE_DS3231=const(0x00)
_REG_CONTROL=const(0x0E)
_REG_STATUS=const(0x0F)

_REG_TEMP_MSB=const(0x11)
_REG_TEMP_LSB=const(0x12)

#################################--RTC-DS1307--#################################
def ds1307init_sinc():
    reloj_rtc_int=rtc.now()
    date = []
    for i in range(0, 6):
        if i==0:
            date.append(decode_ds1307(reloj_rtc_int[i]%100))
        else:
            date.append(decode_ds1307(reloj_rtc_int[i]))
    date = ustruct.pack('>'+'B'*8, 0x00,date[5],date[4],date[3],0x00,date[2],date[1],date[0])
    i2c.init()
    i2c.writeto(_ADDR_DS3231,_WRITE_DS3231)
    i2c.writeto(_ADDR_DS3231, date)
    i2c.writeto_mem(_ADDR_DS3231,_REG_CONTROL,0x00)
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
'''
def code_ds1307(valor_ds1307):
    valor=hex(ord(valor_ds1307))
    valor1= int(valor) & 15
    valor2= int(valor)>>4
    valorint= int(str(valor2)+str(valor1))
    return valorint
'''
def obtener_ds1307():
    i2c.init()
    i2c.writeto(_ADDR_DS3231,_READ_DS3231)
    fechaPrueba = i2c.readfrom_mem(_ADDR_DS3231,0,7)    #lee 7 registros desde el 0x00 al 0x06
    fechaVec = []
    for i in range(len(fechaPrueba)):
        valor1= fechaPrueba[i] & 15
        valor2= fechaPrueba[i] >> 4
        fechaVec.append(int(str(valor2)+str(valor1)))
    fechaVec[6]=fechaVec[6]+2000
    print(fechaVec[6],fechaVec[5],fechaVec[4],fechaVec[2],fechaVec[1],fechaVec[0])
    i2c.deinit()
    return fechaVec

def temperature_DS3231():
    i2c.init()
    i2c.writeto(_ADDR_DS3231,_READ_DS3231)
    TEM1=i2c.readfrom_mem(_ADDR_DS3231,_REG_TEMP_MSB,1)  #11h
    TEM2=i2c.readfrom_mem(_ADDR_DS3231,_REG_TEMP_LSB,1)  #12h
    TEM1 = (int(ord(TEM1))) << 2
    TEM2 = (int(ord(TEM2))) >> 6
    TEMP = TEM1 | TEM2
    if TEMP >> 9:
        print('negativo')
    else:
        print('TEMP:',TEMP*0.25)
    i2c.deinit()

def sinc_RTC_ds1307():
    fechaVec=obtener_ds1307()
    rtc.init((fechaVec[6],fechaVec[5],fechaVec[4],fechaVec[2],fechaVec[1],fechaVec[0], 0, 0),source=RTC.INTERNAL_RC)
    print('RTC3231 to LoPy',rtc.now())
##############################################################################

def clockSynchronization(dateTime):
    rtc.init(dateTime,source=RTC.INTERNAL_RC)
    print(rtc.now())

###########################----calibrationType----##############################
#Llamado desde el method:wifi, redirecciona a los métodos:
    #h0Calibration:             Calibra P1
    #h1Calibration:             Calibra P2
    #clockSynchronizationApp:   Sincroniza el reloj del LoPy con la app.
    #restoreConfigFile:         Elimina el config generado por la app.
    #levelWaterUpdate:          Envía a la app nos niveles de agua
    #finishCalibration:         Finaliza la conexión con la app.
def calibrationType(argCalibration):
    print('argCalibration: ', argCalibration[0])
    switcher = {
        97: h0Calibration,
        98: h1Calibration,
        99: finishCalibration,
        100: clockSynchronizationApp,
        101:restoreConfigFile,
        102:levelWaterUpdate,
        103:Files,
        104:downloadFiles,
    }
    func = switcher.get(argCalibration[0])       # Get the function from switcher dictionary
    return func(argCalibration)                  # Execute the function
#############################----h0Calibration----##############################
#almacena el valor de P1: P1(vMin,0).
def h0Calibration(none):
    ads1115Write(_CHANNEL0)
    vMin=ads1115Read()
    p1=ustruct.pack('HH',vMin,0)
    writeFile(pathConfigFile,'wb',2,p1)
    msg='Calibración de P1 realizada con éxito'
    return True, msg
##############################----h1Calibration----#############################
#almacena el valor de P2: P2(Vx,hx)
def h1Calibration(hx):
    ads1115Write(_CHANNEL0)
    v1=ads1115Read()
    p1=readFile(pathConfigFile,'rb',2) #tupla binaria con p1
    p1=ustruct.unpack('HH',p1)
    config=ustruct.pack('HHHH',p1[0],p1[1],v1,int(hx[1:]))
    writeFile(pathConfigFile,'wb',2,config)
    msg='Calibración de P2 realizada con éxito'
    return True,msg
#########################----clockSynchronizationApp----########################
def clockSynchronizationApp(date):
    dateTime=time.gmtime(int(date[1:]))
    msg='Fecha Actualizada'
    clockSynchronization(dateTime)
    ds1307init_sinc()
    return True,msg
############################----restoreConfigFile----###########################
def restoreConfigFile(none):
    if len(os.listdir('/flash/configFile'))==1:
        msg='Actualmente se ejecuta con la configuración de Fabrica'
    else:
        os.remove(pathConfigFile+'2')
        msg='Restaurado a configuración de Fabrica'
    return True,msg
#############################----levelWaterUpdate----###########################
def levelWaterUpdate(none):
    ads1115Write(_CHANNEL0)
    vX=ads1115Read()
    config=configFile()
    equationParameters=slope(config)
    hX=waterLevel(equationParameters,vX)
    print(hX)
    tStamp=rtc.now()
    print(tStamp[:6])
    tStamp=str(tStamp[0])+'-'+str(tStamp[1])+'-'+str(tStamp[2])+'*'+str(tStamp[3])+':'+str(tStamp[4])+':'+str(tStamp[5])
    msg=str(hX)
    msg=msg+'[mm]*'+tStamp
    return True,msg

##############################----Files----#############################
def Files(pathLogs):
    pathLogs=str(pathLogs[1:])
    logsStore=os.listdir(pathLogs[2:len(pathLogs)-1])
    i=0
    msg=''
    for i in range(i,len(logsStore)):
        msg=msg+logsStore[i]+'!'
        i+=1
    msg=str(msg)
    return True,msg

##############################----downloadFiles----#############################
def downloadFiles(numFile):
    numFile=int(numFile[1:])
    print('Listo para descarga de archivos')
    print(numFile, os.listdir('logsDir'), os.listdir('logsDir')[numFile])

    dFile=readFile('logsDir/','rb',(os.listdir('logsDir')[numFile]))
    print(dFile)

    msg=dFile
    return True,msg

############################----finishCalibration----###########################
def finishCalibration(none):
    msg='Finish wifi LoPy'
    pycom.rgbled(False)
    return False,msg

##################################----WiFi----##################################
#Activa el WiFi ssid:waterLevel, clave: ucuenca1234.
#Parámetros del socket con ipServer:"host" y puerto:"port" (definidos al inicio)
#luego del proceso de calibración se desactiva el wifi.
def wifi():
    print('wifi init')
    pycom.rgbled(0x009999) # blue
    wlan = WLAN(mode=WLAN.AP, ssid='waterLevel', auth=(WLAN.WPA2,'ucuenca1234'), channel=7, antenna=WLAN.INT_ANT)
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        serversocket.bind(socket.getaddrinfo(host,port)[0][-1])     #ipServer 192.168.4.1
    except Exception as e:
        print('bind failed, error code: ',str(e[0]))
        sys.exit()
    serversocket.listen(1)
    print('socket is now listening over port: ', port)

    wifiSocket=True
    while (wifiSocket):
        print('socket init')
        sc, addr = serversocket.accept()
        print('sc: ',sc,' addr: ',addr)
        recibido = sc.recv(16)
        print('valor recibido :', recibido)
        print('dato[0]: ',recibido[0])
        wifiSocket, msg=calibrationType(recibido)
        sc.send(msg)
    print('closing wifi and socket')
    sc.close()
    serversocket.close()
    wlan.deinit()

'''
rtc = RTC()
date='a1521567462'
dateTime=time.gmtime(int(date[1:]))
clockSynchronization(dateTime)
ds1307init_sinc()
'''

#wifi()

#sinc_RTC_ds1307()
#ds1307init_sinc()
while True:
    #print(rtc.now())
    obtener_ds1307()
    #temperature_DS3231()
    time.sleep(1)
