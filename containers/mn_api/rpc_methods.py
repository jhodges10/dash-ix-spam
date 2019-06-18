from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
import time, os, sys
from pprint import pprint
from pandas import DataFrame
from pandas.io.json import json_normalize
from tqdm import tqdm
from db_conn import Database
import json

# rpc_password = "admin"
# rpc_user = "admin"

rpc_user = "dashrpc"
rpc_password = "password"
testnet = True

def rpc_conn(user=rpc_user, password=rpc_password):
    if os.getenv('RPC_IP'):
        rpc_hostname = os.getenv('RPC_IP')
    else:
        # rpc_hostname = "dash_server"
        rpc_hostname = 'localhost'
    if os.getenv('RPC_PORT'):
        rpc_port = os.getenv('RPC_PORT')
    else:
        # rpc_port = 9998
        rpc_port = 19998

    if testnet == False:
        rpc_conn = AuthServiceProxy(f"http://{rpc_user}:{rpc_password}@{rpc_hostname}:{rpc_port}")
    else:
        rpc_conn = AuthServiceProxy(f"http://{rpc_user}:{rpc_password}@{rpc_hostname}:{rpc_port}")

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
    protx_list = list()
    for node in tqdm(protxlist):
        node_info = rpc_conn().protx('info', node)

        # vin = str(node_info['collateralHash']) + '-' + str(node_info['collateralIndex']) # define vin
        # big_dict[vin] = node_info['state']['votingAddress']

        protx_list.append(node_info)

    # write_json(big_dict, 'masternode_info')
    return protx_list

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
    # pprint(get_prgtx_info())
    # prgtx_data = get_prgtx_info()
    # Database.insert_protx_info(prgtx_data)
    get_mn_csv()
    pass