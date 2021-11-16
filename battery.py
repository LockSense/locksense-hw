from bluepy import btle 
import time


#p = btle.Peripheral("54:6C:0E:52:F3:2B")
start_batt=0
stop_batt=None
start_time=0
stop_time=None
p = None

def listen_batt(p):
 p.writeCharacteristic(int("0x001f",16),b"\x01\x00")
 
def read_batt(p):
 batt = 0
 batt = int.from_bytes(p.readCharacteristic(int("0x001e",16)),"big")
 return batt

def start_batt_recording(peri):
    global start_batt,start_time,p
    p=peri
    start_batt =read_batt(peri)
    start_time =time.time() 

def stop_batt_recording():
    global stop_batt,stop_time
    stop_batt=read_batt(peri)
    stop_time=time.time()

def calc_batt():
 global start_batt,start_time,stop_batt,stop_time
 if stop_time!=None:
  delta_batt =start_batt-stop_batt
  delta_time =stop_time-start_time
  print("The battery consumption (%):",(delta_batt/delta_time))
  #return string


#start_batt_recording()
#time.sleep(10)
#stop_batt_recording()
#calc_batt()
