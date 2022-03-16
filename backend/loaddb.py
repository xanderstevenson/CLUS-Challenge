# Preload DemoQuestion DB with all questions from the questions directory
# This will overwrite DB and start out with a fresh, initial DB

from pymongo import MongoClient
import os, json

DB_CONNECT_URL = os.getenv('DATABASE_URL')
LOCAL_FILE_URL_PREFIX = 'http://localhost:8000/static/'

client = MongoClient(DB_CONNECT_URL)
database = client.DemoQuestion 

# Read all meta data for data models
META = './data/meta.json'
with open(META) as f:
    data = json.load(f)
    
# Loading Questions Database 
print ('Loading questions database...')
collection = database.question
for i in data['questions']:
    i['filename'] = LOCAL_FILE_URL_PREFIX + i['filename']
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