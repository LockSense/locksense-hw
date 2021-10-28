import numpy
import sys
import time
import wave 
import os
from serial import Serial,SerialException 

def get_script_path():
 return os.path.dirname(os.realpath(sys.argv[0]))


def save_file(data):
 filename = time.strftime("pdm_test_%Y-%m-%d_%H-%M-%S_pcm")
 print("................saving file........")
 w = wave.open("./samples/" + filename + ".wav", "w")
 w.setnchannels(1)
 w.setframerate(16000)
 w.setsampwidth(2)
 w.writeframes(data)
 w.close()
 print("......done...")

try:
 ser = None
 ser = Serial("COM3",256000,timeout=0.1)
 pcmdata = bytearray()
  
 frame = 0
 while True:
  indata = ser.read(384)
  pcmdata+=bytearray(indata)
    
  #print(type(pcmdata))
  #pcmdata.append(arr) 

  #collect 1000 frames
  if frame == 200 :
   #pcmdata.reverse()
   save_file(pcmdata)
   frame=0
  else:
   frame+=1
   print(frame)

     
except SerialException as e:
 print("Serial port error")
 print(e)
finally:
 if set is not None: ser.close()  




