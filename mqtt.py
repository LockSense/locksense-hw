import paho.mqtt.client as mqtt
import time
import wave
import json
import tensorflow as tf

def save_wav(decoded):
    bb = bytearray(decoded)
    filename = time.strftime("pdm_test_%Y-%m-%d_%H-%M-%S_adpcm")
    w = wave.open("mqtt_samples/"+filename + ".wav", "w")
    w.setnchannels(1)
    w.setframerate(16000)
    w.setsampwidth(2)
    w.writeframes(bb)
    w.close()


session = tf.compat.v1.Session(graph = tf.compat.v1.Graph())
#initialize = tf.compat.v1.global_variables_initializer()
model = None
classes = ["daisy","dandelion","roses","sunflowers","tulips"]



def model_loader():
    global model
    if model == None: 
        model = load_model(MODEL_NAME)
    return model



def classify_audio(filename,image):
    with session.graph.as_default():
         print("*******start classifying")
         set_session(session)
         print("*******loading model")
         model = model_loader()
         print("*******model loaded")
         result = model.predict(image)
         themax = np.argmax(result)   
    #return {predType:audPred/imgPred, fileName:fileName, prediction:0/1/2}

def on_connect(client,userdata,flags,rc):
     print("Connected with result code " + str(rc))
     client.subscribe("Audio/Sensor1/Start")
     client.subscribe("Audio/Sensor1/Data")
     client.subscribe("Manager/#")

def on_message(client,userdata,msg):
    if "Start" in msg.topic:
        print(msg.payload.decode("utf-8"))
    elif "Data" in msg.topic:
        if "Manager" in msg.topic:
         #Conduct Inference using payload
         recv_dict= json.loads(msg.payload)
         result=classify_audio(recv_dict["filename"])
         print("Sending Results: ",result)
         client.publish("Manager/category1/topic4",json.dumps(result))
        else:
         #Save Audio file
         print("Saving Audio File...")
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
