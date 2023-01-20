import dotenv
from fastapi import FastAPI
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