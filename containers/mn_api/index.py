from flask import Flask
from flask_restplus import Resource, Api
from rpc_methods import *
from insight import check_insight_block_count
import optparse
import json
import socket

app = Flask(__name__)
api = Api(app)

@api.route('/mn_vkeys')
class VotingKeyAddresss(Resource):
    def get(self):
        print("Fetching voting keys")
        data = get_prgtx_info()
        return data

@api.route('/status')
class NodeStatus(Resource):
    def get(self):
        print("Fetching node status")
        cur_block = get_best_block()
        highest_block = check_insight_block_count()
        return {"sync_progress": f"{cur_block}/{highest_block}"}

if __name__ == "__main__":
    print(socket.gethostname())

    parser = optparse.OptionParser(usage="python index.py -p ")
    parser.add_option('-p', '--port', action='store', dest='port', help='The port to listen on.')
    (args, _) = parser.parse_args()
    if args.port == None:
        print("Missing required argument: -p/--port")
        # sys.exit(1)
        port=5000
        app.run(host='0.0.0.0', port=port, debug=False)
    else:
        app.run(host='0.0.0.0', port=int(args.port), debug=False)