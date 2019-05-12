#!/usr/bin/env python3

from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
import time, os, sys
from datetime import datetime
import logging
import simplejson as json
from pprint import pprint
from tqdm import tqdm
from cryptocompare import CryptoCompare
from decimal import Decimal

rpc_password = "admin"
rpc_user = "admin"

coinbase_tx_count = 0

def rpc_conn(user=rpc_user, password=rpc_password):
    rpc_conn = AuthServiceProxy("http://%s:%s@localhost:19998" % (user, password))
    return rpc_conn
        
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

def get_tx_value(tx_timestamp, dash_amt, currency='USD'):
    tx_datetime = datetime.fromtimestamp(tx_timestamp)
    tx_date = tx_datetime.strftime('%Y-%m-%d')
    avg_price = Decimal(CryptoCompare.match_day_to_price(tx_date))
    tx_value_decimal = dash_amt * avg_price
    tx_value = tx_value_decimal.quantize(Decimal('1.00'))
    return tx_value

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
        tx_info['usd_value'] = get_tx_value(tx_info['datetime'], tx_info['value'])

        return coinbase, tx_info

def check_mn_wallets(payment_wallets):
    for masternode in tqdm(payment_wallets):
        payment_wallets[masternode]['payment_count'], payment_wallets[masternode]['payments_dict'] = check_address(payment_wallets[masternode]['payoutAddress'])
    
    with open('payment_info_v2.json', 'w') as outfile:  
        json.dump(payment_wallets, outfile)

if __name__ == '__main__':
    pr_list = get_proregtx_list()
    masternode_wallets = process_proregtx(pr_list)
    check_mn_wallets(masternode_wallets)
    # scan_blocks()
    # check_matching_tx()
    # print(redis_conn.get(29936))