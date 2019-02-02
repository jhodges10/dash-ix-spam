from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
import time, os, sys
import logging
from threading import Thread
from redis import Redis
from rq import Queue
from check_tx import check_lock

print("Starting IX Spam Program")

print("Intitializing Redis Queue")

redis_conn = Redis('localhost', 6379)
print("Connection Made")

try:
    q = Queue(connection=redis_conn)

except:
    print("No Redis connection possible, exiting...")
    sys.exit(1)

password = "admin"
user = "admin"

tx_count = 0
rate = 0
locked = 0
unlocked = 0

def rpc_conn(user=user, password=password):
    rpc_conn = AuthServiceProxy("http://%s:%s@localhost:19998" % (user, password))
    return rpc_conn

def run_spam():
    global tx_count
    tx_count = 1
    timeLast = time.time()

    expectedRate = float(input("What rate would you like to spam at?"))
    global rate
    rate = 0
    if expectedRate == 0: sleep = 0
    else: sleep = 1/expectedRate
    while True:
        timeLast = time.time()
        time.sleep(sleep)

        address = rpc_conn().getnewaddress()
        
        try:
            txid = rpc_conn().instantsendtoaddress(address, 0.002)
            job = q.enqueue(check_lock, txid, tx_count)
            #_thread.start_new_thread(check_lock, (tx_count, txid))
            timeNow = time.time()
            rate = 1 / (timeNow - timeLast)
            if rate < expectedRate * .98 and not expectedRate == 0:
                sleep = sleep * rate / expectedRate
            elif rate > expectedRate * 1.02 and not expectedRate == 0:
                sleep = sleep * rate / expectedRate
            # print(round(1 / (timeNow - timeLast), 2), tx_count, txid)

        except JSONRPCException as e:
            print("Crashed because of {}".format(e))
            sys.exit(1)

        tx_count += 1
                
        # Add new print line because pretty
        # print("\n")

        # Wait 5 seconds before restarting loop


def get_addr():		
    while True:
        address = rpc_conn().getnewaddress()

def post_output():
    global rate, tx_count
    old = tx_count
    while True:
        if not old == tx_count:
            old = tx_count
            print(round(rate, 2), tx_count)
        time.sleep(2)

if __name__ == '__main__':
    try:
        t = Thread(target=post_output, args=())
        t.start()
        
        run_spam()
        t.join()
        # get_addr()

    except Exception and KeyboardInterrupt and SystemExit as errtxt:
        t.join
        print(errtxt)
        time.sleep(5)
