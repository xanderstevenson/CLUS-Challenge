# Preload DemoQuestion DB with all questions from the questions directory
# This will overwrite DB and start out with a fresh, initial DB

from pymongo import MongoClient
import os, json

LOCAL_FILE_URL_PREFIX = 'http://localhost:8000/static/'

# Read all meta data for data models
META = './data/meta.json'
with open(META) as f:
    data = json.load(f)

environments_vars = data['env'][0]
DB_CONNECT_URL              = environments_vars['database_url']
DB_NAME                     = environments_vars['database_name']

try:
    print('Connecting to MongoDB...')
    client = MongoClient(DB_CONNECT_URL)
    client.server_info() # will throw an exception
except:
    print(f'Cannot connect with {DB_CONNECT_URL}')
    exit()
 
database = client[DB_NAME]

# Loading Questions Database 
print ('Loading questions database...')
collection = database.question
for i in data['questions']:
    filter = { '_id':i['_id'] }
    if( collection.find_one(filter) ):       # If exists then update/replace with new values
        print(f'updating -> Question#{i["_id"]}...')
        key = i.pop('_id')
        collection.replace_one( {'_id':key}, i )
    else:
        print(f'inserting -> Question#{i["_id"]} with image {i["filename"]}')
        collection.insert_one(i)

# Loading Race Cars Database
print ('Loading race cars database...')
collection = database.car
for i in data['cars']:
    filter = {"number":i['number']}
    if( collection.find_one(filter) ):
        print(f'updating race car #{i["number"]}')
        collection.replace_one( filter, i )
    else:
        print(f'inserting race car#{i["number"]} with IP={i["ip"]}')
        collection.insert_one(i)