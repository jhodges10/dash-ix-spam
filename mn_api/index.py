from flask import Flask
from flask_restplus import Resource, Api
from rpc_methods import *
import optparse
import json

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
        data = get_best_block()
        return {"best_block": data}

if __name__ == "__main__":
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