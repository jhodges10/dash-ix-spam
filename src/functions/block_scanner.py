#!/usr/bin/env python3

from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
import time, os, sys
import logging
import simplejson as json
from threading import Thread
from redis import Redis
from rq import Queue
from pprint import pprint
from tqdm import tqdm

print("Intitializing Redis...")

try:
    redis_conn = Redis('localhost', 6379)
    print("Connection Made")
except:
    print("Failed to connect to Redis")

rpc_password = "admin"
rpc_user = "admin"

tx_count = 0
rate = 0
locked = 0
unlocked = 0
coinbase_tx_count = 0

def rpc_conn(user=rpc_user, password=rpc_password):
    rpc_conn = AuthServiceProxy("http://%s:%s@localhost:19998" % (user, password))
    return rpc_conn

def parse_tx(block_hash, block_number, input_tx_list):
    global coinbase_tx_count
    for tx in input_tx_list:
        tx1_info = rpc_conn().gettxout(tx, 0)
        print(tx1_info)
        # tx2_info = rpc_conn().gettxout(tx, 1)
        if tx1_info is not None:
            tx1_info['txid'] = tx
            tx1_info['block_number'] = block_number
            redis_conn.set(block_number, json.dumps(tx1_info))
            coinbase_tx_count += 1
        else:
            pass
    
    time.sleep(1)
    return True

def scan_blocks():
    latest_block = rpc_conn().getblockcount() # Get highest block

    # Try to resume where we left off
    try:
        cur_block = json.loads(redis_conn.get('current_block'))['scan_info']
        print(cur_block)
    except Exception as e:
        print(e)
        cur_block = 0
    
    # Loop over all blocks and load information
    while cur_block <= latest_block:
        print("TX info for block {}".format(cur_block))
        try:
            block_hash = rpc_conn().getblockhash(cur_block)
            block_info = rpc_conn().getblock(str(block_hash))
            # pprint(block_info)
            parse_tx(block_hash, cur_block, block_info['tx'])
        except JSONRPCException as e:
            print("Crashed because of {}".format(e))
            sys.exit(1) 
        cur_block += 1
        redis_conn.set('current_block', json.dumps({'scan_info': cur_block}))

    global coinbase_tx_count
    print(coinbase_tx_count)

def check_matching_tx(address='yd5KMREs3GLMe6mTJYr3YrH1juwNwrFCfB'):
    matching_tx = list()
    for block in range(29935, rpc_conn().getblockcount()):
        try:
            coinbase_data = json.loads(redis_conn.get(block))
            if address in coinbase_data['scriptPubKey']['addresses']:
                matching_tx.append(coinbase_data['value'])
            else:
                pass
            print("Got a good one")
        except Exception as e:
            print(e)
            # No coinbase tx in that block
            pass
        print("Block number: {}".format(block))

        time.sleep(10)

    print(matching_tx)

def get_proregtx_list():
    info = rpc_conn().protx('list')
    return info

def process_proregtx(protxlist):
    payment_wallets = dict()
    for node in protxlist:
        node_info = rpc_conn().protx('info', node)
        if node_info['state']['PoSePenalty'] == 0:
            vin = str(node_info['collateralHash']) + '-' + str(node_info['collateralIndex']) # define vin
            # print(vin)
            payment_wallets[vin] = {
                'payoutAddress': node_info['state']['payoutAddress'],
                'ownerAddress': node_info['state']['ownerAddress'],
                'operatorReward': node_info['operatorReward']
            }
        else:
            # print("Skipping because it's not a valid node")
            pass
    print(f"{len(payment_wallets)} Masternode wallets to be checked.")

    return payment_wallets

def check_address(wallet_address):
    # print(wallet_address)
    tx_list = rpc_conn().getaddresstxids({"addresses": [wallet_address]})
    coinbase_tx_count = 0
    payments_dict = dict()
    for tx in tx_list:
        coinbase_tx, tx_info = check_tx(tx)
        if coinbase_tx is True:
            # pprint(tx_info)
            payments_dict[tx] = tx_info
            # This is where we'll pull out the datetime and the payment amount
            coinbase_tx_count += 1
        else:
            continue
        
    return coinbase_tx_count, payments_dict

def get_tx_timing(block_hash):
    block_info = rpc_conn().getblock(block_hash)
    return block_info['time']

def check_tx(txid):
    try:
        tx_info = rpc_conn().gettxout(txid, 0)
    except TypeError:
        tx_info = rpc_conn().gettxout(txid, 1)

    if tx_info is None:
        coinbase = False
        tx_info = None
        return coinbase, tx_info

    else:
        if tx_info['coinbase'] == True:
            coinbase = True
        else:
            coinbase = False

        tx_info['datetime'] = get_tx_timing(tx_info['bestblock'])

        return coinbase, tx_info

def check_mn_wallets(payment_wallets):
    for masternode in tqdm(payment_wallets):
        payment_wallets[masternode]['payment_count'], payment_wallets[masternode]['payments_dict'] = check_address(payment_wallets[masternode]['payoutAddress'])
    
    with open('payment_info.json', 'w') as outfile:  
        json.dump(payment_wallets, outfile)

if __name__ == '__main__':
    pr_list = get_proregtx_list()
    masternode_wallets = process_proregtx(pr_list)
    check_mn_wallets(masternode_wallets)
    # scan_blocks()
    # check_matching_tx()
    # print(redis_conn.get(29936))