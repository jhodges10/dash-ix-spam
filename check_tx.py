from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
import time, os, sys
import logging

password = "admin"
user = "admin"

locked = 0
unlocked = 0

def rpc_conn(user=user, password=password):
    rpc_conn = AuthServiceProxy("http://%s:%s@localhost:19998" % (user, password))
    return rpc_conn

def check_lock(txid, count=0):
    global locked
    global unlocked
    time.sleep(2)
    txid_response = rpc_conn().gettransaction(str(txid))

    if txid_response['instantlock'] is True:
        locked += 1
        print("Succeeded" + " - #" + str(locked) + " - " + txid_response['txid'])
        with open("locked.txt", "a") as f:
            f.write("Instant tx lock" + " " + str(txid) + "\n")

    else:
        time.sleep(2)

    if txid_response['instantlock'] is True:
        locked += 1
        print("Succeeded" + " - #" + str(locked) + " - " + txid_response['txid'])
        with open("locked.txt", "a") as f:
            f.write("2 Second tx lock" + " " + str(txid) + "\n")

    else:
        time.sleep(4)

    if txid_response['instantlock'] is True:
        locked += 1
        print("Succeeded" + " - #" + str(locked) + " - " + txid_response['txid'])
        with open("locked.txt", "a") as f:
            f.write("4 Second tx lock" + " " + str(txid) + "\n")
    else:
        unlocked += 1
        print("Failed" + " - #" + str(unlocked) + " - " + txid_response['txid'])
        with open("unlocked.txt", "a") as f:
            f.write("Unlocked tx" + " " + str(txid) + "\n")

    return True

