import binascii
import asyncio
import zmq
import zmq.asyncio
import signal
import struct
import sys
import os
from lib.send_to_graphql import add_payment
from lib.block_based_mn_payments import BlockPayment

if not (sys.version_info.major >= 3 and sys.version_info.minor >= 4):
    print("This example only works with Python 3.4 and greater")
    exit(1)

port = 28332

class ZMQHandler():
    def __init__(self):
        self.bp = BlockPayment()
        self.loop = asyncio.get_event_loop()
        self.zmqContext = zmq.asyncio.Context()
        self.zmqSubSocket = self.zmqContext.socket(zmq.SUB)
        self.zmqSubSocket.setsockopt_string(zmq.SUBSCRIBE, "hashblock")
        self.zmqSubSocket.setsockopt_string(zmq.SUBSCRIBE, "hashgovernancevote")
        self.zmqSubSocket.setsockopt_string(zmq.SUBSCRIBE, "hashgovernanceobject")
        print(os.getenv('RPC_HOSTNAME', default='127.0.0.1'))
        self.zmqSubSocket.connect(f"tcp://{os.getenv('RPC_HOSTNAME', default='127.0.0.1')}:{port}")

    @asyncio.coroutine
    def handle(self) :
        msg = yield from self.zmqSubSocket.recv_multipart()
        topic = msg[0]
        body = msg[1]
        sequence = "Unknown"
        if len(msg[-1]) == 4:
          msgSequence = struct.unpack('<I', msg[-1])[-1]
          sequence = str(msgSequence)
        if topic == b"hashblock":
            # Print this for debugging
            print('- HASH BLOCK ('+sequence+') -')
            print(binascii.hexlify(body).decode("utf-8"))

            # Update masternode list and wallets, then process the block for mn payments
            latest_block = binascii.hexlify(body).decode("utf-8")
            self.bp.refresh_mn_info() # We have to make sure we update the masternode wallets list each block
            paid_mn = self.bp.process_block(latest_block)

            # Send the information we get back to the database
            print(f"Submitting payment to database for: {paid_mn}")
            
        elif topic == b"hashgovernancevote":
            print('- HASH GOVERNANCE VOTE ('+sequence+') -')
            print(binascii.hexlify(body).decode("utf-8"))
        elif topic == b"hashgovernanceobject":
            print('- HASH GOVERNANCE OBJECT ('+sequence+') -')
            print(binascii.hexlify(body).decode("utf-8"))
        asyncio.ensure_future(self.handle()) # schedule ourselves to receive the next message

    def start(self):
        self.loop.add_signal_handler(signal.SIGINT, self.stop)
        self.loop.create_task(self.handle())
        self.loop.run_forever()

    def stop(self):
        self.loop.stop()
        self.zmqContext.destroy()

daemon = ZMQHandler()
daemon.start()