from bluepy import btle
import struct
import time
import wave
from struct import unpack,pack


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

def tic1_DecodeSingle(nibble):
    global SI_Dec
    global PV_Dec
    #print("length of my step size..........",len(tic1_stepsize_Lut))
    step = tic1_stepsize_Lut[SI_Dec]
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

decoded = bytearray()
byte_buf = ''
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
    bb = bytearray(decoded)
    filename = time.strftime("pdm_test_%Y-%m-%d_%H-%M-%S_adpcm")

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
    decoded = []
    missedFrames = 0

inbuffer=bytearray()
noti_count=0
frame_count=0
class MyDelegate(btle.DefaultDelegate):
    def __init__(self):
         btle.DefaultDelegate.__init__(self)
         

    def handleNotification(self, cHandle, data):
        global inbuffer,noti_count,SI_Dec,PV_Dec,frame_count
        #print("each data type is............",type(data))
        inbuffer+=bytearray(data)
        
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
        if frame_count ==600: #600 frame count corresponds to ~0.06 second
         save_wav()
         frame_count=0
        # ... perhaps check cHandle
        # ... process 'data'


# Initialisation  -------
p = btle.Peripheral("54:6C:0E:52:F3:2B")
p.setDelegate( MyDelegate() )

# Setup to turn notifications on, e.g.
#chs=srvs[2].getCharacteristics();
#ch=chs[1];

p.writeCharacteristic(int("0x002f",16),b"\x01\x00")
p.writeCharacteristic(int("0x0032",16),b"\x01\x00")

# Main loop --------

while True:
    if p.waitForNotifications(1.0):
        # handleNotification() was called
        continue

    print ("Waiting...")
    # Perhaps do something else here
