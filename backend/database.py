import motor.motor_asyncio
import os, random
from model import DemoQuestion, User, Car
from utils import get_time, get_uuid

# export DATABASE_URL = 'mongodb://devnet:ciscopsdt@10.194.239.243:27017/'
DB_CONNECT_URL = os.getenv('DATABASE_URL')
client = motor.motor_asyncio.AsyncIOMotorClient(DB_CONNECT_URL)
database = client.DemoQuestion

async def fetch_one_question(qnumber: str):
    collection = database.question
    document = await collection.find_one({"_id": qnumber})
    return document

async def fetch_many_questions(maxQuestions):
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
async def create_user(email: str, first: str, last: str) -> User:
    collection = database.user
    user_in_db = await collection.find_one({"email": email.lower()})
    if( user_in_db ):
        print(f'User with email={email} already exists in database')
        return {}
    user_id = get_uuid()
    document = { "_id": user_id, "email": email.lower(), "first": first, "last": last }
    result = await collection.insert_one(document)
    return { "_id": user_id }

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
        await collection.update_one(filter, {"$set": {"userid": userid,"start": epoch}})
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
        document['position'] = 0
        # Record time taken for user
        await update_user_time(userid, timetaken)
        # Clear car data, return car to available pool
        [document.pop(key) for key in { "_id","userid", "start"}]
        await collection.replace_one(filter,document)
        document = await collection.find_one({'number': car_number})                                         
    return document

async def fetch_leaderboard_users():
    collection = database.user
    users= []
    cursor = collection.find({})
    async for document in cursor:
        users.append(User(**document))
    return users

async def get_car_payload(user_id: str,weight: int):
    collection = database.car
    filter = { 'userid': user_id }
    document = await collection.find_one(filter)
    car_url = None
    payload = None
    if document:
        current_position = document['position']
        new_position = current_position + weight
        car_url = 'http://%s' % document['ip']
        print(f'current = {current_position}, new = {new_position}')
        if ( new_position >= 0 ):   # Don't want car to fall off cliff
            direction = 'forward' if (weight > 0) else 'backward'
            payload = '{"speed": %s,"weight": %s, "direction": "%s"}' % (document['speed'], abs(weight), direction)
            await collection.update_one(filter, {"$set": {"position": new_position}})

    return (car_url,payload)
        