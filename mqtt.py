import paho.mqtt.client as mqtt
import time
import wave
import json
import tensorflow as tf

audio_src = 0

def save_wav(decoded):
    global audio_src
    bb = bytearray(decoded)
    filename = time.strftime("pdm_test_%Y-%m-%d_%H-%M-%S_adpcm")
    if audio_src =0:
        w = wave.open("AudioRepo/cat1/"+filename + ".wav", "w")   
    elif audio_src =1 
        w = wave.open("AudioRepo/cat2/"+filename + ".wav", "w")
    w.setnchannels(1)
    w.setframerate(16000)
    w.setsampwidth(2)
    w.writeframes(bb)
    w.close()

def on_connect(client,userdata,flags,rc):
     print("Connected with result code " + str(rc))
     client.subscribe("Audio/Sensor1/Start")
     client.subscribe("Audio/Sensor1/Data")
     client.subscribe("Audio/Sensor2/Start")
     client.subscribe("Audio/Sensor2/Data")
     client.subscribe("Manager/#")

def on_message(client,userdata,msg):
    global audio_src
    if "Start" in msg.topic:
        print(msg.payload.decode("utf-8"))
    elif "Data" in msg.topic:
        if "Manager" in msg.topic:
         #Conduct Inference using payload
         recv_dict= json.loads(msg.payload)
         result=classify_audio(recv_dict["filename"])
         print("Sending Results: ",result)
         client.publish("Manager/category1/topic4",json.dumps(result))
        elif "Sensor1" in msg.topic:
         #Save Audio file
         print("Saving Audio File...")
         audio_src =0
         save_wav(msg.payload)
         print("Done Saving!")
        elif "Sensor2" in msg.topic:
         #Save Audio file
         print("Saving Audio File...")
         audio_src =1
         save_wav(msg.payload)
         print("Done Saving!")

def setup(hostname):
 client = mqtt.Client()
 client.on_connect = on_connect
 client.on_message = on_message
 print("Connecting")
 client.connect("localhost",1883,60)
 client.loop_forever()

def main():
    setup("192.168.0.1")
    while True:
        pass
if __name__=="__main__":
    main()
