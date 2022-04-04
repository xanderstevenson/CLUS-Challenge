import re
from fastapi import Request
from fastapi import FastAPI, HTTPException
from fastapi import status as statuscode
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from model import DemoQuestion, User, Car
import httpx
import pandas as pd
import asyncio
import json

from database import (
    get_environment_vars,
    fetch_one_question,
    fetch_many_questions,
    create_user,
    fetch_user_by_id,
    start_the_challenge,
    fetch_all_cars,
    end_the_challenge,
    fetch_leaderboard_users,
    get_car_payload,
    send_car_to_start_position,
)

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

environment_vars = get_environment_vars()

# Added to create path to static files for all question images
app.mount("/static", StaticFiles(directory="data/questions"),name="static")

@app.get("/")
async def hello_world():
    envs = get_environment_vars()
    return { 'Car simulation:' : envs['car_simulation'] }

@app.get("/questions")
async def get_many_questions():
    response = await fetch_many_questions()
    return response

@app.get("/question/{id}}", response_model=DemoQuestion)
async def get_question_by_id(id):
    response = await fetch_one_question(id)
    if response:
        return response
    raise HTTPException(404, f"There is no question with number {id}")

@app.post("/user",
          description="Create a new user",
          status_code=statuscode.HTTP_201_CREATED
          )
async def register_a_user(user: User):
    print(user)
    response = await create_user(user)
    if( response == {} ):
        raise HTTPException(403, f"user with email {user.email} may already exists in DB")
    return response

@app.get("/user/{userid}", 
         description="Query a user by user id",
         response_model=User)
async def get_user(userid: str):
    response = await fetch_user_by_id(userid)
    return response

@app.get("/cars")
async def get_all_cars():
    response = await fetch_all_cars()
    return response

@app.put("/start",
         response_model=Car,
         description="Signal start the challenge and return first car available for this userid")
async def start_challenge(userid: str):
    response = await start_the_challenge(userid)
    if( response ):
        return response
    raise HTTPException(404, f"Can't signal start of challenge for user {userid}")

@app.put("/end",
         response_model=Car,
         description="Signal end of the challenge and cleanup routine")
async def end_challenge(userid: str):
    response = await end_the_challenge(userid)
    if response:
        current_position = response['position']
        car_id = response['number']
        print('end_challenge: current position=',current_position,' car# ',car_id)
        if( current_position > 0):
            weight = -1 * current_position
            (car_url,payload) = await get_car_payload('',car_id,weight)
            if (payload is not None):
                print(f'Send cmd to car {car_url} with payload {payload}')
                if( environment_vars['car_simulation'] is not True):
                    data = json.loads(payload)
                    async with httpx.AsyncClient() as client:
                        resp = await client.post(car_url,json=data)
                        if resp:
                            print('Sending POST to car with status code = ',resp.status_code)
                        else:
                            raise HTTPException(404, f"Can't send command to reset to starting position for user {userid}")       
        return response
    raise HTTPException(404, f"Can't signal end of challenge for user {userid}")

@app.put("/score",
        description="Actions taken after user answer a question correctly or incorrectly")
async def score_a_question(user_id: str, weight: int):
    ''' If user answers the question correctly, send weight as positive number
        otherwise, send weight as negative number.
    ''' 
    (car_url,payload) = await get_car_payload(user_id,0,weight)
    if (payload is not None):
        print(f'Send cmd to car {car_url} with payload {payload}')
        data = json.loads(payload)
        async with httpx.AsyncClient() as client:
            if( environment_vars['car_simulation'] is not True):
                response = await client.post(car_url,json=data)
                print('Sending POST to car with status code = ',response.status_code)
                if response:
                    return response.status_code
                else:
                    raise HTTPException(404, f"Can't send command to car for user {user_id}")
    return 200
        
@app.put("/reset/{carid}",
        description="Reset car position and make it avaialble for grab (if user quit mid-race)")
async def reset_car(carid: int):
    current_position = await send_car_to_start_position(carid)
    print('Current car position is ',current_position)
    if current_position > 0:
        weight = -1 * current_position
        (car_url,payload) = await get_car_payload('',carid,weight)
        if (payload is not None):
            print(f'Send cmd to car {car_url} with payload {payload}')
            if( environment_vars['car_simulation'] is not True):
                data = json.loads(payload)
                async with httpx.AsyncClient() as client:
                    response = await client.post(car_url,json=data)
                    print('Sending POST to car with status code = ',response.status_code)
                    if response:
                        return response.status_code
                    else:
                        raise HTTPException(404, f"Can't send command to reset car#{carid} to starting position")
        return 200
    return 200

# Migrate code from Leaderboard project here for now. This should be done in ReactJS as a
# frontend component.        
templates = Jinja2Templates(directory="data")
app.mount("/template", StaticFiles(directory="data"),name="template")
    
@app.get('/leaders',
         description="Get users who completed challege with time recorded")
async def get_users(request: Request):
    response = await fetch_leaderboard_users()
    response.sort(key=lambda x: x.timetaken)
    users_dict = []
    for x in response: 
        if x.timetaken > 0:
            users_dict.append(x.__dict__)
    df = pd.DataFrame(users_dict)
    return templates.TemplateResponse('leaders.html', context={'request': request, 'data': df.to_html()})