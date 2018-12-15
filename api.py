import falcon, os, json, random, base64, time, mimetypes, sys, traceback, re
import logging
from schema import Schema, And, Use, Optional, SchemaError
from datetime import datetime, timedelta
from pprint import pprint
from middleware import CorsMiddleware, JSONTranslator, RequireJSON
import pymongo
from datetime import datetime
from bson.objectid import ObjectId
import ssl
from pprint import pprint
from bson import json_util
from dateutil.relativedelta import relativedelta

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_SCHEME = os.environ['DB_SCHEME'] if 'DB_SCHEME' in os.environ else None
DB_USER = os.environ['DB_USER'] if 'DB_USER' in os.environ else None
DB_PASS = os.environ['DB_PASS'] if 'DB_PASS' in os.environ else None
DB_HOST = os.environ['DB_HOST'] if 'DB_HOST' in os.environ else None
DB_NAME = os.environ['DB_NAME'] if 'DB_NAME' in os.environ else None
DB_ARGS = os.environ['DB_ARGS'] if 'DB_ARGS' in os.environ else None

db_client = pymongo.MongoClient(f"{DB_SCHEME}://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}?{DB_ARGS}") #, ssl_cert_reqs=ssl.CERT_NONE)
db = db_client.get_default_database()

def check_schema(conf_schema, conf):
  try:
    conf_schema.validate(conf)
    return True
  except SchemaError:
    return False

class JSONEncoder(json.JSONEncoder):
  def default(self, o):
    if isinstance(o, ObjectId):
      return str(o)
    elif isinstance(o, datetime):
      return o.isoformat()+"Z"
    return json.JSONEncoder.default(self, o)

class PollsResource(object):
  @staticmethod
  def get_document(_id):
    return db.polls.find_one({'_id': ObjectId(_id)})

  def on_get(self, req, resp):
    results = {}
    resp.status = falcon.HTTP_200
    req.context['result'] = results

  def on_post(self, req, resp):
    req_data = req.context['data']

    conf_schema = Schema({
      'name': And(Use(str))
    })

    if not check_schema(conf_schema, req_data):
      resp.status = falcon.HTTP_400
      raise falcon.HTTPBadRequest('Invalid keys')

    req_data['created_date'] = datetime.utcnow()
    req_data['status'] = "unpublished"
    req_data['candidates'] = []

    _id = db.polls.insert_one(req_data).inserted_id
    document = PollsResource.get_document(_id)
    document["id"] = document.pop("_id")

    resp.status = falcon.HTTP_201
    req.context['result'] = json.loads(json.dumps(document, cls=JSONEncoder))


class VotesResource(object):
  def on_get(self, req, resp):
    results = {}
    resp.status = falcon.HTTP_200
    req.context['result'] = results

class ResultsResource(object):
  def on_get(self, req, resp):
    results = {}
    resp.status = falcon.HTTP_200
    req.context['result'] = results

# class GraphGoalGroupsResource(object):
#   def on_get(self, req, resp, goal_group_id):
#     results = {'date': [], 'goal': [], 'actual': []}
#     previous_actual = 0
#     for doc in db_client.budget.goals.find({'goal_group_id': ObjectId(goal_group_id), "user_id": ObjectId("5b622d9b43156f6dc8bc8781")}, ["date","expected_value","expected_value","actual_value"], sort=[('date', pymongo.ASCENDING)]):
#       results['date'].append(doc['date'].strftime("%Y-%m-%d"))
#       results['goal'].append(doc['expected_value'])
#       if 'actual_value' in doc:
#         previous_actual = doc['actual_value']
#         results['actual'].append(doc['actual_value'])
#       else:
#         results['actual'].append(previous_actual)
#     resp.status = falcon.HTTP_200
#     req.context['result'] = results

# class ExpendituresByDayResource(object):
#   def on_get(self, req, resp):
#     results = {'date': [], 'value': [], 'average': []}
#     previous_actual = 0
#     current_month = ""
#     month_count = 0
#     month_total = 0 
#     for doc in db_client.budget.transactions.aggregate([{'$match': {'description': re.compile(r'^((?!TRANSFER).)*$'), 'amount': {'$lt': 0}, 'date': {'$gt': datetime.today()-timedelta(days=500)}}}, {'$project': {'date': {'$substr': ['$date', 0, 10]}, 'amount': '$amount'}}, {'$group': {'_id': '$date', 'total': {'$sum': '$amount'}}}, {'$sort': {'_id': 1}}]):
#       results['date'].append(str(doc['_id']))
#       results['value'].append(doc['total']*-1)
#       if str(doc['_id'])[0:7] != current_month:
#         current_month = str(doc['_id'])[0:7]
#         if month_count >= 1:
#           for i in range(month_count):
#             results['average'].append(month_total/30)
#         month_count = 1
#         month_total = doc['total']*-1
#       else:
#         month_count += 1
#         month_total += (doc['total']*-1)
#     resp.status = falcon.HTTP_200
#     req.context['result'] = results

# class BudgetsResource(object):
#   def on_get(self, req, resp):
#     results = []
#     for doc in db_client.budget.budgets.find({"user_id": ObjectId("5b622d9b43156f6dc8bc8781")}, sort=[('name', pymongo.ASCENDING)]):
#       results.append({"id": str(doc['_id']), 'name': doc['name']})
#     resp.status = falcon.HTTP_200
#     req.context['result'] = results
#
# class BudgetResource(object):
#   def on_get(self, req, resp, budget_id):
#     doc = db_client.budget.budgets.find_one({'_id': ObjectId(budget_id), "user_id": ObjectId("5b622d9b43156f6dc8bc8781")})
#     result = {"id": str(doc['_id']), 'name': doc['name']}
#     resp.status = falcon.HTTP_200
#     req.context['result'] = result
#
# class BudgetBucketsResource(object):
#   def on_get(self, req, resp, budget_id):
#     results = []
#     # Get Date from query string
#     # TODO: Check budget_id access
#     buckets = list(db_client.budget.buckets.find({"budget_id": ObjectId(budget_id)}, sort=[('type', pymongo.ASCENDING), ('name', pymongo.ASCENDING)]))
#     for bucket in buckets:
#       # Get balance of backup
#       balance = 0
#       if bucket['carry_over'] == True:
#         transactions = list(db_client.budget.transactions.find({'allocation.bucket_id': bucket['_id']}))
#         for transaction in transactions:
#           for allocation in transaction['allocation']:
#             if allocation['bucket_id'] == bucket['_id']:
#               balance += allocation['amount']
#       else:
#         # TODO: FINISH THIS
#         start_time = datetime.utcnow().replace(microsecond=0, second=0, minute=0, hour=0, day=1)
#         end_time = start_time + relativedelta(months=1)
#         transactions = list(db_client.budget.transactions.find({'allocation.bucket_id': bucket['_id'], 'date': {'$gte': start_time, '$lt': end_time}}))
#         #transactions = list(db.transactions.find({'allocation.bucket_id': bucket['_id']}))
#         for transaction in transactions:
#           for allocation in transaction['allocation']:
#             if allocation['bucket_id'] == bucket['_id']:
#               #pprint(allocation)
#               balance += allocation['amount']

#       results.append({"id": str(bucket['_id']), 'name': bucket['name'], 'amount': bucket['amount'], 'carry_over': bucket['carry_over'], 'type': bucket['type'], 'balance': balance, 'warning_balance': bucket['warning_balance'], 'critical_balance': bucket['critical_balance']})
#     resp.status = falcon.HTTP_200
#     req.context['result'] = results
# 
# class TransactionsResource(object):
#   def on_get(self, req, resp):
#     results = []
#     # TODO : This should probably be replaced with transactions for an account/budget
#     for doc in db_client.budget.transactions.find({'allocation.bucket_id': {'$exists': False},'allocation.amount': {'$exists': False}, 'ignore': {'$exists': False}}, sort=[('date', pymongo.ASCENDING)]):
#       results.append({"id": str(doc['_id']), 'date': str(doc['date']), 'amount': doc['amount'],'description': doc['description']})
#     resp.status = falcon.HTTP_200
#     req.context['result'] = results

# class TransactionResource(object):
#   def on_patch(self, req, resp, transaction_id):
#     req_data = req.context['data']
#     # TODO: prevent injections
#     allocation = []
#     for rec in req_data['allocation']:
#       pprint(rec)
#       allocation.append({'bucket_id': ObjectId(rec['bucket_id']), 'amount': rec['amount']})
#     db_client.budget.transactions.update_one({'_id': ObjectId(transaction_id)}, {'$set': {'allocation': allocation}})
#     result = {}
#     doc = db_client.budget.transactions.find_one({'_id': ObjectId(transaction_id)})
#     if 'allocation' in doc:
#       result = {"id": str(doc['_id']), 'date': str(doc['date']), 'amount': doc['amount'],'description': doc['description'], 'allocation': [{'bucket_id': str(alloc['bucket_id']), 'amount': alloc['amount']} for alloc in doc['allocation']]}
#     else:
#       result = {"id": str(doc['_id']), 'date': str(doc['date']), 'amount': doc['amount'],'description': doc['description']}
#     resp.status = falcon.HTTP_200
#     req.context['result'] = json.loads(json.dumps(result,default=json_util.default))

# Setup routes
api = falcon.API(middleware=[RequireJSON(), JSONTranslator(), CorsMiddleware()])
api.add_route('/api/polls', PollsResource())
api.add_route('/api/polls/{poll_id}', PollsResource())
api.add_route('/api/polls/{poll_id}/votes', VotesResource())
api.add_route('/api/polls/{poll_id}/votes/{vote_id}', VotesResource())
api.add_route('/api/polls/{poll_id}/results', ResultsResource())

