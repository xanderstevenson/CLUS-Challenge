
from typing import Optional
from pydantic import BaseModel
    
class DemoQuestion(BaseModel):
    _id: str
    answer: str
    prompt: Optional[str]
    weight: Optional[int]
    filename: str

class User(BaseModel):
    email: str
    first: str
    last: str
    timetake: Optional[int]

class Car(BaseModel):
    _id: str
    number: int
    ip: str
    position: int = 0
    start: Optional[int]
    userid: Optional[str]
    