from typing import List

from pydantic import BaseModel, ConfigDict, Field


class QuestionCreate(BaseModel):
    text: str
    answer_options: List[str] = Field(..., min_length=2, max_length=4)
    correct_answers: List[str] = Field(..., min_length=1)


class QuestionUpdate(BaseModel):
    text: str
    answer_options: List[str] = Field(..., min_length=2, max_length=4)
    correct_answers: List[int] = Field(..., min_length=1)


class QuestionBase(BaseModel):
    id: int
    text: str
    answer_options: List[str]
    correct_answers: List[str]

    model_config = ConfigDict(arbitrary_types_allowed=True)


class Question(BaseModel):
    id: int
    text: str
    answer_options: List[str]
    correct_answers: List[str]
    company_id: int

    model_config = ConfigDict(arbitrary_types_allowed=True)
