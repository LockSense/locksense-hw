from bluepy import btle
import struct
import time
import time 
import wave
from struct import unpack,pack
import battery as bt
import paho.mqtt.client as mqtt 
import json

##---------------Global Variables---------------
tic1_stepsize_Lut = [
  7,    8,    9,   10,   11,   12,   13,   14, 16,   17,   19,   21,   23,   25,   28,   31,
  34,   37,   41,   45,   50,   55,   60,   66, 73,   80,   88,   97,  107,  118,  130,  143,
  157,  173,  190,  209,  230,  253,  279,  307, 337,  371,  408,  449,  494,  544,  598,  658,
  724,  796,  876,  963, 1060, 1166, 1282, 1411, 1552, 1707, 1878, 2066, 2272, 2499, 2749, 3024,
  3327, 3660, 4026, 4428, 4871, 5358, 5894, 6484, 7132, 7845, 8630, 9493,10442,11487,12635,13899,
  15289,16818,18500,20350,22385,24623,27086,29794, 32767
]

tic1_IndexLut = [
  -1, -1, -1, -1, 2, 4, 6, 8,
  -1, -1, -1, -1, 2, 4, 6, 8
]

buf = bytearray()
framecount=0
SI_Dec = 0
PV_Dec = 0
decoded = bytearray()
byte_buf = ''
inbuffer=bytearray()
noti_count=0
frame_count=0
p=None 

def tic1_DecodeSingle(nibble):
    global SI_Dec
    global PV_Dec
    #print("length of my step size..........",len(tic1_stepsize_Lut))
    if SI_Dec <=89:
     step = tic1_stepsize_Lut[SI_Dec]
    else:
     step=0
    cum_diff  = step>>3;

    SI_Dec += tic1_IndexLut[nibble];

    if SI_Dec < 0:
        SI_Dec = 0
    if SI_Dec > 88:
        SI_Dec = 88;

    if nibble & 4:
        cum_diff += step
    if nibble & 2:
        cum_diff += step>>1
    if nibble & 1:
        cum_diff += step>>2;

    if nibble & 8:
        if PV_Dec < (-32767+cum_diff):
           PV_Dec = -32767
        else:
            PV_Dec -= cum_diff
    else:
        if PV_Dec > (0x7fff-cum_diff):
            PV_Dec = 0x7fff
        else:
            PV_Dec += cum_diff

    return PV_Dec;

def decode_adpcm(_buf):
    global decoded
    global buf
    global SI_Dec
    global PV_Dec

    for b in _buf:
     #b,= unpack('B',byte(b))
     decoded+=(pack('h', tic1_DecodeSingle(b & 0xF)))
     decoded+=(pack('h', tic1_DecodeSingle(b >> 4)))

def save_wav():
    global decoded
    print("saving file.................")
    filename = time.strftime("pdm_test_%Y-%m-%d_%H-%M-%S_adpcm")
    client.publish("Audio/Sensor1/Data",decoded)
    bb = bytearray(decoded)

    print ("...................saving file")
    w = wave.open("samples/"+filename + ".wav", "w")
    w.setnchannels(1)
    w.setframerate(16000)
    w.setsampwidth(2)
    w.writeframes(bb)
    w.close()
    print (".................DONE...")
    #clear stuff for next stream
    SI_Dec = 0
    PV_Dec = 0
    decoded=bytearray()
    #bb=bytearray()
    missedFrames = 0
    
    
class MyDelegate(btle.DefaultDelegate):
 def __init__(self):
  btle.DefaultDelegate.__init__(self)


 def handleNotification(self, cHandle, data):
  global inbuffer,noti_count,SI_Dec,PV_Dec,frame_count,p
  #print("each data type is............",type(data))
  inbuffer+=bytearray(data)
  if cHandle==49:
   if len(inbuffer)>=20:
    if noti_count==0: #first notification
     seqNum, SI_received, PV_received = struct.unpack('BBh', inbuffer[0:4])
     seqNum = (seqNum >> 3)
     print ("Frame sequence number: %d" % seqNum)
     PV_Dec = PV_received
     SI_Dec = SI_received
     #print ("HDR_1 local: %d, HDR_1 received: %d" % (SI_Dec, SI_received))
     #print ("HDR_2 local: %d, HDR_2 received: %d" % (PV_Dec, PV_received))
     decode_adpcm(inbuffer[4:])
     noti_count+=1
    elif noti_count==4: #last notification
     frame_count +=1
     noti_count=0
     inbuffer=bytearray()
    else:
     decode_adpcm(data)
     noti_count+=1
   if frame_count ==108: #600 frame count corresponds to 6 seconds of recording
    print(frame_count)
    frame_count=0
    save_wav()
    batt = bt.read_batt(p)
    with open("log.txt","a") as f:
     audio_recording_done = time.strftime("%H-%M-%S")
     f.write("RECORDING DONE @ "+audio_recording_done+ " BATTERY LEVEL @ "+str(batt)+"\n")
    
  elif cHandle==30:
    with open("log.txt","a") as f:
     battery_level = time.strftime("%H-%M-%S")
     f.write("Battery level @ "+battery_level+" "+str(int.from_bytes(data,"big"))+"\n")
  else:
    print("INCOMING HANDLE: ",cHandle)
    
def on_buzzer():
    p.writeCharacteristic(int("0x002b",16),b"\x01")

def off_buzzer():
    p.writeCharacteristic(int("0x002b",16),b"\x00")
        
    
def connect_ble():
 global p
 print("Connecting to BLE Sensortag...")
 #p = btle.Peripheral("54:6C:0E:52:F3:2B")
 p = btle.Peripheral("F0:F8:F2:86:B9:85")
 print("Connected!")
 p.setDelegate( MyDelegate() )

 p.writeCharacteristic(int("0x002f",16),b"\x01\x00")
 p.writeCharacteristic(int("0x0032",16),b"\x01\x00")
 bt.listen_batt(p)
 client.loop_start()
 while True:
  if p.waitForNotifications(1.0):
     # handleNotification() was called
     continue
  print ("Waiting...")
  
 client.loop_end()

def on_connect(client, userdata,flags,rc):
    print("Connected to MQTT with result code: "+str(rc))
    #client.subscribe("door1/verdict")
    client.publish("Audio/Sensor1/Start","Sensor 1 is connected to Audio Broker")

def on_message(client,userdata,msg):
    recv_dict = json.loads(msg.payload)
    val = recv_dict["response"]
    print("VERDICT VALUES === ",val)
    if val == 0:
        on_buzzer()
        time.sleep(1)
        off_buzzer()
    else:
        off_buzzer()
    return
    
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
#client.connect("localhost",1883,60)
client.username_pw_set("rabbits", "cutebunnies:)")
client.tls_set()
client.connect("locksense.dorcastan.com", 8883, 60)
connect_ble()
#client.loop_forever()
