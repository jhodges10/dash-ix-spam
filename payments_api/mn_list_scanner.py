#!/usr/bin/env python3

from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
import time, os, sys
from datetime import datetime
import logging
import simplejson as json
from pprint import pprint
from tqdm import tqdm
from lib.cryptocompare import CryptoCompare
from decimal import Decimal

rpc_password = "admin"
rpc_user = "admin"


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
        
    # return coinbase_tx_count, payments_dict
    return payments_dict

def get_tx_timing(block_hash):
    block_info = rpc_conn().getblock(block_hash)
    return block_info['time']

def get_usd_value(tx_timestamp, dashValue, currency='USD'):
    tx_datetime = datetime.fromtimestamp(tx_timestamp)
    tx_date = tx_datetime.strftime('%Y-%m-%d')
    avg_price = Decimal(CryptoCompare.match_day_to_price(tx_date))
    tx_value_decimal = dashValue * avg_price
    tx_value = str(tx_value_decimal.quantize(Decimal('1.00')))
    return tx_value

def check_tx(txid):
    # TODO IMPROVE THIS AREA
    try:
        tx_info = rpc_conn().gettxout(txid, 0)
    except TypeError:
        tx_info = rpc_conn().gettxout(txid, 1)
    except Exception:
        return None

    clean_tx_info = dict()

    if tx_info['coinbase'] == True:
        tx_info['paymentTimestamp'] = get_tx_timing(tx_info['bestblock'])
        clean_tx_info['paymentTimestamp'] = tx_info['paymentTimestamp'] # Re-assing paymentDate in our new dict
        clean_tx_info['usdValue'] = get_usd_value(tx_info['paymentTimestamp'], tx_info['value'])
        clean_tx_info['paymentAddress'] = tx_info['scriptPubKey']['addresses'][0]
        clean_tx_info['dashValue'] = str(tx_info['value'])

        return clean_tx_info

def process_wallets(masternode_wallets):
    for masternode_vin in tqdm(masternode_wallets):
        print(masternode_vin)
        # masternode_wallets[masternode_vin]['payment_count'], masternode_wallets[masternode_vin]['payments_dict'] = check_address(masternode_wallets[masternode_vin]['payoutAddress'])
        data = check_address(masternode_wallets[masternode_vin]['payoutAddress'])
        print(data)
        masternode_wallets[masternode_vin] = data


    with open('payment_info_v3.json', 'w') as outfile:  
        json.dump(masternode_wallets, outfile)

# This would be set to run every x minutes as a python lambda function, deployed via Terraform
def process_latest_block():
    # Add storage and check for "last block checked" to make sure we don't ever missing blocks
    block_hash = rpc_conn().getbestblockhash()
    block_info = rpc_conn().getblock(block_hash)
    txes = block_info['tx']

    mn_payments = list()
    for tx in txes:
        if check_tx(tx) != None:
            mn_payments.append(check_tx(tx))
        else:
            continue

    pprint(mn_payments)
    return mn_payments


if __name__ == '__main__':
    #pr_list = get_proregtx_list()
    #masternode_wallets = process_proregtx(pr_list)
    #process_wallets(masternode_wallets)
    
    process_latest_block()

    # scan_blocks()
    # check_matching_tx()
    # print(redis_conn.get(29936))