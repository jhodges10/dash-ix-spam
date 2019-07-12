import binascii
import zmq
import struct
import time

port = 28332

def zmq_tx_consumer():
    zmqContext = zmq.Context()
    zmqSubSocket = zmqContext.socket(zmq.SUB)
    zmqSubSocket.setsockopt_string(zmq.SUBSCRIBE, "hashblock")
    zmqSubSocket.setsockopt_string(zmq.SUBSCRIBE, "hashtx")

    zmqSubSocket.connect("tcp://127.0.0.1:%i" % port)
    
    try:
        while True:
            msg = zmqSubSocket.recv_multipart()
            topic = str(msg[0])
            body = msg[1]
            sequence = "Unknown"
            if len(msg[-1]) == 4:
                msgSequence = struct.unpack('<I', msg[-1])[-1]
                sequence = str(msgSequence)
            if topic == "hashblock":
                print('- HASH BLOCK ('+sequence+') -')
                print(binascii.hexlify(body))
            elif topic == "hashtx":
                print('- HASH TX  ('+sequence+') -')
                print(binascii.hexlify(body))

    except KeyboardInterrupt:
        zmqContext.destroy()

if __name__ == '__main__':
    print("Starting ZMQ Listener...")
    zmq_tx_consumer()