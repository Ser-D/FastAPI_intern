from typing import List

from pydantic import BaseModel, ConfigDict, Field


class QuestionCreate(BaseModel):
    text: str
    answer_options: List[str] = Field(..., min_items=2, max_items=4)
    correct_answers: List[str] = Field(..., min_items=1)


class QuestionUpdate(BaseModel):
    text: str
    answer_options: List[str] = Field(..., min_items=2, max_items=4)
    correct_answers: List[int] = Field(..., min_items=1)


class Question(BaseModel):
    id: int
    text: str
    answer_options: List[str]
    correct_answers: List[str]
    company_id: int

    model_config = ConfigDict(arbitrary_types_allowed=True)
