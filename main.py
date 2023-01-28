import json
import os
from urllib.request import urlopen
import dotenv
from fastapi import FastAPI, Form, HTTPException, Header, Request, Response
import uvicorn
from models.plot_model import PlotModel
from models.story_model import StoryModel
from fastapi.middleware.cors import CORSMiddleware
from jose import JWTError, jwt
from models.user_model import UserViewModel
from services.openai_service import generate_story
from services.story_service import get_user_stories
from services.user_service import create_user, get_user, process_sale

origins = ["*"]
AUTH0_DOMAIN = "coralina.us.auth0.com"
API_AUDIENCE = "https://coralina.us.auth0.com/api/v2/"
ALGORITHMS = ["RS256"]
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "auth.json"


dotenv.load_dotenv()

app = FastAPI()
app_public = FastAPI(openapi_prefix='/public')
app_private = FastAPI(openapi_prefix='/api')

app.mount("/public", app_public)
app.mount("/api", app_private)


@app_private.middleware("http")
async def verify_user_agent(request: Request, call_next):
    try:
        token = request.headers["Authorization"]
        payload = decode_jwt(token)
        response = await call_next(request)
        return response
    except Exception as err:
        return Response(status_code=400)


def decode_jwt(token: str):
    try:
        token = token.split(" ")[1]
        jsonurl = urlopen("https://" + AUTH0_DOMAIN + "/.well-known/jwks.json")
        jwks = json.loads(jsonurl.read())
        unverified_header = jwt.get_unverified_header(token)
        rsa_key = {}
        for key in jwks["keys"]:
            if key["kid"] == unverified_header["kid"]:
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"],
                }
        if rsa_key:
            try:
                payload = jwt.decode(
                    token,
                    rsa_key,
                    algorithms=ALGORITHMS,
                    audience=API_AUDIENCE,
                    issuer="https://" + AUTH0_DOMAIN + "/",
                )
            except jwt.ExpiredSignatureError:
                raise HTTPException(status_code=401, detail="token_expired")
            except jwt.JWTClaimsError:
                raise HTTPException(status_code=404, detail="invalid_claims")

            except Exception:
                raise HTTPException(status_code=401, detail="invalid_header")
        if payload is not None:
            return payload
        raise HTTPException(status_code=401, detail="invalid_header")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=400, detail=e)


@app_private.post("/generate")
async def generate(plot: PlotModel, Authorization=Header(...)) -> StoryModel:
    try:
        token = decode_jwt(Authorization)
        nickname = token["https://coralina.app/nickname"]

        return await generate_story(plot, nickname)
    except Exception as e:
        print(f'Error {e}')
        return HTTPException(status_code=500, detail=e)


@app_private.get("/user/{user_login}")
async def get_get_user(user_login: str, Authorization=Header(...)):
    if authenticated_user(Authorization, user_login):
        return get_user(user_login)


@app_private.get("/stories/{user_login}")
async def get_get_user_stories(user_login: str, Authorization=Header(...)):
    if authenticated_user(Authorization, user_login):
        return get_user_stories(user_login)


@app_private.post("/user")
async def post_create_user(user: UserViewModel, Authorization=Header(...)):
    if authenticated_user(Authorization, user.user_login):
        return create_user(user)


@app_public.post("/sale")
async def post_sale(product_id: str = Form(...), email: str = Form(...), quantity: int = Form(...), ):
    process_sale(email.split("@")[0], product_id, quantity)

def authenticated_user(Authorization, user_login):
    token = decode_jwt(Authorization)
    nickname = token["https://coralina.app/nickname"]
    if nickname == user_login:
        return True

    raise HTTPException(status_code=403, detail="Unauthorized")


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app_private.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app_public.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


if __name__ == '__main__':
    if (os.environ["ENV"] == 'prod'):
        uvicorn.run("main:app",
                    host="0.0.0.0",
                    port=8000,
                    reload=True,
                    ssl_keyfile="privkey.pem",
                    ssl_certfile="cert.pem"
                    )
    else:
        uvicorn.run("main:app",
                    host="0.0.0.0",
                    port=8000,
                    reload=True
                    )
