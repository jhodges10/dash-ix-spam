from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
import time, os, sys
from pprint import pprint
from tqdm import tqdm
import json

# rpc_password = "admin"
# rpc_user = "admin"

rpc_user = "jeff"
rpc_password = "jeff"
testnet = False

def rpc_conn(user=rpc_user, password=rpc_password):
    user = "jeff"
    password = "F-1N4iKTbQ3lnL6x-am1FMdIRYPPcvodBW2BPwarHM4="
    
    print(sys.platform)

    if os.getenv('RPC_IP'):
        rpc_ip = os.getenv('RPC_IP')
    elif sys.platform == 'darwin':
        # print(sys.platform)
        # rpc_ip = "127.0.0.1"
        rpc_ip = "localhost"
        # rpc_ip = "157.230.74.15" # testing ip
    else:
        # Running in docker by docker-compose start, connect via hostname
        rpc_ip = "dash_node"
    
    print(rpc_ip)
    print("http://%s:%s@%s:9998" % (user, password, rpc_ip))

    if testnet == False:
        try:
            rpc_conn = AuthServiceProxy("http://%s:%s@%s:9998" % (user, password, rpc_ip))
        except:
            rpc_conn = AuthServiceProxy("http://%s:%s@%s:9998" % (user, password, 'localhost'))
    else:
        rpc_conn = AuthServiceProxy("http://%s:%s@%s:19998" % (user, password, 'localhost'))

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