import numpy
import sys
import time
import wave 
import os
from serial import Serial,SerialException 

def get_script_path():
 return os.path.dirname(os.realpath(sys.argv[0]))


device_name = "COM3"

baudrate = 256000
bytes_per_read = 16000
framerate = 16000
num_seconds = 32

# bits_per_symbol = 1 # Not sure about this
# bytes_per_second = baudrate * bits_per_symbol / 8
# num_frames = int(bytes_per_second * num_seconds / bytes_per_read)
num_frames = int(framerate * num_seconds / bytes_per_read)

def save_file(data):
 filename = time.strftime("pdm_test_%Y-%m-%d_%H-%M-%S_pcm")
 print("................saving file........")
 w = wave.open("./samples/" + filename + ".wav", "w")
 w.setnchannels(1)
 w.setframerate(framerate)
 w.setsampwidth(2)
 w.writeframes(data)
 w.close()
 print("......done...")

try:
 ser = None
 ser = Serial(device_name,baudrate,timeout=None)
 pcmdata = bytearray()
  
 frame = 0
 while True:
  indata = ser.read(bytes_per_read)
  pcmdata+=bytearray(indata)
    
  #print(type(pcmdata))
  #pcmdata.append(arr) 

  #collect 1000 frames
  if frame == num_frames:
   #pcmdata.reverse()
   save_file(pcmdata)
   break

  print(frame)
  frame+=1

     
except SerialException as e:
 print("Serial port error")
 print(e)
finally:
 if set is not None: ser.close()  




