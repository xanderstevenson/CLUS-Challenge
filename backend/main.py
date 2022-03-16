
from urllib import response
from fastapi import FastAPI, HTTPException
from fastapi import status as statuscode
from fastapi.staticfiles import StaticFiles
from model import DemoQuestion, User, Car

from database import (
    fetch_one_question,
    fetch_many_questions,
    create_user,
    fetch_user_by_id,
    start_the_challenge,
    fetch_all_cars,
    end_the_challenge,
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

# Added to create path to static files for all question images
app.mount("/static", StaticFiles(directory="data/questions"),name="static")

@app.get("/")
async def hello_world():
    return {"Hello": "World"}

# Maximum number of questions fetch from all questions in the DB, 0 will fetch all.
MAX_NUMBER_OF_QUESTIONS = 5

@app.get("/questions")
async def get_many_questions():
    response = await fetch_many_questions(MAX_NUMBER_OF_QUESTIONS)
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
async def register_a_user(email: str, first: str, last: str):
    response = await create_user(email, first, last)
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


@app.put("/end}",
         response_model=Car,
         description="Signal end of the challenge and cleanup routine")
async def end_challenge(userid: str):
    response = await end_the_challenge(userid)
    if response:
        return response
    raise HTTPException(404, f"Can't signal end of challenge for user {userid}")
         
@app.get('/leaders',
         response_model=User,
         description="Get users who completed challege with time recorded")
async def get_users():
    response = await fetch_leaderboard_users()
    return response