from typing import List, Optional
from pydantic import BaseModel


class ParagraphModel(BaseModel):
    text: Optional[str]
    image_url: Optional[str]

class StoryModel(BaseModel):
    paragraphs: Optional[List[ParagraphModel]]

