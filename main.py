from fastapi import FastAPI
from fastapi.security import HTTPBearer
from fastapi import HTTPException
from fastapi import Depends
from fastapi.responses import HTMLResponse
from bot_database import get_user_by_username,password_hash
from pydantic import BaseModel,Field
import logging
from bot import groq_ai
from dotenv import load_dotenv
load_dotenv()
import os
from pwdlib import PasswordHash
from pwdlib.exceptions import UnknownHashError
from bot_database import save_user,save_assistant
#----------JWT----------------------
import jwt
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

security = HTTPBearer()


app = FastAPI()

@app.get("/", response_class=HTMLResponse)
def read_root():
    if os.path.exists("Frontend.html"):
        with open("Frontend.html", "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Frontend.html not found!</h1>"


logging.basicConfig(filename="logging.log",
                    level=logging.INFO,
                    format= "%(asctime)s|%(levelname)s | %(message)s")

from fastapi.middleware.cors import CORSMiddleware


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
def verify_token(token):
    try:
        payload = jwt.decode(token,
                            JWT_SECRET_KEY,
                           algorithms=["HS256"]
                           )
        return payload

    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401,
                            detail= "invalid token")


#-----------------------------------/Login-----------------------------------------
#-----------------------------------/Login-----------------------------------------
#-----------------------------------/Login-----------------------------------------

class LoginRequest (BaseModel):
    username : str
    password : str

@app.post("/login")
async def login_user (login : LoginRequest):
    username = login.username
    password = login.password
    user = get_user_by_username(username)
    if user is None:
        logging.warning("Login failed")
        raise HTTPException(status_code=401,
                             detail= "Invalid username or password")

    password_user = user[2]
    try:
        password_correct = password_hash.verify(password, password_user)
    except UnknownHashError :
        logging.error("Invalid password hash in database")
        raise HTTPException (status_code=500,
                             detail= "Internal server error X")
        
    if password_correct :
        
        payload =  {
                            "user_id" : user[0],
                            "username" : user[1],
                            "role" :user[3]
                        } 
        
        
        token = jwt.encode(payload , JWT_SECRET_KEY, algorithm="HS256")

        return {"access_token": token,
                "token_type": "Bearer",
                "payload": payload}
    

    else:
        logging.warning("Login failed: invalid password")
        raise HTTPException(status_code=401, detail= "Invalid username or password")
    
    

#-----------------------------------/chat-----------------------------------------
#-----------------------------------/chat-----------------------------------------
#-----------------------------------/chat-----------------------------------------

class requestUser(BaseModel):
    user : str = Field(
        min_length=2,
        max_length=40
        )  

@app.post("/chat")

async def model_groc (
    data: requestUser,
    credentials = Depends(security)
    ):
    verify_token(credentials.credentials)
    fin_user = data.user
    result= await groq_ai(
        fin_user
        )
    return {
        "message": result
        }

