from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from model import load_model, load_encoder
from pydantic import BaseModel
import pandas as pd

class Person(BaseModel):
    age: int
    job: str
    marital: str
    education: str
    balance: int
    housing: str
    duration: int
    campaign: int

app = FastAPI()

bearer = HTTPBearer()

def get_username_for_token(token):
    if token == "abc123":
        return "pedro1"
    return ""

ml_models = {}

@app.on_event("startup")
async def startup_event():
    ml_models["ohe"] = load_encoder()
    ml_models["models"] = load_model()

@app.get("/")
async def root():
    """
    Route to check that API is alive!
    """
    return "Model API is alive!"

async def validate_token(credentials: HTTPAuthorizationCredentials = Depends(bearer)):
    token = credentials.credentials

    username = get_username_for_token(token)
    if username == "":
        raise HTTPException(status_code=401, detail="Invalid token")

    return {"username": username}

@app.post("/predict")
async def predict(person: Person, 
                  user=Depends(validate_token)
                 ):
    """
    Route to make predictions!
    """
    # Load the models
    ohe = ml_models["ohe"]
    model = ml_models["models"]

    df_person = pd.DataFrame([person.dict()])

    person_t = ohe.transform(df_person)
    pred = model.predict(person_t)[0]

    return {
            "prediction": str(pred),
            "username": user["username"]
            }