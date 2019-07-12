#!/usr/bin/env python3

from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
import time, os, sys
import datetime
import logging
import simplejson as json
from pprint import pprint
from tqdm import tqdm
from decimal import Decimal
from rpc_methods import rpc_conn, get_proregtx_list

def get_mn_wallets():
    # wallets should be key/value pair of vin -> payee
    # But right now, it's just a set of addresses to see if it's worth pursuing

    mn_list = rpc_conn().masternodelist()
    mn_wallets = set()

    for node in mn_list:
        mn_wallets.add(mn_list[node]['payee'])

    return mn_wallets

def check_tx(txid, mn_wallet_list):
    tx_raw = rpc_conn().getrawtransaction(txid)
    tx_decoded = rpc_conn().decoderawtransaction(tx_raw)
    
    for vout in tx_decoded['vout']:
        node_payee = vout['scriptPubKey']['addresses'][0]
        if node_payee in mn_wallet_list:
            print("Found a payment to a masternode wallet")
            found_node = list(rpc_conn().masternodelist('payee', node_payee).keys())[0]
            return found_node
        else:
            print("Don't do a thing")
            continue

def process_block(block_hash):
    block_info = rpc_conn().getblock(block_hash)
    # pprint(block_info)
    cb_tx = block_info['tx'][0]
    return cb_tx


if __name__ == '__main__':
    # test_txid = '3fcc6bdaf487c6ead6b8ae17f42d6ed2dd76d728df991f98d984639d07837f3d'
    mn_wallet_list = get_mn_wallets()
    latest_block = rpc_conn().getbestblockhash()
    cb_tx = process_block(latest_block)
    print(check_tx(cb_tx, mn_wallet_list))
