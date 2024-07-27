from typing import List

from pydantic import BaseModel, ConfigDict


class QuizCreate(BaseModel):
    title: str
    description: str
    question_ids: List[int]


class QuizUpdate(BaseModel):
    title: str
    description: str
    question_ids: List[int]


class Quiz(BaseModel):
    id: int
    title: str
    description: str
    question_ids: List[int]
    usage_count: int
    company_id: int

    model_config = ConfigDict(arbitrary_types_allowed=True)
