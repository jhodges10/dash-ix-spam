from flask import Flask
from flask import make_response
from flask_restplus import Resource, Api
from lib.rpc_methods import *
from lib.insight import check_insight_block_count
from celery import Celery
import optparse
import simplejson as json
import socket

app = Flask(__name__)
app = Api(app)
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

# TODO implement celery
# https://github.com/miguelgrinberg/flask-celery-example/blob/master/app.py
# https://blog.miguelgrinberg.com/post/using-celery-with-flask


@app.route('/mn_vkeys')
class VotingKeyAddresss(Resource):
    def get(self):
        print("Fetching voting keys")
        data = get_prgtx_info()
        return data

"""
@app.route('/protx_list')
class ProtxList(Resource):
    def get(self):
        print("Fetching Protx info")
        data = Database.get_protx_info()
        for row in data:
            print(row.keys())
        return data
"""

@app.route('/status')
class NodeStatus(Resource):
    def get(self):
        print("Fetching node status")
        cur_block = get_best_block()
        highest_block = check_insight_block_count()
        return {"sync_progress": f"{cur_block}/{highest_block}"}


@app.route('/mn_csv')
class MasternodeCSV(Resource):
    def get(self):
        print("Fetching masternode list as CSV")
        output = make_response(get_mn_csv())
        output.headers["Content-Disposition"] = "attachment; filename=export.csv"
        output.headers["Content-type"] = "text/csv"
        return output

@app.route('/mn_json')
class MasternodeJSON(Resource):
    def get(self):
        print("Fetching masternode list as JSON")
        mn_info = get_prgtx_json()
        output = make_response(json.dumps(mn_info, use_decimal=True))
        output.headers["Content-type"] = "application/json"
        return output


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