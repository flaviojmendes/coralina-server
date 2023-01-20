import os
import dotenv
from fastapi import FastAPI
import uvicorn
from models.plot_model import PlotModel
from models.story_model import StoryModel
from fastapi.middleware.cors import CORSMiddleware

from services.openai_service import generate_story
dotenv.load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/generate")
async def generate(plot: PlotModel) -> StoryModel:
    return await generate_story(plot)

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
