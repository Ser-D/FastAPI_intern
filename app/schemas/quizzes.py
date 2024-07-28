from typing import List

from pydantic import BaseModel, Field

from app.schemas.questions import QuestionBase


class QuizCreate(BaseModel):
    title: str
    description: str
    question_ids: List[int] = Field(..., min_items=2)
    usage_count: int = 0


class QuizUpdate(BaseModel):
    title: str
    description: str
    question_ids: List[int] = Field(..., min_items=2)
    usage_count: int = 0


class Quiz(BaseModel):
    id: int
    title: str
    description: str
    question_ids: List[int]
    usage_count: int
    company_id: int

    class Config:
        arbitrary_types_allowed = True


class QuizRunResponse(BaseModel):
    selected_answers: List[int]


class QuizWithQuestions(BaseModel):
    id: int
    title: str
    description: str
    questions: List[QuestionBase]

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True


class QuizResult(BaseModel):
    total_questions: int
    correct_answers: int
    score: float


class QuizResponseRedis(BaseModel):
    selected_answers: List[int]
    is_correct: bool
