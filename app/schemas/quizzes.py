from typing import List

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.questions import QuestionBase


class QuizCreate(BaseModel):
    title: str
    description: str
    question_ids: List[int] = Field(..., min_length=2)
    usage_count: int = 0


class QuizUpdate(BaseModel):
    title: str
    description: str
    question_ids: List[int] = Field(..., min_length=2)
    usage_count: int = 0


class Quiz(BaseModel):
    id: int
    title: str
    description: str
    question_ids: List[int]
    usage_count: int
    company_id: int

    model_config = ConfigDict(from_attributes=True)


class QuizRunResponse(BaseModel):
    selected_answers: List[int]


class QuizWithQuestions(BaseModel):
    id: int
    title: str
    description: str
    questions: List[QuestionBase]

    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)


class QuizResult(BaseModel):
    total_questions: int
    correct_answers: int
    score: float


class QuizResponseRedis(BaseModel):
    selected_answers: List[int]
    is_correct: bool


class QuizImportResponse(BaseModel):
    detail: str
    status_code: int
