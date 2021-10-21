'''
/*
 * Copyright (c) 2016-2020, Texas Instruments Incorporated
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 *
 * *  Redistributions of source code must retain the above copyright
 *    notice, this list of conditions and the following disclaimer.
 *
 * *  Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in the
 *    documentation and/or other materials provided with the distribution.
 *
 * *  Neither the name of Texas Instruments Incorporated nor the names of
 *    its contributors may be used to endorse or promote products derived
 *    from this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
 * THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
 * PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
 * CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
 * EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
 * PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
 * OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
 * WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
 * OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
 * EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */
'''
from struct import unpack, pack
import struct
import wave
try:
    from serial import Serial
    from serial import SerialException # pip [--proxy <addr>] install pyserial
except ImportError:
    print("Could not load module pyserial. Please install package. pip [--proxy <addr>] install pyserial.")
    sys.exit(1)
from time import time
import time
import winsound
import os
import sys
import argparse
import textwrap

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

SI_Dec = 0
PV_Dec = 0

def get_script_path():
    return os.path.dirname(os.path.realpath(sys.argv[0]))

def tic1_DecodeSingle(nibble):
    global SI_Dec
    global PV_Dec

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

decoded = []
buf = ''
bytearr = bytearray()

def decode_adpcm(_buf):
    global decoded
    global buf
    global SI_Dec
    global PV_Dec

    buf = _buf

    for b in _buf:
        b,= unpack('B', b)
        decoded.append(pack('h', tic1_DecodeSingle(b & 0xF)))
        decoded.append(pack('h', tic1_DecodeSingle(b >> 4)))

def unpack_pcm(_buf):
    global bytearr
    bytearr += bytearray(_buf)
    #print(bytearr) 

def save_wav():
    global bytearr

    filename = time.strftime("pdm_test_%Y-%m-%d_%H-%M-%S_") + vargs.compression_format

    print("saving file")
    w = wave.open(get_script_path() + "/samples/" + filename + ".wav", "w")
    w.setnchannels(1)
    w.setframerate(16000)
    w.setsampwidth(1)
    #w.writeframes(''.join(decoded))
    
    w.writeframes(bytearr)
    w.close()
    print("...........................DONE...")

    #clear stuff for next stream
    SI_Dec = 0
    PV_Dec = 0
    decoded = []
    missedFrames = 0


if __name__ == "__main__":

    # Argument parsing
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent('''\
           Reads audio data from a SimpleLink LaunchPad via UART and saves
           to a wav file. Audio data may be in PCM format or encoded via ADPCM.
           If encoded, the script will perform ADPCM decode.

           Stores sampled audio data as a wav file in the samples/ folder in the
           same directory as the script.

           The script will idle until data is received. On reception of data
           it will unpack the serial frame and print the sequence number.

           Serial Frames are of the form where NB is a variable length
           specified by the framesize argument:

           [         1B        ][     3B(optional)  ][     NB     ]
           [  Sequence Number  ][  Encoding Header  ][ Audio Data ]

           If the audio data is compressed in ADPCM format, the encoding header
           is of the form:

           [         1B        ][           2B          ]
           [   Step Index (SI) ][  Predicted Value(PV)  ]

           Note that the frame size, baudrate, and compression settings must
           match what the LaunchPad is producing. Changing these options
           requires recompiling the audio image on the LaunchPad.

        '''),
        epilog=textwrap.dedent('''\

            Usage examples:
              %(prog)s COM127 68 NONE -b 460800
                  Read audio data from LaunchPad at port COM127 with frame size
                  68B and no compression.
              %(prog)s COM127 20 ADPCM -b 460800
                  Read audio data from LaunchPad at port COM127 with frame size
                  20B and ADPCM compression
        '''))


    parser.add_argument('port', help="COM port name and number of user/UART port on LaunchPad")
    parser.add_argument('framesize', help="Size of audio frames in bytes", type=int)
    parser.add_argument('compression_format', help='Compression format', choices=['ADPCM','NONE'], default='NONE')
    parser.add_argument('-b', '--baudrate', help='Baud rate of serial data', default=460800, type=int)

    vargs = parser.parse_args()

    indata = ''
    inbuffer = ''
    frameNum = 1

    if vargs.compression_format == 'ADPCM':
        useCompression = True
    else:
        useCompression = False

    if vargs.framesize is not None:
        bufLen = vargs.framesize


    lastByteTime = 0

    prevSeqNum = 0
    missedFrames = 0
    try:
        ser = None
        ser = Serial(vargs.port, vargs.baudrate, timeout=0.1)
        readSoFar = 0

        print ("Audio Reader Started!")
        print ("Reading from {} at {}".format(vargs.port, str(vargs.baudrate)))
        print ("Waiting for data")
        
        count = 0
        doneReading = False
        while True:
            
            indata = ser.read(bufLen - readSoFar)
            readSoFar = len(indata)
            #if not indata and len(decoded):
            #    if time.time() - lastByteTime > 2:
            if doneReading is True:
                    #save wav file
                    save_wav()
                    count =0
                    doneReading = False
            elif indata:
                #print("This is new data")
                word = indata.decode("utf-8")
                list = word.splitlines()
                for s in list: 
                   if s.startswith("20000") and len(s)==8:                
                    #print("----------start of word---------")
                    print(s)
                    unpack_pcm(bytes(s[5:],"utf-8"))
                    #print("----------end of word-----------")
                
                count = count+1
                #print(count)
                if count == 1000:
                   
                   doneReading=True
                 
 
                #inbuffer += indata.decode("utf-8")
                #newstr = (inbuffer.replace("start","").replace("end",""))
                #print(newstr[1])


                #if len(inbuffer) == bufLen:
                #    seqNum, SI_received, PV_received = struct.unpack('BBh', inbuffer[0:4])
                #    print ("Frame sequence number: %d" % seqNum)

                #   if useCompression:
                #        print ("SI local: %d, SI received: %d" % (SI_Dec, SI_received))
                #        print ("PV local: %d, PV received: %d" % (PV_Dec, PV_received))

                #   prevSeqNum = seqNum

                #  if missedFrames > 0:
                #        print ("######################### MISSED #########################")
                #        print (missedFrames)
                #        print ("##########################################################")

                #    if useCompression:
                #        decode_adpcm(inbuffer[4:])
                #    else:
                       
                #unpack_pcm(indata)
                        
                #    inbuffer = ''
                #    readSoFar = 0
                     
                #    lastByteTime = time.time()

    except SerialException as e:
        print ("Serial port error")
        print (e)

    finally:
        if ser is not None: ser.close()
