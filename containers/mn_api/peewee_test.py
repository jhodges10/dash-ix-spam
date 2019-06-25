import datetime
import os

from flask import Flask
from flask import g
from flask import redirect
from flask import request
from flask import url_for, abort, render_template, flash, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
from functools import wraps
from peewee import *
from lib.rpc_methods import *
from lib.payment_rank import *
from lib.mn_list_scanner import *

# config - aside from our database, the rest is for use by Flask
DATABASE = 'tweepee.db'
PG_DATABASE = os.getenv('POSTGRES_URI')
DEBUG = True

# create a flask application - this ``app`` object will be used to handle
# inbound requests, routing them to the proper 'view' functions, etc
app = Flask(__name__)
app.config.from_object(__name__)

# create a peewee database instance -- our models will use this database to
# persist information
database = SqliteDatabase(DATABASE)
# database = PostgresqlDatabase(PG_DATABASE)

# model definitions -- the standard "pattern" is to define a base model class
# that specifies which database to use.  then, any subclasses will automatically
# use the correct storage. for more information, see:
# http://charlesleifer.com/docs/peewee/peewee/models.html#model-api-smells-like-django
class BaseModel(Model):
    class Meta:
        database = database


# the user model specifies its fields (or columns) declaratively, like django
class Masternode(BaseModel):
    protx_hash = CharField(unique=True)
    collateralhash = CharField()
    collateralindex = CharField()
    collateraladdress = CharField()
    operatorreward = CharField()
    service = CharField()
    registeredheight = BigIntegerField()
    lastpaidheight = BigIntegerField()
    posepenalty = CharField()
    poserevivedheight = BigIntegerField()
    posebanheight = BigIntegerField()
    revocationreason = CharField()
    owneraddress = CharField()
    votingaddress = CharField()
    payoutaddress = CharField()
    pubkeyoperator = CharField()
    confirmations = BigIntegerField()
    date_added = DateTimeField(default=datetime.datetime.now)
    date_modified = DateTimeField(default=datetime.datetime.now)
    payment_rank = CharField(null=True)

    @property
    def serialize(self):
        data = {
            'protx_hash': self.protx_hash,
            'collateralHash': self.collateralhash,
            'collateralIndex': self.collateralindex,
            'collateralAddress': self.collateraladdress,
            'operatorReward': self.operatorreward,
            'service': self.service,
            'registeredHeight': self.registeredheight,
            'lastPaidHeight': self.lastpaidheight,
            'PoSePenalty': self.posepenalty,
            'PoSeRevivedHeight': self.poserevivedheight,
            'PoSeBanHeight': self.posebanheight,
            'revocationReason': self.revocationreason,
            'ownerAddress': self.owneraddress,
            'votingAddress': self.votingaddress,
            'payoutAddress': self.payoutaddress,
            'pubKeyOperator': self.pubkeyoperator,
            'confirmations': self.confirmations,
            'date_added': self.date_added,
            'date_modified': self.date_modified,
            'payment_rank': self.payment_rank,
        }
        return data


    @property
    def rank(self):
        data = {
            'payment_rank': self.payment_rank,
        }
        return data


    def __repr__(self):
        return "{}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}".format(
            self.protx_hash,
            self.collateralhash,
            self.collateralindex,
            self.collateraladdress,
            self.operatorreward,
            self.service,
            self.registeredheight,
            self.lastpaidheight,
            self.posepenalty,
            self.poserevivedheight,
            self.posebanheight,
            self.revocationreason,
            self.owneraddress,
            self.votingaddress,
            self.payoutaddress,
            self.pubkeyoperator,
            self.confirmations,
            self.date_added,
            self.date_modified,
            self.payment_rank,
        )


# the user model specifies its fields (or columns) declaratively, like django
class Payment(BaseModel):
    masternode_vin = CharField()
    payment_timestamp = DateTimeField()
    dash_value = CharField()
    usd_value = CharField()
    date_added = DateTimeField(default=datetime.datetime.now)
    date_modified = DateTimeField(default=datetime.datetime.now)

    @property
    def serialize(self):
        data = {
            'masternode_vin': self.masternode_vin,
            'payment_timestamp': self.payment_timestamp,
            'dash_value': self.dash_value,
            'usd_value': self.usd_value,
            'date_added': self.date_added,
            'date_modified': self.date_modified,
        }
        return data

    def __repr__(self):
        return "{}, {}, {}, {}, {}".format(
            self.masternode_vin,
            self.payment_timestamp,
            self.dash_value,
            self.usd_value,
            self.date_added,
        )

# simple utility function to create tables
def create_tables():
    with database:
        database.create_tables([Masternode], safe=True)

def update_masternode_list():
    nodes = get_prgtx_json()
    for node in nodes:
        cur_node = nodes[node]
        Masternode.insert(
            protx_hash=cur_node['proTxHash'],
            collateralhash=cur_node['collateralHash'],
            collateralindex=cur_node['collateralIndex'],
            collateraladdress=cur_node['collateralAddress'],
            operatorreward=cur_node['operatorReward'],
            service=cur_node['state']['service'],
            registeredheight=cur_node['state']['registeredHeight'],
            lastpaidheight=cur_node['state']['lastPaidHeight'],
            posepenalty=cur_node['state']['PoSePenalty'],
            poserevivedheight=cur_node['state']['PoSeRevivedHeight'],
            posebanheight=cur_node['state']['PoSeBanHeight'],
            revocationreason=cur_node['state']['revocationReason'],
            owneraddress=cur_node['state']['ownerAddress'],
            votingaddress=cur_node['state']['votingAddress'],
            payoutaddress=cur_node['state']['payoutAddress'],
            pubkeyoperator=cur_node['state']['pubKeyOperator'],
            confirmations=cur_node['confirmations'],
        ).on_conflict_replace().execute()

@database.atomic()
def update_payment_rank():
    nodes = get_payment_ranks()
    for node in nodes:
        collateral_hash, collateral_index = node.split('-')
        payment_rank = nodes[node]
        Masternode.update(
            payment_rank=payment_rank
        ).where((Masternode.collateralhash == collateral_hash) & (Masternode.collateralindex == collateral_index)).execute()

# Request handlers -- these two hooks are provided by flask and we will use them
# to create and tear down a database connection on each request.
@app.before_request
def before_request():
    g.db = database
    g.db.connect()

@app.after_request
def after_request(response):
    g.db.close()
    return response

@app.route('/api/v1/list', methods=['GET'])
def masternode_endpoint(page=1):
    # get reque/st
    if request.method == 'GET':
        per_page = 500
        query = Masternode.select().order_by(Masternode.payment_rank.desc()).paginate(page, per_page)
        data = [i.serialize for i in query]

        if data:
            res = jsonify({
                'masternodes': data,
                'meta': {
                   'page': page,
                   'per_page': per_page,
                   'page_url': request.url}
                })
            res.status_code = 200
        else:
            # if no results are found.
            output = {
                "error": "No results found. Check url again",
                "url": request.url,
            }
            res = jsonify(output)
            res.status_code = 404
        return res

@app.route('/api/v1/payments/<string:masternode_vin>', methods=['GET'])
def payments_endpoint(masternode_vin, page=1):
    # get reque/st
    if request.method == 'GET':
        per_page = 100
        query = Payment.select().where(Payment.masternode_vin == masternode_vin).order_by(Payment.payment_timestamp).paginate(page, per_page)
        data = [i.serialize for i in query]

        if data:
            res = jsonify({
                'masternodes': data,
                'meta': {
                   'page': page,
                   'per_page': per_page,
                   'page_url': request.url}
                })
            res.status_code = 200
        else:
            # if no results are found.
            output = {
                "error": "No results found. Check url again",
                "url": request.url,
            }
            res = jsonify(output)
            res.status_code = 404
        return res

@app.route('/api/v1/rank/<string:masternode_vin>', methods=['GET'])
def rank_endpoint(masternode_vin):
    print(masternode_vin)
    # get reque/st
    if request.method == 'GET':
        collateral_hash, collateral_index = masternode_vin.split('-') 
        query = Masternode.select(Masternode.payment_rank).where((Masternode.collateralhash == collateral_hash) & (Masternode.collateralindex == collateral_index)).execute()
        data = [i.rank for i in query]

        if data:
            res = jsonify(data[0])
            res.status_code = 200
        else:
            # if no results are found.
            output = {
                "error": "No results found. Check url again",
                "url": request.url,
            }
            res = jsonify(output)
            res.status_code = 404
        return res



# allow running from the command line
if __name__ == '__main__':
    create_tables()

    # update_masternode_list()
    scheduler = BackgroundScheduler()
    job = scheduler.add_job(update_masternode_list, 'interval', minutes=2)
    job = scheduler.add_job(update_payment_rank, 'interval', minutes=1)
    scheduler.start()

    # update_masternode_list()

    # Run app
    app.run()