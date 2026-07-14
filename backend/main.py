from fastapi import FastAPI
#this imports first api class

app = FastAPI()
#this creates your backend application


@app.get("/")#This creates an API endpoint.
def home(): #Defines the function that runs when / is requested.
    return {
        "message": "Medical AI Assistant Backend Running 🚀"
    }

#uvicorn main:app --reload---starts asgi server,open main.py app and finds app variable 
# and restart automaically whenever code changes