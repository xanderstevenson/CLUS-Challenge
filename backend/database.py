import motor.motor_asyncio
import os, random, json
from model import DemoQuestion, User, Car
from utils import get_time, get_uuid, get_meta

# Read environment variables from meta file
meta = get_meta()
environments_vars = meta['env'][0]
DB_CONNECT_URL              = environments_vars['database_url']
DB_NAME                     = environments_vars['database_name']
MAX_QUESTIONS_TO_GENERATE   = environments_vars['questions_to_generate']
CAR_SIMULATION              = environments_vars['car_simulation']
CAR_URL_TEMPLATE            = environments_vars['car_url_template']

try:
    print('Connecting to MongoDB...')
    client = motor.motor_asyncio.AsyncIOMotorClient(DB_CONNECT_URL)
    client.server_info() # will throw an exception
except:
    print(f'Cannot connect DB with {DB_CONNECT_URL}')
    exit()
    
database = client[DB_NAME]

def get_environment_vars():
    return environments_vars

async def fetch_one_question(qnumber: str):
    collection = database.question
    document = await collection.find_one({"_id": qnumber})
    return document

async def fetch_many_questions(maxQuestions=MAX_QUESTIONS_TO_GENERATE):
    # Only return maxQuestions from the database in random order
    questions = []
    # Fetch all questions from DB
    collection = database.question
    cursor = collection.find({})
    async for document in cursor:
        questions.append(DemoQuestion(**document))
    # Generate a random list of maxQuestions questions from all questions in DB
    totalQuestions = len(questions)
    if (maxQuestions > 0):
        randomlist = random.sample(range(0, totalQuestions), maxQuestions )
    else:
        randomlist = random.sample(range(0, totalQuestions), totalQuestions)
    new_questions = list(map(questions.__getitem__, randomlist))

    return new_questions

# Create and register new user in DB, record startTime and return car id assigned to this user
async def create_user(user):
    collection = database.user
    print('Creating DB user ',user)
    user_in_db = await collection.find_one({"email": user.email.lower()})
    if( user_in_db ):
        print(f'User with email={user.email} already exists in database')
        print(type(user_in_db))
        if( ('timetaken' in user_in_db) and (user_in_db['timetaken'] > 0) ):  # Don't allow user on leaderboard to retake the challenge
            return {}
        else:
            print('User already registered but have not taken or completed challenge, permission to take challenge granted',user_in_db['_id'])
            return { "id": user_in_db['_id'] }
    user_id = get_uuid()
    document = { "_id": user_id, "email": user.email.lower(), "first": user.first, "last": user.last }
    result = await collection.insert_one(document)
    return { "id" :user_id }

async def fetch_user_by_id(userid: str):
    collection = database.user
    document = await collection.find_one({"_id": userid})
    return document

async def fetch_all_cars():
    cars = []
    collection = database.car
    cursor = collection.find({})
    async for document in cursor:
        cars.append(Car(**document))
    return cars
    
async def start_the_challenge(userid: str):
    collection = database.car
    filter = { 'start': None }
    epoch = get_time()
    car = await collection.find_one(filter) # Find first available
    if( car ):
        print(f'car #{car["number"]} is assigned to user:{userid}')
        await collection.update_one(filter, {"$set": {"userid": userid,"start": epoch,"position": 0}})
        car = await collection.find_one({'number' : car['number']})
    return car

async def update_user_time(userid: str, timetaken: int):
    collection = database.user
    filter = {'_id': userid }
    document = collection.find(filter)
    if( document ):
        await collection.update_one(filter, {"$set": {"timetaken": timetaken}})
        return 1
    return 0

async def end_the_challenge(userid: str):
    collection = database.car
    filter = { 'userid': userid }
    epoch = get_time()
    # User has completed the challenge -> clear car data, record user time
    document = await collection.find_one(filter)
    if( document ):
        timetaken = epoch - document['start']
        car_number = document['number']
        # Record time taken for user
        await update_user_time(userid, timetaken)
        # Clear car data, return car to available pool
        [document.pop(key) for key in { "_id","userid", "start"}]
        await collection.replace_one(filter,document)
        document = await collection.find_one({'number': car_number})                                         
    return document

async def send_car_to_start_position(car_number: int) -> int:
    collection = database.car
    filter = { 'number': car_number }
    # Admin request to reset car record in DB and send it to starting position
    document = await collection.find_one(filter)
    current_position = 0
    if( document ):
        current_position = document['position']
        if( ("userid" in document) and (document['position'] > 0)):
            print('Sending car to starting position')                                        
        # remove _id and optional fields before replace
        for key in { '_id','userid', 'start' }:  
            if key in document:
                document.pop(key)
        await collection.replace_one(filter,document)
        #document = await collection.find_one(filter)                                         
    return current_position

async def fetch_leaderboard_users():
    collection = database.user
    users= []
    cursor = collection.find({})
    async for document in cursor:
        users.append(User(**document))
    return users

# Car URL template


async def get_car_payload(user_id: str,car_id: int,weight: int):
    ''' Get car payload by user_id or car_id
    '''
    collection = database.car
    filter = {'number':car_id} if (car_id != 0) else {'userid':user_id}
    print(f'filter {filter} weight {weight}')
    car_url = None
    payload = None
    document = await collection.find_one(filter)
    if document:
        car_url = CAR_URL_TEMPLATE % document['ip']
        direction = 'forward' if (weight > 0) else 'backward'
        if( weight+document['position'] < 0 ):
            weight += document['position']
        if( (document['position'] == 0) and (weight < 0) ):
            payload= None
        else:
            payload = '{"speed": %s,"weight": %s, "direction": "%s"}' % (document['speed'], abs(weight), direction)
            new_position = document['position'] + weight
            await collection.update_one(filter, {"$set": {"position": new_position}})

    return (car_url,payload)
        