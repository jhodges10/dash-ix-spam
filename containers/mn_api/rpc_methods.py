from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
import time, os, sys
from pprint import pprint
from tqdm import tqdm
import json

# rpc_password = "admin"
# rpc_user = "admin"

rpc_user = "dashrpc"
rpc_password = "password"
testnet = False

def rpc_conn(user=rpc_user, password=rpc_password):
    if os.getenv('RPC_IP'):
        rpc_hostname = os.getenv('RPC_IP')
    else:
        rpc_hostname = "dash_server"

    if os.getenv('RPC_PORT'):
        rpc_port = os.getenv('RPC_PORT')
    else:
        rpc_port = 9998

    if testnet == False:
        rpc_conn = AuthServiceProxy(f"http://{rpc_user}:{rpc_password}@{rpc_hostname}:{rpc_port}")
    else:
        rpc_conn = AuthServiceProxy(f"http://{rpc_user}:{rpc_password}@{rpc_ip}:{rpc_port}")

    return rpc_conn

def get_best_block():
    latest_block = rpc_conn().getblockcount()
    return latest_block

def get_proregtx_list():
    info = rpc_conn().protx('list')
    return info

def get_prgtx_info():
    protxlist = get_proregtx_list()

    big_dict = dict()
    for node in tqdm(protxlist):
        node_info = rpc_conn().protx('info', node)

        vin = str(node_info['collateralHash']) + '-' + str(node_info['collateralIndex']) # define vin
        big_dict[vin] = node_info['state']['votingAddress']

    c_write_json(big_dict, 'masternode_info')
    return big_dict

def c_write_json(data, filename):
    cache_dir = ''
    dirname = os.path.dirname(os.path.abspath(__file__))
    absolute_cache_dir = os.path.abspath(os.path.join(dirname, cache_dir))
    filename = filename + '.json'
    absolute_file_path = os.path.abspath(os.path.join(absolute_cache_dir, filename))

    with open(absolute_file_path, 'w') as json_stuff:
        json.dump(data, json_stuff)
    return True


if __name__ == "__main__":
    # pprint(get_prgtx_info())
    pass