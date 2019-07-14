#!/usr/bin/env python3

from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
import time, os, sys
import datetime
import logging
import simplejson as json
from pprint import pprint
from tqdm import tqdm
from decimal import Decimal
from lib.rpc_methods import rpc_conn

class BlockPayment:
    def __init__(self):
        self.mn_list = self.get_mn_list()
        self.mn_wallets = self.get_mn_wallets()

    @staticmethod
    def get_mn_list():
        try:
            mn_list = rpc_conn().masternodelist()
        except Exception as e:
            print(e)
            mn_list = []
        
        return mn_list

    def get_mn_wallets(self):
        # wallets should be key/value pair of vin -> payee
        # But right now, it's just a set of addresses to see if it's worth pursuing

        mn_list = self.mn_list
        mn_wallets = set()
        try:
            for node in mn_list:
                mn_wallets.add(mn_list[node]['payee'])
        except:
            pass
        return mn_wallets

    def check_tx(self, txid):
        tx_raw = rpc_conn().getrawtransaction(txid)
        tx_decoded = rpc_conn().decoderawtransaction(tx_raw)
        
        for vout in tx_decoded['vout']:
            node_payee = vout['scriptPubKey']['addresses'][0]
            if node_payee in self.mn_wallets:
                found_node = list(rpc_conn().masternodelist('payee', node_payee).keys())[0]
                pment_dict = {
                    "vin": found_node,
                    "value": vout['value']
                }
                return pment_dict
            else:
                continue

    def process_block(self, block_hash):
        block_info = rpc_conn().getblock(block_hash)
        # pprint(block_info)
        cb_tx = block_info['tx'][0]
        paid_mn = self.check_tx(cb_tx)
        return paid_mn

    def refresh_mn_info(self):
        print("Refreshing MN info")
        self.mn_list = rpc_conn().masternodelist()
        self.mn_wallets = self.get_mn_wallets()
        print("MN info refreshed")

if __name__ == '__main__':
    # test_txid = '3fcc6bdaf487c6ead6b8ae17f42d6ed2dd76d728df991f98d984639d07837f3d'
    bp = BlockPayment()
    latest_block = rpc_conn().getbestblockhash()
    paid_mn = bp.process_block(latest_block)
    print(paid_mn)