

from typing import Optional
from pydantic import BaseModel


class PlotModel(BaseModel):
    main_character: Optional[str]
    supporting_characters: Optional[str]
    villain: Optional[str]
    details: Optional[str]
    theme: Optional[str]