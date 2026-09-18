from groq import Groq,APIConnectionError,RateLimitError,AuthenticationError,APITimeoutError,InternalServerError,AsyncGroq
from fastapi import FastAPI, HTTPException
import os
from bot_database import create_db,save_user,save_assistant
import logging
from dotenv import load_dotenv
create_db()
load_dotenv()


api_key = os.getenv("GROQ_API_KEY")
if api_key:
    client = AsyncGroq(api_key=api_key)
else:
    logging.error("GROQ_API_KEY is not configured")
    raise RuntimeError ("GROQ_API_KEY is not configured")

async def groq_ai (fin_user):
    
    
    #save_user(user_id,fin_user)

    try:
        
        response = await client.chat.completions.create(
                model= "openai/gpt-oss-120b",
                messages= [
                    {"role" : "system", "content": """You are the AI assistant of "Chat آلنايض".

At the start of every new conversation, say:
"مرحباً بك في شات آلنايض 👋"

Then give one short, inspiring hacker quote. After that, answer the user normally and helpfully.
"""},
                    {"role": "user", "content": fin_user}
                ],timeout=30
            )
    except APITimeoutError :
        logging.error("APITimeoutError")
        raise HTTPException(
            status_code= 504,
            detail="Groq API took too long to respond" 
                            )
    
    except RateLimitError :
        logging.error("RateLimitError")
        raise HTTPException (
            status_code=429,
            detail= "Too many requests. Please Try again later"
        )

    except AuthenticationError :
        logging.error("AuthenticationError")
        raise HTTPException (
            status_code= 401,
            detail= "Échec de l'authentification. Vérifiez vos identifiants et réessayez."
        )
       
    except APIConnectionError:
        logging.error("APIConnectionError")
        raise HTTPException (
            status_code= 503,
             detail= "Connection error. Please try again later."
        )
        
    except InternalServerError:
        logging.error("InternalServerError")
        raise HTTPException (
            status_code=503,
            detail= "Groq server is currently unavailable. Please try again later."
        )
        
    except Exception :
        logging.exception("Unexpected error")
        raise HTTPException (
            status_code=500,
            detail="Une erreur inattendue s'est produite."
        )

    result = response.choices[0].message.content
    save_assistant(result)

    return  result
    