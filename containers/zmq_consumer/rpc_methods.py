from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
import time, os, sys
from pprint import pprint
from pandas import DataFrame
from pandas.io.json import json_normalize
from tqdm import tqdm
import json


def rpc_conn():
    rpc_hostname = os.getenv('RPC_HOSTNAME', default='localhost')        
    rpc_port = os.getenv('RPC_PORT', default=19998)
    rpc_user = os.getenv('RPC_USER', default='dashrpc')
    rpc_pass = os.getenv('RPC_PASSWORD', default='password')
    
    rpc_conn = AuthServiceProxy(f"http://{rpc_user}:{rpc_pass}@{rpc_hostname}:{rpc_port}")

    return rpc_conn

def get_best_block():
    latest_block = rpc_conn().getblockcount()
    return latest_block

def get_proregtx_list():
    info = rpc_conn().protx('list', 'valid')
    return info

def get_prgtx_info():
    protxlist = get_proregtx_list()
    big_dict = dict()
    protx_list = list()
    for node in tqdm(protxlist):
        node_info = rpc_conn().protx('info', node)

        # vin = str(node_info['collateralHash']) + '-' + str(node_info['collateralIndex']) # define vin
        # big_dict[vin] = node_info['state']['votingAddress']
        protx_list.append(node_info)

    return protx_list

def get_prgtx_json():
    protxlist = get_proregtx_list()
    big_dict = dict()
    protx_list = list()
    for node in tqdm(protxlist):
        node_info = rpc_conn().protx('info', node)

        # vin = str(node_info['collateralHash']) + '-' + str(node_info['collateralIndex']) # define vin
        # big_dict[vin] = node_info['state']['votingAddress']

        big_dict[node] = node_info
    
    print(type(big_dict))

    return big_dict

def get_mn_csv():
    mn_list = list()
    mn_dict = rpc_conn().masternodelist()

    for node in mn_dict:
        new_dict = dict()
        new_dict = mn_dict[node]
        new_dict['masternodevin'] = node
        mn_list.append(new_dict)
    
    mn_df = DataFrame.from_records(mn_list)
    
    return mn_df.to_csv(index=False)

def write_json(data, filename):
    cache_dir = ''
    dirname = os.path.dirname(os.path.abspath(__file__))
    absolute_cache_dir = os.path.abspath(os.path.join(dirname, cache_dir))
    filename = filename + '.json'
    absolute_file_path = os.path.abspath(os.path.join(absolute_cache_dir, filename))

    with open(absolute_file_path, 'w') as json_stuff:
        json.dump(data, json_stuff)
    return True


if __name__ == "__main__":
    pass
