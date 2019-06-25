from rpc_methods import get_prgtx_info, get_best_block
from pprint import pprint
from collections import OrderedDict

"""
Sort the set in ascending order by "testHeight" and “ProRegTx hash”. 
“testHeight” is determined for each individual entry and equals the “last paid height” (or “registered height” if the masternode was never paid).
If the masternode was PoSe-banned before and revived later, the “revival height” of the masternode is used instead of the “registered height”. 
If the “testHeight” of two masternodes is identical, the ProRegTx hash acts as a deterministic tie breaker.
"""

def get_payment_ranks():

    proregtx_info_list = get_prgtx_info()
    node_count = len(proregtx_info_list)
    cur_block = get_best_block()

    node_dict = dict()
    testHeight = 0

    for node in proregtx_info_list:
        vin = f"{node['collateralHash']}-{node['collateralIndex']}"
        lastpaid_height = node['state']['lastPaidHeight']
        revived_height = node['state']['PoSeRevivedHeight']
        registered_height = node['state']['registeredHeight']

        if lastpaid_height > abs(revived_height):
            testHeight = lastpaid_height
        elif 0 <= lastpaid_height < revived_height:
            testHeight = revived_height
        else:
            testHeight = registered_height

        payment_distance = testHeight - cur_block
        rank = payment_distance / node_count

        node_dict[vin] = rank

    sorted_set = OrderedDict(sorted(node_dict.items(), key=lambda x: x[1], reverse=True))

    # pprint(sorted_set)
    print(f"{len(sorted_set)} nodes found in the sorted set, out of a total of {node_count}.")
    print(f"The next node to be paid is: {sorted_set.popitem()}")
    return sorted_set

if __name__ == "__main__":
    get_payment_ranks()
